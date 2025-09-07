import pandas as pd
import glob
import os
from datetime import datetime
import re

def extract_date_from_filename(filename):
    """Extract date from filename like spx_0dte_calls_20250309_2055.csv"""
    match = re.search(r'(\d{8})', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y%m%d').date()
    return None

def extract_option_type(filename):
    """Extract option type (calls/puts) from filename"""
    if 'calls' in filename:
        return 'call'
    elif 'puts' in filename:
        return 'put'
    return None

def load_and_process_dataset():
    """Load all CSV files and concatenate them into one dataset"""
    print("Loading SPX 0DTE options dataset...")
    
    # Get all CSV files
    csv_files = glob.glob('dataset/*.csv')
    print(f"Found {len(csv_files)} CSV files")
    
    dataframes = []
    
    for file in csv_files:
        try:
            # Extract metadata from filename
            date = extract_date_from_filename(file)
            option_type = extract_option_type(file)
            
            # Read CSV
            df = pd.read_csv(file)
            
            # Add metadata columns
            df['date'] = date
            df['option_type'] = option_type
            df['filename'] = os.path.basename(file)
            
            dataframes.append(df)
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Clean and process data
    print(f"Combined dataset shape: {combined_df.shape}")
    print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    print(f"Option types: {combined_df['option_type'].value_counts()}")
    
    return combined_df

def analyze_dataset(df):
    """Basic analysis of the dataset"""
    print("\n=== Dataset Analysis ===")
    print(f"Total rows: {len(df):,}")
    print(f"Total unique dates: {df['date'].nunique()}")
    print(f"Average SPX close: ${df['spx_close'].mean():.2f}")
    print(f"SPX range: ${df['spx_close'].min():.2f} - ${df['spx_close'].max():.2f}")
    print(f"Average VIX: {df['vix_close'].mean():.2f}")
    print(f"VIX range: {df['vix_close'].min():.2f} - {df['vix_close'].max():.2f}")
    print(f"Total volume: {df['volume'].sum():,}")
    print(f"Total open interest: {df['openInterest'].sum():,}")
    
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nMissing values:")
    print(df.isnull().sum())

if __name__ == "__main__":
    # Load and process dataset
    df = load_and_process_dataset()
    
    # Save combined dataset to root directory
    df.to_csv('spx_0dte_combined.csv', index=False)
    print(f"\nSaved combined dataset to 'spx_0dte_combined.csv'")
    
    # Analyze dataset
    analyze_dataset(df)