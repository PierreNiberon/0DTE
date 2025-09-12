import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from datetime import datetime

def calculate_liquidity_costs():
    """Extract liquidity costs across the entire dataset to visualize market maker profits"""
    
    print("Loading SPX 0DTE options dataset...")
    df = pd.read_csv('dataset/processed/spx_0dte_combined.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"Loaded {len(df):,} options records")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    # Calculate intrinsic values for both calls and puts
    df['intrinsic_value_call'] = np.maximum(df['spx_close'] - df['strike'], 0)
    df['intrinsic_value_put'] = np.maximum(df['strike'] - df['spx_close'], 0)
    
    # Calculate moneyness
    df['moneyness'] = (df['strike'] - df['spx_close']) / df['spx_close']
    
    # Calculate liquidity costs
    liquidity_costs = []
    
    for _, row in df.iterrows():
        date = row['date']
        spx_close = row['spx_close']
        strike = row['strike']
        option_type = row['option_type']
        last_price = row['lastPrice']
        bid = row['bid']
        ask = row['ask']
        volume = row['volume']
        moneyness = row['moneyness']
        
        # Calculate intrinsic value based on option type
        if option_type == 'call':
            intrinsic_value = max(spx_close - strike, 0)
            is_itm = spx_close > strike
        else:  # put
            intrinsic_value = max(strike - spx_close, 0)
            is_itm = strike > spx_close
        
        # Calculate various liquidity cost metrics
        time_value = last_price - intrinsic_value
        bid_ask_spread = ask - bid
        mid_price = (bid + ask) / 2
        
        # Liquidity cost definitions:
        # 1. ITM Discount: How much ITM options trade below intrinsic value
        itm_discount = 0
        if is_itm and intrinsic_value > 0:
            itm_discount = max(0, intrinsic_value - last_price)
        
        # 2. Bid-Ask Spread Cost: Half-spread cost for immediate execution
        spread_cost = bid_ask_spread / 2
        
        # 3. Last vs Mid Price Deviation: Where the last trade occurred vs fair mid
        if mid_price > 0:
            last_vs_mid = (mid_price - last_price) / mid_price
        else:
            last_vs_mid = 0
            
        # 4. Total Effective Liquidity Cost (main metric)
        # For ITM options: discount from intrinsic + spread cost
        # For OTM options: primarily spread cost
        if is_itm:
            effective_liquidity_cost = itm_discount + spread_cost
        else:
            effective_liquidity_cost = spread_cost
        
        # Categorize moneyness for analysis
        if abs(moneyness) < 0.005:  # Within 0.5%
            moneyness_category = 'ATM'
        elif moneyness > 0.005:
            moneyness_category = 'OTM_Call/ITM_Put'
        else:
            moneyness_category = 'ITM_Call/OTM_Put'
        
        liquidity_costs.append({
            'date': date,
            'spx_close': spx_close,
            'strike': strike,
            'option_type': option_type,
            'last_price': last_price,
            'bid': bid,
            'ask': ask,
            'volume': volume,
            'moneyness': moneyness,
            'moneyness_category': moneyness_category,
            'intrinsic_value': intrinsic_value,
            'time_value': time_value,
            'is_itm': is_itm,
            'itm_discount': itm_discount,
            'spread_cost': spread_cost,
            'bid_ask_spread': bid_ask_spread,
            'last_vs_mid': last_vs_mid,
            'effective_liquidity_cost': effective_liquidity_cost,
            'market_maker_profit_per_contract': effective_liquidity_cost * 100  # Convert to dollars per contract
        })
    
    # Convert to DataFrame
    liquidity_df = pd.DataFrame(liquidity_costs)
    
    # Save the processed dataset
    output_path = 'dataset/processed/liquidity_costs_analysis.csv'
    liquidity_df.to_csv(output_path, index=False)
    print(f"\nLiquidity costs dataset saved to {output_path}")
    
    return liquidity_df

def analyze_liquidity_patterns(liquidity_df):
    """Analyze and visualize liquidity cost patterns"""
    
    print("\n=== LIQUIDITY COST ANALYSIS ===")
    
    # Overall statistics
    total_volume = liquidity_df['volume'].sum()
    weighted_avg_cost = (liquidity_df['effective_liquidity_cost'] * liquidity_df['volume']).sum() / total_volume
    total_mm_profit = (liquidity_df['market_maker_profit_per_contract'] * liquidity_df['volume']).sum()
    
    print(f"Total Volume Analyzed: {total_volume:,.0f} contracts")
    print(f"Volume-Weighted Average Liquidity Cost: ${weighted_avg_cost:.4f}")
    print(f"Estimated Total Market Maker Profit: ${total_mm_profit:,.0f}")
    
    # By option type
    by_type = liquidity_df.groupby('option_type').agg({
        'effective_liquidity_cost': ['mean', 'median'],
        'volume': 'sum',
        'market_maker_profit_per_contract': lambda x: (x * liquidity_df.loc[x.index, 'volume']).sum()
    }).round(4)
    
    print(f"\n=== BY OPTION TYPE ===")
    print(by_type)
    
    # By moneyness category
    by_moneyness = liquidity_df.groupby(['option_type', 'moneyness_category']).agg({
        'effective_liquidity_cost': ['mean', 'median', 'count'],
        'volume': 'sum',
        'itm_discount': 'mean',
        'spread_cost': 'mean'
    }).round(4)
    
    print(f"\n=== BY MONEYNESS CATEGORY ===")
    print(by_moneyness)
    
    return liquidity_df

def create_liquidity_visualizations(liquidity_df):
    """Create comprehensive visualizations of liquidity costs"""
    
    print("\nCreating liquidity cost visualizations...")
    
    # Create multi-panel visualization
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(20, 18))
    
    # 1. Daily Market Maker Profits Over Time
    daily_profits = liquidity_df.groupby('date').agg({
        'market_maker_profit_per_contract': lambda x: (x * liquidity_df.loc[x.index, 'volume']).sum(),
        'volume': 'sum'
    })
    
    ax1.plot(daily_profits.index, daily_profits['market_maker_profit_per_contract'], 'g-', linewidth=2)
    ax1.set_title('Daily Market Maker Profits from Liquidity Costs', fontweight='bold')
    ax1.set_ylabel('Total Daily Profit ($)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Liquidity Cost by Moneyness (Scatter)
    calls = liquidity_df[liquidity_df['option_type'] == 'call']
    puts = liquidity_df[liquidity_df['option_type'] == 'put']
    
    ax2.scatter(calls['moneyness'], calls['effective_liquidity_cost'], 
                alpha=0.3, s=calls['volume']/1000, c='blue', label='Calls')
    ax2.scatter(puts['moneyness'], puts['effective_liquidity_cost'], 
                alpha=0.3, s=puts['volume']/1000, c='red', label='Puts')
    ax2.axvline(x=0, color='black', linestyle='--', alpha=0.5, label='ATM')
    ax2.set_xlabel('Moneyness (Strike-Spot)/Spot')
    ax2.set_ylabel('Effective Liquidity Cost ($)')
    ax2.set_title('Liquidity Costs by Moneyness (Size = Volume)', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Volume-Weighted Liquidity Costs by Date and Type
    daily_by_type = liquidity_df.groupby(['date', 'option_type']).agg({
        'effective_liquidity_cost': lambda x: (x * liquidity_df.loc[x.index, 'volume']).sum() / liquidity_df.loc[x.index, 'volume'].sum(),
        'volume': 'sum'
    }).reset_index()
    
    call_daily = daily_by_type[daily_by_type['option_type'] == 'call']
    put_daily = daily_by_type[daily_by_type['option_type'] == 'put']
    
    ax3.plot(call_daily['date'], call_daily['effective_liquidity_cost'], 'b-', label='Calls', linewidth=2)
    ax3.plot(put_daily['date'], put_daily['effective_liquidity_cost'], 'r-', label='Puts', linewidth=2)
    ax3.set_title('Volume-Weighted Daily Liquidity Costs', fontweight='bold')
    ax3.set_ylabel('Avg Liquidity Cost ($)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. ITM Discount Distribution (Where ITM options trade below intrinsic)
    itm_data = liquidity_df[liquidity_df['is_itm'] & (liquidity_df['itm_discount'] > 0)]
    
    if len(itm_data) > 0:
        ax4.hist(itm_data[itm_data['option_type'] == 'call']['itm_discount'], 
                 bins=30, alpha=0.5, label='Call ITM Discounts', color='blue', density=True)
        ax4.hist(itm_data[itm_data['option_type'] == 'put']['itm_discount'], 
                 bins=30, alpha=0.5, label='Put ITM Discounts', color='red', density=True)
        ax4.set_xlabel('ITM Discount ($)')
        ax4.set_ylabel('Density')
        ax4.set_title('Distribution of ITM Option Discounts', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No ITM Discounts Found', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('ITM Discount Distribution', fontweight='bold')
    
    # 5. Heatmap of Liquidity Costs by Date and Moneyness Category
    pivot_data = liquidity_df.groupby(['date', 'option_type', 'moneyness_category']).agg({
        'effective_liquidity_cost': lambda x: (x * liquidity_df.loc[x.index, 'volume']).sum() / liquidity_df.loc[x.index, 'volume'].sum()
    }).reset_index()
    
    # Format dates to show only date part (no time)
    pivot_data['date_str'] = pivot_data['date'].dt.strftime('%Y-%m-%d')
    
    # Create pivot for calls
    call_pivot = pivot_data[pivot_data['option_type'] == 'call'].pivot(
        index='date_str', columns='moneyness_category', values='effective_liquidity_cost'
    )
    
    if not call_pivot.empty:
        sns.heatmap(call_pivot.T, ax=ax5, cmap='Reds', cbar_kws={'label': 'Liquidity Cost ($)'})
        ax5.set_title('Call Options: Liquidity Cost Heatmap', fontweight='bold')
        ax5.set_ylabel('Moneyness Category')
        ax5.set_xlabel('Date')
        # Rotate x-axis labels for better readability
        ax5.tick_params(axis='x', rotation=45)
    else:
        ax5.text(0.5, 0.5, 'Insufficient Call Data', ha='center', va='center', transform=ax5.transAxes)
    
    # 6. Put Options Heatmap
    put_pivot = pivot_data[pivot_data['option_type'] == 'put'].pivot(
        index='date_str', columns='moneyness_category', values='effective_liquidity_cost'
    )
    
    if not put_pivot.empty:
        sns.heatmap(put_pivot.T, ax=ax6, cmap='Blues', cbar_kws={'label': 'Liquidity Cost ($)'})
        ax6.set_title('Put Options: Liquidity Cost Heatmap', fontweight='bold')
        ax6.set_ylabel('Moneyness Category')
        ax6.set_xlabel('Date')
        # Rotate x-axis labels for better readability
        ax6.tick_params(axis='x', rotation=45)
    else:
        ax6.text(0.5, 0.5, 'Insufficient Put Data', ha='center', va='center', transform=ax6.transAxes)
    
    plt.tight_layout()
    plt.savefig('visualizations/06_liquidity_costs_surface.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Liquidity cost visualizations saved as 'visualizations/06_liquidity_costs_surface.png'")

def main():
    """Main execution function"""
    
    print("=== MARKET MAKER LIQUIDITY COST EXTRACTION ===")
    print("Analyzing where market makers make money from bid-ask spreads and ITM discounts...\n")
    
    # Extract liquidity costs
    liquidity_df = calculate_liquidity_costs()
    
    # Analyze patterns
    liquidity_df = analyze_liquidity_patterns(liquidity_df)
    
    # Create visualizations
    create_liquidity_visualizations(liquidity_df)
    
    print("\n" + "="*70)
    print("LIQUIDITY COST ANALYSIS COMPLETE!")
    print("Dataset saved: dataset/processed/liquidity_costs_analysis.csv")
    print("Visualization: visualizations/06_liquidity_costs_surface.png")
    print("="*70)

if __name__ == "__main__":
    main()