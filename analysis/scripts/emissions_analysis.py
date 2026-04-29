import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

def get_project_root():
    return Path(__file__).resolve().parent.parent.parent

def group_sector(sector):
    if 'Electricity' in sector: return 'Energy Production'
    if 'Manufacturing' in sector: return 'Manufacturing'
    if 'Mining' in sector: return 'Mining'
    if 'Transportation' in sector: return 'Transportation'
    if 'Agriculture' in sector: return 'Agriculture'
    if 'Activities by households' in sector: return 'Households'
    if 'Construction' in sector: return 'Construction'
    return 'Services & Other'

def main():
    root = get_project_root()
    data_path = root / 'data' / 'cleaned' / 'air_emissions_clean.csv'
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading air emissions data...")
    df = pd.read_csv(data_path)
    
    # We want to drop the aggregate rows if any exist. Total usually isn't here since we only parsed data after the 'Total' row, 
    # but let's make sure 'Total' isn't in sector names
    df = df[~df['Sector'].str.contains('Total', case=False, na=False)].copy()
    
    # Apply broader groupings
    df['Broad_Sector'] = df['Sector'].apply(group_sector)
    
    # Aggregate by Year and Broad_Sector
    df_agg = df.groupby(['Year', 'Broad_Sector'])['CO2_Emissions_Tonnes'].sum().reset_index()
    
    # Convert tonnes to millions of tonnes for readability
    df_agg['CO2_Mt'] = df_agg['CO2_Emissions_Tonnes'] / 1_000_000
    
    # Pivot for stacked area chart
    pivot_df = df_agg.pivot(index='Year', columns='Broad_Sector', values='CO2_Mt').fillna(0)
    
    # Sort columns by total emissions to put the largest at the bottom
    col_order = pivot_df.sum().sort_values(ascending=False).index
    pivot_df = pivot_df[col_order]
    
    # ---- PLOT 1: Stacked Area Chart (Emissions Evolution) ----
    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(14, 8))
    
    # Use a nice color palette
    colors = sns.color_palette("Set2", n_colors=len(col_order))
    
    plt.stackplot(pivot_df.index, [pivot_df[col] for col in pivot_df.columns], labels=pivot_df.columns, colors=colors, alpha=0.85)
    
    plt.title('Evolution of CO₂ Emissions in Kazakhstan by Sector (2010-2019)', fontsize=18, fontweight='bold', pad=20)
    plt.ylabel('CO₂ Emissions (Million Tonnes)', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.xticks(pivot_df.index, rotation=0)
    
    # Reverse legend order to match stack
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1], loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12)
    
    sns.despine()
    plt.tight_layout()
    out_1 = out_dir / 'emissions_stacked_area.png'
    plt.savefig(out_1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_1.name}")
    
    # ---- PLOT 2: Pie Charts for Each Year ----
    years = sorted(df_agg['Year'].unique())
    
    for year in years:
        df_year = df_agg[df_agg['Year'] == year].sort_values('CO2_Mt', ascending=False)
        
        plt.figure(figsize=(10, 8))
        
        # Create an explosion for the largest slice to highlight it
        explode = [0.05 if i == 0 else 0 for i in range(len(df_year))]
        
        plt.pie(df_year['CO2_Mt'], labels=df_year['Broad_Sector'], autopct='%1.1f%%', 
                startangle=140, colors=colors, explode=explode, shadow=False, 
                textprops={'fontsize': 11})
        
        plt.title(f'Share of CO₂ Emissions by Sector ({year})', fontsize=18, fontweight='bold', pad=20)
        
        plt.tight_layout()
        out_year = out_dir / f'emissions_pie_{year}.png'
        plt.savefig(out_year, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved {out_year.name}")
        
    # Save statistics for artifact (keep latest year stats)
    latest_year = years[-1]
    df_latest = df_agg[df_agg['Year'] == latest_year].sort_values('CO2_Mt', ascending=False)
    stats_out = out_dir / 'emissions_latest_stats.csv'
    df_latest.to_csv(stats_out, index=False)
    
    print("\nAir emissions analysis complete.")

if __name__ == '__main__':
    main()
