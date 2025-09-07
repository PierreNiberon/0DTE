import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SPXInteractive3D:
    def __init__(self, csv_path='dataset/processed/spx_0dte_combined.csv'):
        """Initialize the interactive 3D visualizer"""
        print("Loading SPX 0DTE options data for interactive 3D visualization...")
        self.df = pd.read_csv(csv_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Sort by date and strike for proper surface plotting
        self.df = self.df.sort_values(['date', 'strike'])
        
        print(f"Loaded {len(self.df):,} options records")
        print(f"Date range: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
        print(f"Strike range: ${self.df['strike'].min():.0f} - ${self.df['strike'].max():.0f}")

    def create_interactive_price_surface(self, option_type='call', sample_every=3):
        """Create interactive 3D surface of option prices"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating interactive {option_type} price surface with {len(sample_dates)} dates...")
        
        # Prepare data for surface plot
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        
        # Create coordinate arrays
        date_indices = list(range(len(dates)))
        strike_values = strikes
        
        # Create meshgrid
        X, Y = np.meshgrid(date_indices, strike_values)
        Z = np.full((len(strike_values), len(date_indices)), np.nan)
        
        # Fill Z with option prices
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            for j, strike in enumerate(strike_values):
                strike_data = date_data[date_data['strike'] == strike]
                if not strike_data.empty:
                    Z[j, i] = strike_data['lastPrice'].iloc[0]
        
        # Create the surface plot
        fig = go.Figure()
        
        # Add options surface
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Viridis',
            name=f'{option_type.title()} Prices',
            hovertemplate='Date: %{x}<br>Strike: $%{y}<br>Price: $%{z:.2f}<extra></extra>',
            opacity=0.8
        ))
        
        # Add SPX price line
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        max_z = np.nanmax(Z) * 1.1
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=spx_prices,
            z=[max_z] * len(date_indices),
            mode='lines+markers',
            line=dict(color='red', width=8),
            marker=dict(size=4, color='red'),
            name='SPX Close',
            hovertemplate='Date: %{x}<br>SPX: $%{y:.2f}<extra></extra>'
        ))
        
        # Create date labels for hover
        date_labels = [d.strftime('%Y-%m-%d') for d in dates]
        
        # Update layout
        fig.update_layout(
            title=f'Interactive 3D {option_type.title()} Options Price Surface<br>SPX 0DTE Options',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Strike Price ($)',
                zaxis_title=f'{option_type.title()} Price ($)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            width=1000,
            height=700,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        # Save and show
        filename = f'visualizations/interactive_3d_{option_type}_prices.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Interactive {option_type} surface saved as '{filename}'")
        return fig

    def create_interactive_iv_surface(self, option_type='call', sample_every=3):
        """Create interactive 3D surface of implied volatility"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = data[data['date'].isin(sample_dates)]
        
        print(f"Creating interactive {option_type} IV surface with {len(sample_dates)} dates...")
        
        # Prepare data for surface plot
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        
        # Create coordinate arrays
        date_indices = list(range(len(dates)))
        strike_values = strikes
        
        # Create meshgrid
        X, Y = np.meshgrid(date_indices, strike_values)
        Z = np.full((len(strike_values), len(date_indices)), np.nan)
        
        # Fill Z with implied volatility
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            for j, strike in enumerate(strike_values):
                strike_data = date_data[date_data['strike'] == strike]
                if not strike_data.empty:
                    Z[j, i] = strike_data['impliedVolatility'].iloc[0]
        
        # Create the surface plot
        fig = go.Figure()
        
        # Add IV surface
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Plasma',
            name=f'{option_type.title()} IV',
            hovertemplate='Date: %{x}<br>Strike: $%{y}<br>IV: %{z:.2%}<extra></extra>',
            opacity=0.9
        ))
        
        # Add SPX price line
        spx_prices = []
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
        
        max_z = np.nanmax(Z) * 1.1
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=spx_prices,
            z=[max_z] * len(date_indices),
            mode='lines+markers',
            line=dict(color='white', width=8),
            marker=dict(size=4, color='white'),
            name='SPX Close',
            hovertemplate='Date: %{x}<br>SPX: $%{y:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Interactive 3D {option_type.title()} Implied Volatility Surface<br>SPX 0DTE Options',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Strike Price ($)',
                zaxis_title=f'{option_type.title()} IV',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            width=1000,
            height=700,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        # Save and show
        filename = f'visualizations/interactive_3d_{option_type}_iv.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Interactive {option_type} IV surface saved as '{filename}'")
        return fig

    def create_combined_interactive_surface(self, sample_every=4):
        """Create combined interactive surface with both calls and puts"""
        
        # Sample data for performance
        unique_dates = sorted(self.df['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = self.df[self.df['date'].isin(sample_dates)].copy()
        
        print(f"Creating combined interactive surface with {len(sample_dates)} dates...")
        
        # Prepare data
        dates = sorted(data['date'].unique())
        strikes = sorted(data['strike'].unique())
        date_indices = list(range(len(dates)))
        
        # Create the figure
        fig = go.Figure()
        
        # Process both calls and puts
        colors = {'call': 'Viridis', 'put': 'Plasma'}
        opacities = {'call': 0.7, 'put': 0.7}
        
        for option_type in ['call', 'put']:
            type_data = data[data['option_type'] == option_type]
            
            # Create meshgrid
            X, Y = np.meshgrid(date_indices, strikes)
            Z = np.full((len(strikes), len(date_indices)), np.nan)
            
            # Fill Z with option prices
            for i, date in enumerate(dates):
                date_data = type_data[type_data['date'] == date]
                for j, strike in enumerate(strikes):
                    strike_data = date_data[date_data['strike'] == strike]
                    if not strike_data.empty:
                        Z[j, i] = strike_data['lastPrice'].iloc[0]
            
            # Add surface
            fig.add_trace(go.Surface(
                x=X, y=Y, z=Z,
                colorscale=colors[option_type],
                name=f'{option_type.title()} Options',
                hovertemplate=f'{option_type.title()}<br>Date: %{{x}}<br>Strike: $%{{y}}<br>Price: $%{{z:.2f}}<extra></extra>',
                opacity=opacities[option_type],
                showscale=True if option_type == 'call' else False
            ))
        
        # Add SPX price line
        spx_prices = []
        max_option_price = 0
        for date in dates:
            spx_price = data[data['date'] == date]['spx_close'].iloc[0]
            spx_prices.append(spx_price)
            max_price = data[data['date'] == date]['lastPrice'].max()
            if max_price > max_option_price:
                max_option_price = max_price
        
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=spx_prices,
            z=[max_option_price * 1.3] * len(date_indices),
            mode='lines+markers',
            line=dict(color='red', width=10),
            marker=dict(size=6, color='red'),
            name='SPX Close',
            hovertemplate='Date: %{x}<br>SPX: $%{y:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='Interactive 3D Combined Options Surface<br>SPX 0DTE Calls & Puts',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Strike Price ($)',
                zaxis_title='Option Price ($)',
                camera=dict(
                    eye=dict(x=1.3, y=1.3, z=1.0)
                )
            ),
            width=1200,
            height=800,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        # Save and show
        filename = 'visualizations/interactive_3d_combined.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Combined interactive surface saved as '{filename}'")
        return fig

    def create_moneyness_surface(self, option_type='call', sample_every=3):
        """Create surface using moneyness instead of absolute strikes"""
        
        # Filter and sample data
        data = self.df[self.df['option_type'] == option_type].copy()
        unique_dates = sorted(data['date'].unique())
        sample_dates = unique_dates[::sample_every]
        data = data[data['date'].isin(sample_dates)]
        
        # Calculate moneyness
        data['moneyness'] = (data['strike'] - data['spx_close']) / data['spx_close']
        
        print(f"Creating interactive {option_type} moneyness surface with {len(sample_dates)} dates...")
        
        # Prepare data for surface plot
        dates = sorted(data['date'].unique())
        moneyness_values = sorted(data['moneyness'].unique())
        
        # Filter to reasonable moneyness range
        moneyness_values = [m for m in moneyness_values if -0.1 <= m <= 0.1]
        
        # Create coordinate arrays
        date_indices = list(range(len(dates)))
        
        # Create meshgrid
        X, Y = np.meshgrid(date_indices, moneyness_values)
        Z = np.full((len(moneyness_values), len(date_indices)), np.nan)
        
        # Fill Z with option prices
        for i, date in enumerate(dates):
            date_data = data[data['date'] == date]
            for j, moneyness in enumerate(moneyness_values):
                # Find closest moneyness
                closest_data = date_data.iloc[(date_data['moneyness'] - moneyness).abs().argsort()[:1]]
                if not closest_data.empty and abs(closest_data['moneyness'].iloc[0] - moneyness) < 0.005:
                    Z[j, i] = closest_data['lastPrice'].iloc[0]
        
        # Create the surface plot
        fig = go.Figure()
        
        # Add options surface
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Viridis',
            name=f'{option_type.title()} Prices',
            hovertemplate='Date: %{x}<br>Moneyness: %{y:.1%}<br>Price: $%{z:.2f}<extra></extra>',
            opacity=0.8
        ))
        
        # Add ATM line (moneyness = 0)
        max_z = np.nanmax(Z) * 1.1
        fig.add_trace(go.Scatter3d(
            x=date_indices,
            y=[0] * len(date_indices),
            z=[max_z] * len(date_indices),
            mode='lines+markers',
            line=dict(color='red', width=8),
            marker=dict(size=4, color='red'),
            name='ATM Line',
            hovertemplate='Date: %{x}<br>ATM<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Interactive 3D {option_type.title()} Options by Moneyness<br>SPX 0DTE Options',
            scene=dict(
                xaxis_title='Time (Date Index)',
                yaxis_title='Moneyness (Strike-Spot)/Spot',
                zaxis_title=f'{option_type.title()} Price ($)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            width=1000,
            height=700,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        # Save and show
        filename = f'visualizations/interactive_3d_{option_type}_moneyness.html'
        fig.write_html(filename)
        fig.show()
        
        print(f"Interactive {option_type} moneyness surface saved as '{filename}'")
        return fig

def main():
    # Initialize visualizer
    viz = SPXInteractive3D()
    
    print("\nCreating interactive 3D visualizations...")
    print("Note: These will open in your default web browser and save as .html files")
    
    # Create various interactive 3D visualizations
    
    # 1. Call options price surface
    viz.create_interactive_price_surface(option_type='call')
    
    # 2. Put options price surface  
    viz.create_interactive_price_surface(option_type='put')
    
    # 3. Call options IV surface
    viz.create_interactive_iv_surface(option_type='call')
    
    # 4. Combined surface
    viz.create_combined_interactive_surface()
    
    # 5. Moneyness-based surface
    viz.create_moneyness_surface(option_type='call')
    
    print("\n" + "="*70)
    print("Interactive 3D visualizations complete!")
    print("Check the visualizations/ folder for .html files")
    print("You can rotate, zoom, and explore each surface interactively!")
    print("="*70)

if __name__ == "__main__":
    main()