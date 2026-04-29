import pandas as pd
import numpy as np
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
    
    print("Loading green growth data for decoupling analysis...")
    df = pd.read_csv(data_path)
    
    # 1. Extract Real GDP and CO2 Emissions
    gdp_measure = 'Real GDP 1'
    co2_measure = 'Production-based CO2 emissions 2'
    
    gdp_df = df[df['Measure'] == gdp_measure].groupby('Year')['Value'].mean().reset_index()
    co2_df = df[df['Measure'] == co2_measure].groupby('Year')['Value'].mean().reset_index()
    
    if gdp_df.empty or co2_df.empty:
        print("Error: Could not find required GDP or CO2 measures in the data.")
        # Fallback to per capita if absolute is missing
        gdp_df = df[df['Measure'] == 'Real GDP per capita 1'].groupby('Year')['Value'].mean().reset_index()
        co2_df = df[df['Measure'] == 'Production-based CO2 intensity, energy-related CO2 per capita 2'].groupby('Year')['Value'].mean().reset_index()
        gdp_measure = 'Real GDP per capita 1'
        co2_measure = 'Production-based CO2 intensity, energy-related CO2 per capita 2'
        
    print(f"Using GDP: {gdp_measure}")
    print(f"Using CO2: {co2_measure}")
    
    # Merge and calculate base indices (2009 = 100)
    merged = pd.merge(gdp_df, co2_df, on='Year', suffixes=('_GDP', '_CO2'))
    merged = merged.sort_values('Year').dropna()
    
    base_year = merged['Year'].min()
    base_gdp = merged[merged['Year'] == base_year]['Value_GDP'].values[0]
    base_co2 = merged[merged['Year'] == base_year]['Value_CO2'].values[0]
    
    merged['GDP_Index'] = (merged['Value_GDP'] / base_gdp) * 100
    merged['CO2_Index'] = (merged['Value_CO2'] / base_co2) * 100
    
    # Calculate Year-over-Year % changes for Tapio Index
    merged['GDP_pct_change'] = merged['Value_GDP'].pct_change() * 100
    merged['CO2_pct_change'] = merged['Value_CO2'].pct_change() * 100
    
    # Tapio Decoupling Elasticity
    merged['Tapio_Elasticity'] = merged['CO2_pct_change'] / merged['GDP_pct_change']
    
    def categorize_decoupling(row):
        gdp_g = row['GDP_pct_change']
        co2_g = row['CO2_pct_change']
        e = row['Tapio_Elasticity']
        
        if pd.isna(e):
            return "Base Year"
        
        if gdp_g > 0:
            if co2_g < 0:
                return "Strong Decoupling"
            elif 0 <= e < 0.8:
                return "Weak Decoupling"
            elif 0.8 <= e <= 1.2:
                return "Expansive Coupling"
            else:
                return "Expansive Negative Decoupling"
        else: # GDP decline
            if co2_g < 0 and e > 1.2:
                return "Strong Negative Decoupling"
            elif co2_g < 0 and 0.8 <= e <= 1.2:
                return "Recessive Coupling"
            elif co2_g < 0 and 0 <= e < 0.8:
                return "Weak Negative Decoupling"
            else:
                return "Strong Negative Decoupling"
                
    merged['Decoupling_State'] = merged.apply(categorize_decoupling, axis=1)
    
    # Save the decoupling data
    csv_out = out_dir / 'decoupling_analysis.csv'
    merged.to_csv(csv_out, index=False)
    print(f"Saved decoupling data to {csv_out.name}")
    
    # 2. Plotting the Decoupling Trends (Indexed to Base Year)
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(merged['Year'], merged['GDP_Index'], marker='o', linewidth=3, color='#2ecc71', label='Real GDP')
    ax.plot(merged['Year'], merged['CO2_Index'], marker='s', linewidth=3, color='#e74c3c', label='CO2 Emissions')
    
    # Highlight the gap (decoupling)
    ax.fill_between(merged['Year'], merged['GDP_Index'], merged['CO2_Index'], 
                    where=(merged['GDP_Index'] > merged['CO2_Index']), 
                    interpolate=True, color='green', alpha=0.1, label='Decoupling Gap')
                    
    ax.set_title('Decoupling of Economic Growth from CO2 Emissions in Kazakhstan', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(f'Index ({base_year} = 100)', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    
    plt.xticks(merged['Year'].unique(), rotation=45)
    ax.legend(loc='upper left', frameon=True, fontsize=11)
    
    ax.grid(True, linestyle='--', alpha=0.7)
    sns.despine()
    
    plt.tight_layout()
    plot_out = out_dir / 'decoupling_trend.png'
    plt.savefig(plot_out, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved decoupling plot to {plot_out.name}")
    
    # 3. Create a Bar chart of Tapio Elasticity
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    plot_data = merged.dropna(subset=['Tapio_Elasticity']).copy()
    
    # Color code by state
    color_map = {
        'Strong Decoupling': '#2ecc71',      # Green
        'Weak Decoupling': '#f1c40f',        # Yellow
        'Expansive Coupling': '#e67e22',     # Orange
        'Expansive Negative Decoupling': '#e74c3c', # Red
        'Strong Negative Decoupling': '#c0392b',
        'Recessive Coupling': '#7f8c8d',
        'Weak Negative Decoupling': '#95a5a6',
        'Base Year': 'gray'
    }
    colors = plot_data['Decoupling_State'].map(color_map).tolist()
    
    bars = ax2.bar(plot_data['Year'].astype(str), plot_data['Tapio_Elasticity'], color=colors)
    
    # Add horizontal lines for thresholds
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.axhline(y=0.8, color='gray', linestyle='--', alpha=0.5, label='Weak Decoupling Threshold (0.8)')
    ax2.axhline(y=1.2, color='gray', linestyle=':', alpha=0.5, label='Coupling Threshold (1.2)')
    
    ax2.set_title('Tapio Decoupling Elasticity by Year', fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('Elasticity (ΔCO2 / ΔGDP)', fontsize=12)
    
    # Add custom legend for states
    import matplotlib.patches as mpatches
    unique_states = plot_data['Decoupling_State'].unique()
    legend_patches = [mpatches.Patch(color=color_map[state], label=state) for state in unique_states]
    ax2.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    
    sns.despine()
    plt.tight_layout()
    bar_out = out_dir / 'decoupling_tapio_elasticity.png'
    plt.savefig(bar_out, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved Tapio elasticity plot to {bar_out.name}")
    print("\nDecoupling analysis complete.")

if __name__ == '__main__':
    main()
