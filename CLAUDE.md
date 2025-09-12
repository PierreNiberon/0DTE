# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based SPX 0DTE (zero days to expiration) options analysis project that processes, analyzes, and visualizes S&P 500 options trading data. The project focuses on creating comprehensive 2D and 3D visualizations to understand options pricing patterns, implied volatility surfaces, and market dynamics.

## Environment Setup

**Virtual Environment**: The project uses a Python virtual environment located at `venv/`. Always activate it before running scripts:
```bash
source venv/bin/activate  # On Linux/Mac
```

**Python Version**: Python 3.12.3 is used with key data science packages:
- pandas (data manipulation)
- numpy (numerical computing)  
- matplotlib (2D plotting)
- plotly (interactive 3D visualizations)
- seaborn (statistical visualization)

## Project Structure

```
├── dataset/
│   ├── source/          # Raw CSV files (spx_0dte_calls_YYYYMMDD_2055.csv format)
│   └── processed/       # Combined dataset (spx_0dte_combined.csv)
├── scripts/             # All analysis and visualization scripts
├── visualizations/      # Generated plots and HTML files
└── venv/               # Python virtual environment
```

## Key Scripts and Workflow

### Data Processing Pipeline
1. **`scripts/process_data.py`** - Combines individual CSV files from `dataset/source/` into a single processed dataset
   - Extracts dates and option types from filenames
   - Combines all data into `dataset/processed/spx_0dte_combined.csv`

### Analysis and Visualization
2. **`scripts/analyze_data.py`** - Comprehensive statistical analysis with 2D visualizations
   - Uses `SPXOptionsAnalyzer` class
   - Generates 12-panel analysis chart saved as PNG
   - Provides summary statistics and options flow analysis

3. **`scripts/visualize_3d.py`** - Static 3D matplotlib visualizations  
   - Uses `SPX3DVisualizer` class
   - Creates price and IV surfaces for calls/puts
   - Saves PNG files with matplotlib

4. **`scripts/interactive_3d.py`** - Interactive Plotly 3D visualizations
   - Uses `SPXInteractive3D` class
   - Creates rotatable HTML visualizations
   - Includes moneyness-based surfaces

5. **`scripts/spx_based_3d.py`** - Advanced SPX-referenced 3D visualizations
   - Uses `SPXBased3D` class
   - Shows options "floating" above SPX baseline
   - Creates wide-format visualizations optimized for analysis

## Common Development Commands

**Run data processing:**
```bash
cd /home/pierre/Documents/projets/0dte
source venv/bin/activate
python scripts/process_data.py
```

**Generate complete analysis:**
```bash
python scripts/analyze_data.py  # 2D analysis and charts
python scripts/visualize_3d.py  # Static 3D surfaces  
python scripts/interactive_3d.py  # Interactive 3D HTML
python scripts/spx_based_3d.py  # SPX-referenced 3D
```

**Check generated outputs:**
```bash
ls -la visualizations/  # View all generated visualizations
```

## Data Structure

The processed dataset (`spx_0dte_combined.csv`) contains:
- **Core fields**: date, option_type (call/put), strike, lastPrice, volume, openInterest
- **Market data**: spx_close, vix_close (SPX and VIX closing prices)
- **Option metrics**: impliedVolatility, bid, ask, inTheMoney
- **Derived fields**: Added by analysis scripts (moneyness, bid_ask_spread, etc.)

## Architecture Notes

**Class-based Design**: Each script uses a main class (e.g., `SPXOptionsAnalyzer`, `SPX3DVisualizer`) that:
- Loads data in `__init__()` 
- Provides multiple visualization/analysis methods
- Handles data preprocessing and calculations internally

**Output Organization**: 
- PNG files for static charts
- HTML files for interactive Plotly visualizations  
- All outputs saved to `visualizations/` directory

**Performance Considerations**:
- Scripts use sampling (e.g., `sample_every=3`) for 3D visualizations to manage performance
- Date filtering available in most visualization methods
- Large dataset (~730K records) requires memory-conscious processing

## Development Workflow

1. **Data Updates**: Add new CSV files to `dataset/source/` and run `process_data.py`
2. **Analysis**: Run `analyze_data.py` for overview statistics and patterns
3. **3D Exploration**: Use interactive scripts for detailed surface analysis
4. **Custom Analysis**: Extend existing classes or create new analysis methods

The project is focused on financial market analysis and visualization, not general software development, so there are no traditional build/test/lint commands.