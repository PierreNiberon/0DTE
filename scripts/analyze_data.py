import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SPXOptionsAnalyzer:
    def __init__(self, csv_path='dataset/processed/spx_0dte_combined.csv'):
        """Initialize the analyzer with the combined dataset"""
        print("Loading SPX 0DTE options data...")
        self.df = pd.read_csv(csv_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['lastTradeDate'] = pd.to_datetime(self.df['lastTradeDate'])
        
        # Calculate additional metrics
        self.df['moneyness'] = (self.df['strike'] - self.df['spx_close']) / self.df['spx_close']
        self.df['days_to_expiry'] = 0  # 0DTE options
        self.df['bid_ask_spread'] = self.df['ask'] - self.df['bid']
        self.df['mid_price'] = (self.df['bid'] + self.df['ask']) / 2
        
        print(f"Loaded {len(self.df):,} options records")
        print(f"Date range: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
    
    def basic_statistics(self):
        """Generate basic statistics about the dataset"""
        print("\n=== BASIC STATISTICS ===")
        print(f"Total records: {len(self.df):,}")
        print(f"Unique trading dates: {self.df['date'].nunique()}")
        print(f"Call options: {len(self.df[self.df['option_type'] == 'call']):,}")
        print(f"Put options: {len(self.df[self.df['option_type'] == 'put']):,}")
        
        print(f"\nSPX Statistics:")
        print(f"  Average close: ${self.df['spx_close'].mean():.2f}")
        print(f"  Range: ${self.df['spx_close'].min():.2f} - ${self.df['spx_close'].max():.2f}")
        print(f"  Volatility: {self.df['spx_close'].std():.2f}")
        
        print(f"\nVIX Statistics:")
        print(f"  Average: {self.df['vix_close'].mean():.2f}")
        print(f"  Range: {self.df['vix_close'].min():.2f} - {self.df['vix_close'].max():.2f}")
        
        print(f"\nVolume Statistics:")
        print(f"  Total volume: {self.df['volume'].sum():,.0f}")
        print(f"  Average daily volume per option: {self.df['volume'].mean():.0f}")
        print(f"  Max single option volume: {self.df['volume'].max():,.0f}")
    
    def create_visualizations(self):
        """Create comprehensive visualizations of the dataset"""
        plt.style.use('default')
        fig = plt.figure(figsize=(20, 24))
        
        # 1. SPX and VIX time series
        ax1 = plt.subplot(4, 3, 1)
        daily_data = self.df.groupby('date').agg({
            'spx_close': 'first',
            'vix_close': 'first'
        }).reset_index()
        
        ax1.plot(daily_data['date'], daily_data['spx_close'], 'b-', linewidth=2, label='SPX')
        ax1.set_ylabel('SPX Price', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.set_title('SPX Price Over Time', fontweight='bold')
        
        ax1_twin = ax1.twinx()
        ax1_twin.plot(daily_data['date'], daily_data['vix_close'], 'r-', linewidth=2, label='VIX')
        ax1_twin.set_ylabel('VIX', color='r')
        ax1_twin.tick_params(axis='y', labelcolor='r')
        
        # 2. Volume distribution by option type
        ax2 = plt.subplot(4, 3, 2)
        volume_by_type = self.df.groupby('option_type')['volume'].sum()
        ax2.pie(volume_by_type.values, labels=volume_by_type.index, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Total Volume by Option Type', fontweight='bold')
        
        # 3. Implied Volatility distribution
        ax3 = plt.subplot(4, 3, 3)
        ax3.hist(self.df[self.df['option_type'] == 'call']['impliedVolatility'], alpha=0.5, bins=50, label='Calls', density=True)
        ax3.hist(self.df[self.df['option_type'] == 'put']['impliedVolatility'], alpha=0.5, bins=50, label='Puts', density=True)
        ax3.set_xlabel('Implied Volatility')
        ax3.set_ylabel('Density')
        ax3.set_title('Implied Volatility Distribution', fontweight='bold')
        ax3.legend()
        
        # 4. Moneyness vs IV scatter
        ax4 = plt.subplot(4, 3, 4)
        calls = self.df[self.df['option_type'] == 'call']
        puts = self.df[self.df['option_type'] == 'put']
        
        ax4.scatter(calls['moneyness'], calls['impliedVolatility'], alpha=0.3, s=1, label='Calls', c='blue')
        ax4.scatter(puts['moneyness'], puts['impliedVolatility'], alpha=0.3, s=1, label='Puts', c='red')
        ax4.set_xlabel('Moneyness (Strike-Spot)/Spot')
        ax4.set_ylabel('Implied Volatility')
        ax4.set_title('IV vs Moneyness', fontweight='bold')
        ax4.legend()
        ax4.set_xlim(-0.1, 0.1)
        
        # 5. Daily volume over time
        ax5 = plt.subplot(4, 3, 5)
        daily_volume = self.df.groupby(['date', 'option_type'])['volume'].sum().unstack(fill_value=0)
        ax5.plot(daily_volume.index, daily_volume['call'], label='Calls', linewidth=2)
        ax5.plot(daily_volume.index, daily_volume['put'], label='Puts', linewidth=2)
        ax5.set_ylabel('Daily Volume')
        ax5.set_title('Daily Volume Over Time', fontweight='bold')
        ax5.legend()
        
        # 6. Bid-Ask spreads
        ax6 = plt.subplot(4, 3, 6)
        ax6.boxplot([self.df[self.df['option_type'] == 'call']['bid_ask_spread'].dropna(),
                    self.df[self.df['option_type'] == 'put']['bid_ask_spread'].dropna()],
                   labels=['Calls', 'Puts'])
        ax6.set_ylabel('Bid-Ask Spread ($)')
        ax6.set_title('Bid-Ask Spreads by Option Type', fontweight='bold')
        
        # 7. Volume vs Open Interest
        ax7 = plt.subplot(4, 3, 7)
        ax7.scatter(self.df['openInterest'], self.df['volume'], alpha=0.3, s=1)
        ax7.set_xlabel('Open Interest')
        ax7.set_ylabel('Volume')
        ax7.set_title('Volume vs Open Interest', fontweight='bold')
        ax7.set_xscale('log')
        ax7.set_yscale('log')
        
        # 8. IV smile by date (sample dates)
        ax8 = plt.subplot(4, 3, 8)
        sample_dates = self.df['date'].unique()[::10][:5]  # Every 10th date, max 5
        
        for date in sample_dates:
            date_data = self.df[(self.df['date'] == date) & (self.df['option_type'] == 'call')]
            if len(date_data) > 0:
                ax8.plot(date_data['moneyness'], date_data['impliedVolatility'], 
                        marker='o', markersize=2, label=date.strftime('%m-%d'), alpha=0.7)
        
        ax8.set_xlabel('Moneyness')
        ax8.set_ylabel('Implied Volatility')
        ax8.set_title('IV Smile Evolution (Calls)', fontweight='bold')
        ax8.legend()
        ax8.set_xlim(-0.05, 0.05)
        
        # 9. Put-Call Volume Ratio over time
        ax9 = plt.subplot(4, 3, 9)
        pc_ratio = daily_volume['put'] / daily_volume['call']
        ax9.plot(pc_ratio.index, pc_ratio, linewidth=2, color='purple')
        ax9.set_ylabel('Put/Call Volume Ratio')
        ax9.set_title('Put/Call Volume Ratio Over Time', fontweight='bold')
        ax9.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        
        # 10. Price vs Volume correlation
        ax10 = plt.subplot(4, 3, 10)
        price_vol_corr = self.df.groupby('date').agg({
            'spx_close': 'first',
            'volume': 'sum'
        })
        ax10.scatter(price_vol_corr['spx_close'], price_vol_corr['volume'], alpha=0.6)
        ax10.set_xlabel('SPX Close')
        ax10.set_ylabel('Total Daily Volume')
        ax10.set_title('SPX Price vs Total Volume', fontweight='bold')
        
        # 11. VIX vs Total Volume
        ax11 = plt.subplot(4, 3, 11)
        vix_vol_corr = self.df.groupby('date').agg({
            'vix_close': 'first',
            'volume': 'sum'
        })
        ax11.scatter(vix_vol_corr['vix_close'], vix_vol_corr['volume'], alpha=0.6, color='red')
        ax11.set_xlabel('VIX Close')
        ax11.set_ylabel('Total Daily Volume')
        ax11.set_title('VIX vs Total Volume', fontweight='bold')
        
        # 12. Heatmap of average IV by moneyness and date
        ax12 = plt.subplot(4, 3, 12)
        
        # Create moneyness bins
        self.df['moneyness_bin'] = pd.cut(self.df['moneyness'], bins=20, labels=False)
        iv_heatmap = self.df.groupby(['date', 'moneyness_bin'])['impliedVolatility'].mean().unstack(fill_value=np.nan)
        
        sns.heatmap(iv_heatmap.T, ax=ax12, cmap='viridis', cbar_kws={'label': 'Avg IV'})
        ax12.set_xlabel('Date')
        ax12.set_ylabel('Moneyness Bin')
        ax12.set_title('IV Heatmap: Moneyness vs Time', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('visualizations/spx_0dte_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nVisualization saved as 'visualizations/spx_0dte_analysis.png'")
    
    def options_flow_analysis(self):
        """Analyze options flow patterns"""
        print("\n=== OPTIONS FLOW ANALYSIS ===")
        
        # Daily aggregations
        daily_stats = self.df.groupby(['date', 'option_type']).agg({
            'volume': 'sum',
            'openInterest': 'sum',
            'impliedVolatility': 'mean',
            'bid_ask_spread': 'mean'
        }).reset_index()
        
        # High volume days
        total_daily_volume = daily_stats.groupby('date')['volume'].sum()
        high_vol_threshold = total_daily_volume.quantile(0.9)
        high_vol_days = total_daily_volume[total_daily_volume > high_vol_threshold]
        
        print(f"\nHigh Volume Days (>90th percentile: {high_vol_threshold:,.0f}):")
        for date, volume in high_vol_days.sort_values(ascending=False).items():
            spx_close = self.df[self.df['date'] == date]['spx_close'].iloc[0]
            vix_close = self.df[self.df['date'] == date]['vix_close'].iloc[0]
            print(f"  {date.strftime('%Y-%m-%d')}: {volume:,.0f} (SPX: ${spx_close:.0f}, VIX: {vix_close:.1f})")
        
        # ITM vs OTM analysis
        itm_otm = self.df.groupby(['option_type', 'inTheMoney']).agg({
            'volume': ['sum', 'mean'],
            'impliedVolatility': 'mean'
        })
        print(f"\nITM vs OTM Analysis:")
        print(itm_otm)
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*60)
        print("SPX 0DTE OPTIONS DATASET SUMMARY REPORT")
        print("="*60)
        
        self.basic_statistics()
        self.options_flow_analysis()
        
        print(f"\n=== KEY INSIGHTS ===")
        
        # Correlation insights
        spx_vix_corr = self.df.groupby('date').agg({
            'spx_close': 'first',
            'vix_close': 'first'
        }).corr().iloc[0,1]
        
        print(f"SPX-VIX correlation: {spx_vix_corr:.3f}")
        
        # Volume patterns
        avg_call_volume = self.df[self.df['option_type'] == 'call']['volume'].mean()
        avg_put_volume = self.df[self.df['option_type'] == 'put']['volume'].mean()
        print(f"Average call volume per option: {avg_call_volume:.0f}")
        print(f"Average put volume per option: {avg_put_volume:.0f}")
        
        # IV characteristics
        call_iv_avg = self.df[self.df['option_type'] == 'call']['impliedVolatility'].mean()
        put_iv_avg = self.df[self.df['option_type'] == 'put']['impliedVolatility'].mean()
        print(f"Average call IV: {call_iv_avg:.1%}")
        print(f"Average put IV: {put_iv_avg:.1%}")

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = SPXOptionsAnalyzer()
    
    # Generate comprehensive analysis
    analyzer.generate_summary_report()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    print("\n" + "="*60)
    print("Analysis complete! Check 'visualizations/spx_0dte_analysis.png' for visualizations.")
    print("="*60)