import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def get_project_root():
    """Returns project root path by navigating up from the script location."""
    # Assuming script is in analysis/scripts/
    return Path(__file__).resolve().parent.parent.parent

def load_data(data_path):
    """Robustly load data, handling the case where an Excel file has a .csv extension."""
    try:
        # First try as standard CSV
        print(f"Attempting to read {data_path} as CSV...")
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Failed to read as CSV ({e}). Trying as Excel file...")
        try:
            # Fallback to Excel if it's actually an XLSX file disguised as CSV
            # This is common if someone manually renames .xlsx to .csv
            df = pd.read_excel(data_path)
            return df
        except Exception as excel_error:
            print(f"Failed to read as Excel ({excel_error}).")
            raise ValueError(f"Could not read the data file: {data_path}")

def analyze_budgets():
    # Setup paths
    root_dir = get_project_root()
    data_path = root_dir / 'data' / 'data.csv'
    outputs_dir = root_dir / 'outputs'
    
    # Ensure outputs directory exists
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("Loading data...")
    try:
        df = load_data(data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
        
    print(f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns.")
    
    # Identify budget-related columns (case-insensitive)
    budget_keywords = ['budget', 'subsidy', 'subsidies', 'cost', 'expense', 'expenditure', 'funding', 'amount', 'investment']
    
    # Find columns that match keywords AND are numeric
    budget_cols = [
        col for col in df.columns 
        if any(kw in str(col).lower() for kw in budget_keywords) 
        and pd.api.types.is_numeric_dtype(df[col])
    ]
    
    # If no specific budget columns are found, fall back to all numeric columns
    if not budget_cols:
        print("\nNo explicitly named budget columns found (e.g., 'budget', 'subsidy').")
        print("Falling back to all numeric columns for financial analysis.")
        budget_cols = df.select_dtypes(include=['number']).columns.tolist()
        
    if not budget_cols:
        print("Error: No numeric columns found in the dataset to perform budget analysis.")
        return

    print(f"\nAnalyzing the following columns as budgets/financials:\n{budget_cols}\n")

    # 1. Summary Statistics
    print("Generating summary statistics...")
    summary_stats = df[budget_cols].describe()
    
    # Save summary stats
    summary_path = outputs_dir / 'budget_summary_statistics.csv'
    summary_stats.to_csv(summary_path)
    print(f"Saved summary statistics to {summary_path}")
    
    # 2. Visualizations
    sns.set_theme(style="whitegrid")
    
    for col in budget_cols:
        print(f"Generating distribution plot for {col}...")
        # Create a figure with 2 subplots: a histogram and a boxplot
        fig, (ax_box, ax_hist) = plt.subplots(
            2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)}, figsize=(10, 6)
        )
        
        # Drop missing values for plotting
        plot_data = df[col].dropna()
        
        if len(plot_data) == 0:
            print(f"Skipping plot for {col} because it contains no valid data.")
            plt.close()
            continue
            
        # Add boxplot
        sns.boxplot(x=plot_data, ax=ax_box, color="lightblue")
        ax_box.set(xlabel='') # Remove x label for the boxplot
        ax_box.set_title(f'Distribution of {col}', fontsize=14)
        
        # Add histogram
        sns.histplot(data=plot_data, ax=ax_hist, kde=True, color="steelblue", bins=30)
        ax_hist.set(xlabel=col, ylabel='Frequency')
        
        # Save figure
        clean_col_name = "".join([c if c.isalnum() else "_" for c in str(col)])
        plot_path = outputs_dir / f'budget_distribution_{clean_col_name}.png'
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"Saved plot to {plot_path}")
        
    # Optional: Correlation matrix if multiple budget columns exist
    if len(budget_cols) > 1:
        print("\nGenerating correlation matrix...")
        plt.figure(figsize=(10, 8))
        corr_matrix = df[budget_cols].corr()
        
        # Plot heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
        plt.title('Correlation Matrix of Budget/Financial Variables')
        plt.tight_layout()
        
        # Save correlation matrix
        corr_path = outputs_dir / 'budget_correlation_matrix.png'
        plt.savefig(corr_path, dpi=300)
        plt.close()
        print(f"Saved correlation matrix plot to {corr_path}")

    print("\n✅ Budget analysis completed successfully.")
    print(f"All outputs are saved in: {outputs_dir}")

if __name__ == "__main__":
    analyze_budgets()
