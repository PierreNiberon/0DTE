import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SPX3DVisualizer:
    def __init__(self, csv_path='dataset/processed/spx_0dte_combined.csv'):
        """Initialize the 3D visualizer with the combined dataset"""
        print("Loading SPX 0DTE options data for 3D visualization...")
        self.df = pd.read_csv(csv_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Sort by date and strike for proper surface plotting
        self.df = self.df.sort_values(['date', 'strike'])
        
        print(f"Loaded {len(self.df):,} options records")
        print(f"Date range: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
        print(f"Strike range: ${self.df['strike'].min():.0f} - ${self.df['strike'].max():.0f}")

    def create_3d_price_surface(self, option_type='call', sample_dates=None, save_name='3d_price_surface'):
        """Create 3D surface plot of option prices"""
        
        # Filter data
        data = self.df[self.df['option_type'] == option_type].copy()
        
        # Sample dates if not provided (for performance)
        if sample_dates is None:
            unique_dates = sorted(data['date'].unique())
            sample_dates = unique_dates[::5]  # Every 5th date
        
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating 3D {option_type} price surface with {len(sample_dates)} dates...")
        
        # Create figure
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Prepare data for surface plot
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        
        # Create meshgrid
        X, Y = np.meshgrid(range(len(dates)), strikes)
        Z = np.full((len(strikes), len(dates)), np.nan)
        
        # Fill Z with option prices
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            for j, strike in enumerate(strikes):
                strike_data = date_data[date_data['strike'] == strike]
                if not strike_data.empty:
                    Z[j, i] = strike_data['lastPrice'].iloc[0]
        
        # Create surface plot
        surface = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, 
                                 linewidth=0, antialiased=True)
        
        # Add SPX price line
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        ax.plot(range(len(dates)), spx_prices, [max(Z[~np.isnan(Z)]) * 1.1] * len(dates), 
                'red', linewidth=4, label='SPX Price', alpha=0.9)
        
        # Customize plot
        ax.set_xlabel('Time (Date Index)', fontsize=12)
        ax.set_ylabel('Strike Price ($)', fontsize=12)
        ax.set_zlabel(f'{option_type.title()} Option Price ($)', fontsize=12)
        ax.set_title(f'3D {option_type.title()} Options Price Surface\nSPX 0DTE Options', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Set date labels (sample)
        date_labels = [d.strftime('%m/%d') for d in dates[::max(1, len(dates)//8)]]
        ax.set_xticks(range(0, len(dates), max(1, len(dates)//8)))
        ax.set_xticklabels(date_labels, rotation=45)
        
        # Add colorbar
        plt.colorbar(surface, ax=ax, shrink=0.6, aspect=30, 
                    label=f'{option_type.title()} Price ($)')
        
        # Add legend
        ax.legend(loc='upper left')
        
        # Adjust viewing angle
        ax.view_init(elev=20, azim=45)
        
        plt.tight_layout()
        plt.savefig(f'visualizations/{save_name}_{option_type}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"3D {option_type} surface saved as 'visualizations/{save_name}_{option_type}.png'")

    def create_3d_iv_surface(self, option_type='call', sample_dates=None, save_name='3d_iv_surface'):
        """Create 3D surface plot of implied volatility"""
        
        # Filter data
        data = self.df[self.df['option_type'] == option_type].copy()
        
        # Sample dates if not provided
        if sample_dates is None:
            unique_dates = sorted(data['date'].unique())
            sample_dates = unique_dates[::5]  # Every 5th date
        
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating 3D {option_type} IV surface with {len(sample_dates)} dates...")
        
        # Create figure
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Prepare data for surface plot
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        
        # Create meshgrid
        X, Y = np.meshgrid(range(len(dates)), strikes)
        Z = np.full((len(strikes), len(dates)), np.nan)
        
        # Fill Z with implied volatility
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            for j, strike in enumerate(strikes):
                strike_data = date_data[date_data['strike'] == strike]
                if not strike_data.empty:
                    Z[j, i] = strike_data['impliedVolatility'].iloc[0]
        
        # Create surface plot
        surface = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8, 
                                 linewidth=0, antialiased=True)
        
        # Add SPX price line
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        ax.plot(range(len(dates)), spx_prices, [np.nanmax(Z) * 1.1] * len(dates), 
                'white', linewidth=4, label='SPX Price', alpha=1.0)
        
        # Customize plot
        ax.set_xlabel('Time (Date Index)', fontsize=12)
        ax.set_ylabel('Strike Price ($)', fontsize=12)
        ax.set_zlabel(f'{option_type.title()} Implied Volatility', fontsize=12)
        ax.set_title(f'3D {option_type.title()} Implied Volatility Surface\nSPX 0DTE Options', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Set date labels
        date_labels = [d.strftime('%m/%d') for d in dates[::max(1, len(dates)//8)]]
        ax.set_xticks(range(0, len(dates), max(1, len(dates)//8)))
        ax.set_xticklabels(date_labels, rotation=45)
        
        # Add colorbar
        plt.colorbar(surface, ax=ax, shrink=0.6, aspect=30, 
                    label=f'{option_type.title()} IV')
        
        # Add legend
        ax.legend(loc='upper left')
        
        # Adjust viewing angle
        ax.view_init(elev=25, azim=60)
        
        plt.tight_layout()
        plt.savefig(f'visualizations/{save_name}_{option_type}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"3D {option_type} IV surface saved as 'visualizations/{save_name}_{option_type}.png'")

    def create_combined_3d_surface(self, sample_dates=None, save_name='3d_combined_surface'):
        """Create combined 3D surface showing both calls and puts"""
        
        # Sample dates if not provided
        if sample_dates is None:
            unique_dates = sorted(self.df['date'].unique())
            sample_dates = unique_dates[::7]  # Every 7th date for performance
        
        data = self.df[self.df['date'].isin(sample_dates)].copy()
        
        print(f"Creating combined 3D surface with {len(sample_dates)} dates...")
        
        # Create figure
        fig = plt.figure(figsize=(18, 14))
        ax = fig.add_subplot(111, projection='3d')
        
        # Prepare data
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        
        # Create surfaces for both calls and puts
        for option_type, color, alpha in [('call', 'viridis', 0.7), ('put', 'plasma', 0.7)]:
            type_data = data[data['option_type'] == option_type]
            
            # Create meshgrid
            X, Y = np.meshgrid(range(len(dates)), strikes)
            Z = np.full((len(strikes), len(dates)), np.nan)
            
            # Fill Z with option prices
            for i, date in enumerate(dates):
                date_data = type_data[type_data['date'] == date]
                for j, strike in enumerate(strikes):
                    strike_data = date_data[date_data['strike'] == strike]
                    if not strike_data.empty:
                        Z[j, i] = strike_data['lastPrice'].iloc[0]
            
            # Create surface plot
            surface = ax.plot_surface(X, Y, Z, cmap=color, alpha=alpha, 
                                     linewidth=0, antialiased=True,
                                     label=f'{option_type.title()} Options')
        
        # Add SPX price line (elevated above the surfaces)
        spx_prices = []
        max_option_price = 0
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
            max_price = data[data['date'] == date]['lastPrice'].max()
            if max_price > max_option_price:
                max_option_price = max_price
        
        ax.plot(range(len(dates)), spx_prices, [max_option_price * 1.2] * len(dates), 
                'red', linewidth=5, label='SPX Close', alpha=1.0)
        
        # Customize plot
        ax.set_xlabel('Time (Date Index)', fontsize=12)
        ax.set_ylabel('Strike Price ($)', fontsize=12)
        ax.set_zlabel('Option Price ($)', fontsize=12)
        ax.set_title('3D Combined Options Price Surface\nSPX 0DTE Calls & Puts', 
                     fontsize=16, fontweight='bold', pad=30)
        
        # Set date labels
        date_labels = [d.strftime('%m/%d') for d in dates[::max(1, len(dates)//6)]]
        ax.set_xticks(range(0, len(dates), max(1, len(dates)//6)))
        ax.set_xticklabels(date_labels, rotation=45)
        
        # Add custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='purple', alpha=0.7, label='Call Options'),
            Patch(facecolor='orange', alpha=0.7, label='Put Options'),
            plt.Line2D([0], [0], color='red', linewidth=3, label='SPX Close')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        # Adjust viewing angle
        ax.view_init(elev=15, azim=45)
        
        plt.tight_layout()
        plt.savefig(f'visualizations/{save_name}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Combined 3D surface saved as 'visualizations/{save_name}.png'")

def main():
    # Initialize visualizer
    viz = SPX3DVisualizer()
    
    # Create various 3D visualizations
    print("\nCreating 3D visualizations...")
    
    # 1. Call options price surface
    viz.create_3d_price_surface(option_type='call')
    
    # 2. Put options price surface  
    viz.create_3d_price_surface(option_type='put')
    
    # 3. Call options IV surface
    viz.create_3d_iv_surface(option_type='call')
    
    # 4. Combined surface (both calls and puts)
    viz.create_combined_3d_surface()
    
    print("\n" + "="*60)
    print("3D visualizations complete! Check the visualizations/ folder.")
    print("="*60)

if __name__ == "__main__":
    main()