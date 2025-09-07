import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SPXBased3D:
    def __init__(self, csv_path='dataset/processed/spx_0dte_combined.csv'):
        """Initialize the SPX-based 3D visualizer"""
        print("Loading SPX 0DTE options data for SPX-based 3D visualization...")
        self.df = pd.read_csv(csv_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Sort by date and strike for proper surface plotting
        self.df = self.df.sort_values(['date', 'strike'])
        
        print(f"Loaded {len(self.df):,} options records")
        print(f"Date range: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
        print(f"SPX range: ${self.df['spx_close'].min():.0f} - ${self.df['spx_close'].max():.0f}")

    def create_spx_based_surface(self, option_type='call', sample_every=3, show_all_dates=False):
        """Create 3D surface with SPX price on Y-axis and options extending upward"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        
        if show_all_dates:
            sample_dates = unique_dates
            sample_every = 1
        else:
            sample_dates = unique_dates[::sample_every]
            
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating SPX-based {option_type} surface with {len(sample_dates)} dates (every {sample_every} days)...")
        print(f"Date range: {sample_dates[0].strftime('%Y-%m-%d')} to {sample_dates[-1].strftime('%Y-%m-%d')}")
        
        # Prepare data
        dates = sorted(data['date'].unique())
        date_indices = list(range(len(dates)))
        
        # Get SPX price range and create Y-axis grid
        spx_min = data['spx_close'].min()
        spx_max = data['spx_close'].max()
        spx_range = np.linspace(spx_min * 0.95, spx_max * 1.05, 50)  # 50 points along SPX range
        
        # Create meshgrid
        X, Y = np.meshgrid(date_indices, spx_range)
        Z = np.full((len(spx_range), len(date_indices)), np.nan)
        
        # For each date and SPX price level, find the closest option and calculate Z
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            current_spx = date_data['spx_close'].iloc[0]
            
            for j, spx_level in enumerate(spx_range):
                # Find options closest to this SPX level (treating SPX level as strike)
                closest_strikes = date_data.iloc[(date_data['strike'] - spx_level).abs().argsort()[:3]]
                
                if not closest_strikes.empty:
                    # Use the closest strike
                    closest_option = closest_strikes.iloc[0]
                    option_premium = closest_option['lastPrice']
                    
                    # Z = SPX price + option premium (options extend above SPX line)
                    Z[j, i] = current_spx + option_premium
        
        # Create the figure
        fig = go.Figure()
        
        # Add options surface
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Viridis',
            name=f'{option_type.title()} Surface',
            hovertemplate=f'{option_type.title()}<br>Date: %{{x}}<br>SPX Level: $%{{y:.0f}}<br>SPX + Premium: $%{{z:.2f}}<extra></extra>',
            opacity=0.8,
            colorbar=dict(title=f"SPX + {option_type.title()} Premium")
        ))
        
        # Add SPX baseline (the actual SPX price line)
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=spx_prices,
            z=spx_prices,  # Z = Y for the baseline
            mode='lines+markers',
            line=dict(color='red', width=10),
            marker=dict(size=6, color='red'),
            name='SPX Close (Baseline)',
            hovertemplate='Date: %{x}<br>SPX: $%{y:.2f}<extra></extra>'
        ))
        
        # Create better X-axis labels with actual dates
        date_labels = [d.strftime('%m/%d') for d in dates]
        
        # Update layout with larger, wider aspect ratio
        fig.update_layout(
            title=f'3D {option_type.title()} Options Surface - All {len(dates)} Trading Days<br>Y-axis: SPX Price, Z-axis: SPX + Option Premium',
            scene=dict(
                xaxis_title='Date',
                yaxis_title='SPX Price Level ($)',
                zaxis_title='SPX + Option Premium ($)',
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(0, len(dates), max(1, len(dates)//12))),
                    ticktext=[date_labels[i] for i in range(0, len(dates), max(1, len(dates)//12))]
                ),
                camera=dict(
                    eye=dict(x=2.0, y=1.2, z=1.0)
                ),
                aspectmode='manual',
                aspectratio=dict(x=2.0, y=1.0, z=0.8)  # Make X (time) axis longer
            ),
            width=1600,  # Much wider
            height=900,  # Taller but not as much
            margin=dict(l=20, r=20, b=20, t=100)
        )
        
        # Save and show
        filename = f'visualizations/spx_based_3d_{option_type}.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"SPX-based {option_type} surface saved as '{filename}'")
        return fig

    def create_moneyness_spx_surface(self, option_type='call', sample_every=3):
        """Alternative approach: Y-axis as moneyness offset from SPX"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating moneyness-SPX {option_type} surface with {len(sample_dates)} dates...")
        
        # Calculate moneyness in absolute dollar terms
        data['moneyness_dollars'] = data['strike'] - data['spx_close']
        
        # Prepare data
        dates = sorted(data['date'].unique())
        date_indices = list(range(len(dates)))
        
        # Create moneyness range (in dollars from SPX)
        moneyness_range = np.linspace(-200, 200, 41)  # -$200 to +$200 from SPX
        
        # Create meshgrid
        X, Y = np.meshgrid(date_indices, moneyness_range)
        Z = np.full((len(moneyness_range), len(date_indices)), np.nan)
        
        # For each date and moneyness level, find option premium
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            current_spx = date_data['spx_close'].iloc[0]
            
            for j, moneyness_dollars in enumerate(moneyness_range):
                # Find options closest to this moneyness
                closest_options = date_data.iloc[(date_data['moneyness_dollars'] - moneyness_dollars).abs().argsort()[:1]]
                
                if not closest_options.empty:
                    closest_option = closest_options.iloc[0]
                    option_premium = closest_option['lastPrice']
                    
                    # Z = SPX price + option premium
                    Z[j, i] = current_spx + option_premium
        
        # Create the figure
        fig = go.Figure()
        
        # Add options surface
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Plasma',
            name=f'{option_type.title()} Surface',
            hovertemplate=f'{option_type.title()}<br>Date: %{{x}}<br>Moneyness: $%{{y:.0f}}<br>SPX + Premium: $%{{z:.2f}}<extra></extra>',
            opacity=0.8,
            colorbar=dict(title=f"SPX + {option_type.title()} Premium")
        ))
        
        # Add SPX baseline at Y=0 (ATM)
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=[0] * len(date_indices),  # Y=0 represents ATM
            z=spx_prices,  # Z = SPX price (baseline)
            mode='lines+markers',
            line=dict(color='red', width=10),
            marker=dict(size=6, color='red'),
            name='SPX Close (ATM Baseline)',
            hovertemplate='Date: %{x}<br>ATM<br>SPX: $%{z:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'3D {option_type.title()} Options Surface<br>Y-axis: $ from SPX, Z-axis: SPX + Option Premium',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Dollars from SPX (Strike - SPX)',
                zaxis_title='SPX + Option Premium ($)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            width=1200,
            height=800,
            margin=dict(l=0, r=0, b=0, t=80)
        )
        
        # Save and show
        filename = f'visualizations/moneyness_spx_3d_{option_type}.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Moneyness-SPX {option_type} surface saved as '{filename}'")
        return fig

    def create_simple_spx_extension(self, option_type='call', sample_every=4):
        """Simplest version: just show how options extend above SPX price"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating simple SPX extension for {option_type} with {len(sample_dates)} dates...")
        
        # Create figure
        fig = go.Figure()
        
        # For each date, create a "fan" of options extending from SPX price
        dates = sorted(data['date'].unique())
        
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            current_spx = date_data['spx_close'].iloc[0]
            
            # Get option data for this date
            strikes = sorted(date_data['strike'].unique())
            prices = []
            z_values = []
            
            for strike in strikes:
                strike_data = date_data[date_data['strike'] == strike]
                if not strike_data.empty:
                    option_price = strike_data['lastPrice'].iloc[0]
                    prices.append(strike)
                    z_values.append(current_spx + option_price)  # Extend above SPX
            
            # Add scatter for this date
            fig.add_trace(go.Scatter3d(
                x=[i] * len(prices),
                y=prices,  # Strike prices on Y-axis
                z=z_values,  # SPX + premium on Z-axis
                mode='markers',
                marker=dict(
                    size=4,
                    color=z_values,
                    colorscale='Viridis',
                    opacity=0.8
                ),
                name=f'{date.strftime("%m/%d")}',
                hovertemplate=f'Date: {date.strftime("%Y-%m-%d")}<br>Strike: $%{{y:.0f}}<br>SPX+Premium: $%{{z:.2f}}<extra></extra>',
                showlegend=False
            ))
        
        # Add SPX baseline
        spx_prices = []
        spx_y_values = []
        for i, date in enumerate(dates):
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
            spx_y_values.append(spx_price)  # SPX price on both Y and Z for baseline
        
        fig.add_trace(go.Scatter3d(
            x=list(range(len(dates))),
            y=spx_y_values,
            z=spx_prices,
            mode='lines+markers',
            line=dict(color='red', width=8),
            marker=dict(size=6, color='red'),
            name='SPX Close',
            hovertemplate='Date: %{x}<br>SPX: $%{y:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'3D {option_type.title()} Options Extension from SPX<br>Options "float" above SPX baseline by their premium',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Strike Price ($)',
                zaxis_title='SPX + Option Premium ($)',
                camera=dict(
                    eye=dict(x=1.3, y=1.3, z=1.0)
                )
            ),
            width=1200,
            height=800,
            margin=dict(l=0, r=0, b=0, t=80)
        )
        
        # Save and show
        filename = f'visualizations/simple_spx_extension_{option_type}.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Simple SPX extension for {option_type} saved as '{filename}'")
        return fig

def main():
    # Initialize visualizer
    viz = SPXBased3D()
    
    print("\nCreating full SPX-based 3D visualization...")
    print("Using all 90 trading days with larger, wider display...")
    
    # Create the full dataset visualization with improved layout
    viz.create_spx_based_surface(option_type='call', sample_every=1)
    
    print("\n" + "="*70)
    print("Full SPX-based 3D visualization complete!")
    print("Check visualizations/spx_based_3d_call.html - now larger and wider!")
    print("="*70)

if __name__ == "__main__":
    main()