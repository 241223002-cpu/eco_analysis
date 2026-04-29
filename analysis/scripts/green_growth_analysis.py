import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

def get_project_root():
    return Path(__file__).resolve().parent.parent.parent

def main():
    root = get_project_root()
    data_path = root / 'data' / 'cleaned' / 'green_growth_clean.csv'
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading green growth data...")
    df = pd.read_csv(data_path)
    
    # We want to focus on Kazakhstan overall ("Total - all activities" or similar general sections)
    # Actually in Green Growth, we have 'Section' and 'Measure'. Let's see what Sections exist.
    # For now, we will just filter by Measure, and if there are multiple sections, we take the main one.
    
    # Set the style for modern aesthetic
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.family'] = 'sans-serif'
    
    metrics_to_plot = {
        'CO2_Productivity': 'Production-based CO2 productivity, GDP per unit of energy-related CO2 emissions 2',
        'Energy_Productivity': 'Energy productivity, GDP per unit of TES 1',
        'Environment_Tax_Revenue': 'Environment related tax revenue 2',
        'Green_Patents_Inventions': 'Development of environment-related technologies 3',
        'Renewable_Electricity': 'Renewable electricity generation 2',
        'Real_GDP_per_Capita': 'Real GDP per capita 1'
    }
    
    for short_name, measure_name in metrics_to_plot.items():
        sub_df = df[df['Measure'] == measure_name].copy()
        
        if sub_df.empty:
            print(f"Skipping {short_name}: no data found.")
            continue
            
        # Group by Year and take mean in case of duplicate sections
        grouped = sub_df.groupby('Year').agg({'Value': 'mean', 'Unit': 'first'}).reset_index()
        grouped = grouped.sort_values('Year')
        
        if grouped.empty or grouped['Value'].isna().all():
            print(f"Skipping {short_name}: all values are NaN.")
            continue
            
        unit = grouped['Unit'].iloc[0]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot with a nice marker and line
        sns.lineplot(
            data=grouped, 
            x='Year', 
            y='Value', 
            marker='o', 
            markersize=8,
            linewidth=2.5,
            color='#2ecc71' if 'Green' in short_name or 'CO2' in short_name or 'Renewable' in short_name else '#3498db',
            ax=ax
        )
        
        # Fill area under the curve slightly for aesthetics
        ax.fill_between(grouped['Year'], grouped['Value'], alpha=0.1, 
                       color='#2ecc71' if 'Green' in short_name or 'CO2' in short_name or 'Renewable' in short_name else '#3498db')
        
        # Titles and labels
        clean_title = short_name.replace('_', ' ')
        ax.set_title(f'Kazakhstan: {clean_title} (2009-2025)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=12)
        
        # Format Y axis label intelligently
        ax.set_ylabel(unit, fontsize=11)
        
        # Ensure integer years on x-axis
        plt.xticks(grouped['Year'].unique(), rotation=45)
        
        # Add grid and clean spines
        ax.grid(True, linestyle='--', alpha=0.7)
        sns.despine()
        
        plt.tight_layout()
        out_file = out_dir / f'green_growth_{short_name}.png'
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved plot: {out_file.name}")
        
    print("\nAll Green Growth trend plots generated successfully.")

if __name__ == '__main__':
    main()
