import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_single_day_calls():
    """Analyze call options pricing structure for a single day"""
    
    # Load the dataset
    print("Loading SPX 0DTE options dataset...")
    df = pd.read_csv('dataset/processed/spx_0dte_combined.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Get available dates and select a representative one
    available_dates = sorted(df['date'].unique())
    print(f"Available dates: {len(available_dates)} days")
    print(f"First date: {available_dates[0].strftime('%Y-%m-%d')}")
    print(f"Last date: {available_dates[-1].strftime('%Y-%m-%d')}")
    
    # Select a date from the middle of the dataset for analysis
    middle_idx = len(available_dates) // 2
    selected_date = available_dates[middle_idx]
    
    print(f"\nSelected date for analysis: {selected_date.strftime('%Y-%m-%d')}")
    
    # Filter data for the selected date and calls only
    day_data = df[(df['date'] == selected_date) & (df['option_type'] == 'call')].copy()
    day_data = day_data.sort_values('strike')
    
    # Get SPX close price for this date
    spx_price = day_data['spx_close'].iloc[0]
    print(f"SPX close price: ${spx_price:.2f}")
    print(f"Number of call options: {len(day_data)}")
    
    # Calculate moneyness and other metrics
    day_data['moneyness'] = (day_data['strike'] - spx_price) / spx_price
    day_data['intrinsic_value'] = np.maximum(spx_price - day_data['strike'], 0)
    day_data['time_value'] = day_data['lastPrice'] - day_data['intrinsic_value']
    
    print(f"Strike range: ${day_data['strike'].min():.0f} - ${day_data['strike'].max():.0f}")
    print(f"Moneyness range: {day_data['moneyness'].min():.1%} to {day_data['moneyness'].max():.1%}")
    
    # Create comprehensive visualization with space for table
    fig = plt.figure(figsize=(18, 18))
    
    # Create subplots with proper spacing to avoid overlaps
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.2], hspace=0.4, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1]) 
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])
    
    # 1. Option Prices vs Strike
    ax1.plot(day_data['strike'], day_data['lastPrice'], 'bo-', linewidth=2, markersize=4)
    ax1.axvline(x=spx_price, color='red', linestyle='--', linewidth=2, label=f'SPX Close: ${spx_price:.0f}')
    ax1.set_xlabel('Strike Price ($)')
    ax1.set_ylabel('Call Option Price ($)')
    ax1.set_title(f'Call Option Prices vs Strike Price\n{selected_date.strftime("%Y-%m-%d")}')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Intrinsic vs Time Value
    width = day_data['strike'].iloc[1] - day_data['strike'].iloc[0] if len(day_data) > 1 else 5
    ax2.bar(day_data['strike'], day_data['intrinsic_value'], width=width*0.4, 
            alpha=0.7, label='Intrinsic Value', color='orange')
    ax2.bar(day_data['strike'], day_data['time_value'], width=width*0.4,
            bottom=day_data['intrinsic_value'], alpha=0.7, label='Time Value', color='green')
    ax2.axvline(x=spx_price, color='red', linestyle='--', linewidth=2, label=f'SPX Close')
    ax2.set_xlabel('Strike Price ($)')
    ax2.set_ylabel('Value ($)')
    ax2.set_title('Intrinsic Value vs Time Value')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Implied Volatility Smile
    ax3.plot(day_data['moneyness'], day_data['impliedVolatility'], 'go-', linewidth=2, markersize=4)
    ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, label='ATM')
    ax3.set_xlabel('Moneyness (Strike-Spot)/Spot')
    ax3.set_ylabel('Implied Volatility')
    ax3.set_title('Implied Volatility Smile')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Volume vs Strike
    ax4.bar(day_data['strike'], day_data['volume'], width=width*0.6, alpha=0.7, color='purple')
    ax4.axvline(x=spx_price, color='red', linestyle='--', linewidth=2, label=f'SPX Close')
    ax4.set_xlabel('Strike Price ($)')
    ax4.set_ylabel('Volume')
    ax4.set_title('Trading Volume by Strike')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Create data table at the bottom
    ax_table = fig.add_subplot(gs[2, :])  # Span both columns for the table
    ax_table.axis('off')
    
    # Prepare table data - select key columns and format
    table_data = day_data[['strike', 'lastPrice', 'volume', 'impliedVolatility', 
                          'bid', 'ask', 'openInterest', 'moneyness', 'intrinsic_value', 'time_value']].copy()
    
    # Format the data for display
    table_display = []
    headers = ['Strike', 'Last Price', 'Volume', 'IV', 'Bid', 'Ask', 'OI', 'Moneyness', 'Intrinsic', 'Time Val']
    
    for _, row in table_data.iterrows():
        formatted_row = [
            f"${row['strike']:.0f}",
            f"${row['lastPrice']:.2f}",
            f"{row['volume']:,.0f}",
            f"{row['impliedVolatility']:.1%}",
            f"${row['bid']:.2f}",
            f"${row['ask']:.2f}",
            f"{row['openInterest']:,.0f}",
            f"{row['moneyness']:.1%}",
            f"${row['intrinsic_value']:.2f}",
            f"${row['time_value']:.2f}"
        ]
        table_display.append(formatted_row)
    
    # Create the table
    table = ax_table.table(cellText=table_display,
                          colLabels=headers,
                          cellLoc='center',
                          loc='center',
                          bbox=[0, 0, 1, 1])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    
    # Color ATM rows (moneyness close to 0)
    for i, row in enumerate(table_data.itertuples()):
        if abs(row.moneyness) < 0.01:  # ATM options
            for j in range(len(headers)):
                table[(i+1, j)].set_facecolor('#ffeeee')  # Light red for ATM
    
    # Color header
    for j in range(len(headers)):
        table[(0, j)].set_facecolor('#e6f3ff')  # Light blue for header
        table[(0, j)].set_text_props(weight='bold')
    
    # Add summary statistics
    fig.text(0.02, 1, f'''Analysis Date: {selected_date.strftime("%Y-%m-%d")}
SPX Close: ${spx_price:.2f}  |  Call Options: {len(day_data)}  |  Strike Range: ${day_data['strike'].min():.0f}-${day_data['strike'].max():.0f}
ATM Options: {len(day_data[abs(day_data['moneyness']) < 0.01])}  |  ITM: {len(day_data[day_data['moneyness'] < 0])}  |  OTM: {len(day_data[day_data['moneyness'] > 0])}''', 
             fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    plt.savefig('visualizations/03_single_day_calls_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\nCall options analysis saved as 'visualizations/03_single_day_calls_analysis.png'")
    
    # Print detailed analysis
    print(f"\n=== CALL OPTIONS PRICING ANALYSIS ===")
    print(f"Date: {selected_date.strftime('%Y-%m-%d')}")
    print(f"SPX Close: ${spx_price:.2f}")
    print(f"Total Call Options: {len(day_data)}")
    
    # ATM analysis
    atm_options = day_data[abs(day_data['moneyness']) < 0.01]
    if len(atm_options) > 0:
        print(f"\nATM Options (within 1% of SPX):")
        for _, opt in atm_options.iterrows():
            print(f"  Strike ${opt['strike']:.0f}: Price ${opt['lastPrice']:.2f}, IV {opt['impliedVolatility']:.1%}")
    
    # Price breakdown
    itm_count = len(day_data[day_data['moneyness'] < 0])
    otm_count = len(day_data[day_data['moneyness'] > 0])
    print(f"\nMoneyness Breakdown:")
    print(f"  ITM (In-the-Money): {itm_count} options")
    print(f"  OTM (Out-of-the-Money): {otm_count} options")
    
    # Highest volume strikes
    top_volume = day_data.nlargest(3, 'volume')
    print(f"\nHighest Volume Strikes:")
    for _, opt in top_volume.iterrows():
        print(f"  Strike ${opt['strike']:.0f}: {opt['volume']:,} contracts (${opt['lastPrice']:.2f})")

if __name__ == "__main__":
    analyze_single_day_calls()