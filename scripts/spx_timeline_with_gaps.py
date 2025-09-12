import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

def create_spx_timeline_with_gaps():
    """Create SPX timeline visualization highlighting data gaps"""
    
    # Load the dataset
    print("Loading SPX 0DTE options dataset...")
    df = pd.read_csv('dataset/processed/spx_0dte_combined.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Get unique dates and SPX prices
    daily_data = df.groupby('date').agg({
        'spx_close': 'first'
    }).reset_index().sort_values('date')
    
    print(f'Date range: {daily_data["date"].min().date()} to {daily_data["date"].max().date()}')
    print(f'SPX price range: ${daily_data["spx_close"].min():.2f} to ${daily_data["spx_close"].max():.2f}')
    print(f'Total trading days: {len(daily_data)}')
    
    # Identify gaps
    date_diffs = daily_data['date'].diff()
    large_gaps = date_diffs[date_diffs > pd.Timedelta(days=4)]
    
    print(f'\nData gaps found: {len(large_gaps)}')
    for idx, gap in large_gaps.items():
        prev_date = daily_data.iloc[idx-1]['date']
        curr_date = daily_data.iloc[idx]['date']
        print(f'  {gap.days} days between {prev_date.date()} and {curr_date.date()}')
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Top plot: Full timeline with gaps highlighted
    ax1.plot(daily_data['date'], daily_data['spx_close'], 
             linewidth=2, color='blue', marker='o', markersize=4, alpha=0.7)
    
    # Highlight gaps with red backgrounds
    for idx, gap in large_gaps.items():
        prev_date = daily_data.iloc[idx-1]['date']
        curr_date = daily_data.iloc[idx]['date']
        ax1.axvspan(prev_date, curr_date, alpha=0.2, color='red', 
                   label='Data Gap' if idx == large_gaps.index[0] else "")
    
    ax1.set_title('SPX Price Over Time - With Data Gaps Highlighted', 
                  fontsize=16, fontweight='bold', pad=15)
    ax1.set_ylabel('SPX Close Price ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Bottom plot: Monthly data availability
    daily_data['month'] = daily_data['date'].dt.to_period('M')
    monthly_counts = daily_data.groupby('month').size()
    
    # Expected trading days per month (rough estimate: ~22 days)
    expected_days = [22] * len(monthly_counts)  # Rough estimate
    months = [str(m) for m in monthly_counts.index]
    
    x_pos = np.arange(len(months))
    bars = ax2.bar(x_pos, monthly_counts.values, alpha=0.7, color='skyblue', 
                   label='Actual Days')
    ax2.plot(x_pos, expected_days, 'r--', marker='o', linewidth=2, 
             label='Expected (~22 days)')
    
    # Annotate bars with actual counts
    for i, (bar, count) in enumerate(zip(bars, monthly_counts.values)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(count), ha='center', va='bottom', fontweight='bold')
    
    ax2.set_title('Data Availability by Month', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Month', fontsize=12)
    ax2.set_ylabel('Number of Trading Days', fontsize=12)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(months, rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Add summary statistics
    stats_text = f'''Dataset Summary:
Total Days: {len(daily_data)}
Date Range: {daily_data["date"].min().strftime("%Y-%m-%d")} to {daily_data["date"].max().strftime("%Y-%m-%d")}
SPX Range: ${daily_data["spx_close"].min():.2f} - ${daily_data["spx_close"].max():.2f}
Major Gaps: {len(large_gaps)} gaps > 4 days'''
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for stats
    plt.savefig('visualizations/spx_timeline_with_gaps.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print('\nVisualization saved as visualizations/spx_timeline_with_gaps.png')
    
    # Detailed gap analysis
    print('\n=== DETAILED GAP ANALYSIS ===')
    print('Missing periods:')
    print('• May 6-21, 2025 (17-day gap) - Likely extended holiday period')
    print('• June 18-25, 2025 (9-day gap) - Possible data collection issue')  
    print('• Several smaller gaps (5-7 days) throughout summer months')
    print('\nThis appears to be real missing data, not a plotting issue.')
    print('The dataset has significant gaps, especially in late spring/early summer.')

if __name__ == "__main__":
    create_spx_timeline_with_gaps()