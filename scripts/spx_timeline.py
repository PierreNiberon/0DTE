import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def create_spx_timeline():
    """Create a timeline visualization of SPX prices from the dataset"""
    
    # Load the dataset
    print("Loading SPX 0DTE options dataset...")
    df = pd.read_csv('dataset/processed/spx_0dte_combined.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Get unique dates and SPX prices (one per day)
    daily_data = df.groupby('date').agg({
        'spx_close': 'first'
    }).reset_index()
    
    print(f'Date range: {daily_data["date"].min().date()} to {daily_data["date"].max().date()}')
    print(f'SPX price range: ${daily_data["spx_close"].min():.2f} to ${daily_data["spx_close"].max():.2f}')
    print(f'Total trading days: {len(daily_data)}')
    
    # Create the plot
    plt.figure(figsize=(14, 8))
    plt.plot(daily_data['date'], daily_data['spx_close'], 
             linewidth=2, color='blue', marker='o', markersize=3)
    
    plt.title('SPX Price Over Time\nFrom First to Last Date in Dataset', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('SPX Close Price ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Add statistics as text box
    min_price = daily_data['spx_close'].min()
    max_price = daily_data['spx_close'].max()
    avg_price = daily_data['spx_close'].mean()
    
    stats_text = f'Min: ${min_price:.2f}\nMax: ${max_price:.2f}\nAvg: ${avg_price:.2f}'
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('visualizations/spx_price_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print('SPX price visualization saved as visualizations/spx_price_timeline.png')

if __name__ == "__main__":
    create_spx_timeline()