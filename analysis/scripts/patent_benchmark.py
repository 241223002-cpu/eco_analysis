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
    data_path = root / 'data' / 'cleaned' / 'patents_clean.csv'
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading patents data for benchmarking...")
    df = pd.read_csv(data_path)
    
    # Filter for Patent applications to measure innovation intent/activity
    df_apps = df[df['Measure'] == 'Patent applications'].copy()
    
    # Aggregate across patent authorities to get total environment-related applications per country per year
    df_agg = df_apps.groupby(['Country', 'Year'])['Patents'].sum().reset_index()
    
    # Check if Kazakhstan is in the dataset
    if 'Kazakhstan' not in df_agg['Country'].unique():
        print("Kazakhstan not found in the patents dataset. Available countries:")
        print(df_agg['Country'].unique())
        return
        
    print("Found Kazakhstan. Preparing benchmark groups...")
    
    # Define benchmark countries
    # 1. Transition/Emerging Economies
    emerging_peers = ['Chile', 'Mexico', 'Poland', 'Turkey', 'Hungary', 'Czechia', 'Colombia']
    # Ensure they exist in data
    emerging_peers = [c for c in emerging_peers if c in df_agg['Country'].unique()]
    
    # 2. Regional/Global Leaders (just for scale context, though they will dwarf KZ)
    leaders = ['Germany', 'Japan', 'United States']
    leaders = [c for c in leaders if c in df_agg['Country'].unique()]
    
    # ---- PLOT 1: Kazakhstan vs Emerging Peers (Time Series) ----
    plt.figure(figsize=(12, 7))
    sns.set_theme(style="whitegrid", context="talk")
    
    countries_to_plot_1 = ['Kazakhstan'] + emerging_peers
    plot_data_1 = df_agg[df_agg['Country'].isin(countries_to_plot_1)]
    
    sns.lineplot(data=plot_data_1, x='Year', y='Patents', hue='Country', 
                 linewidth=2.5, marker='o')
    
    # Highlight Kazakhstan
    kz_data = plot_data_1[plot_data_1['Country'] == 'Kazakhstan']
    plt.plot(kz_data['Year'], kz_data['Patents'], color='red', linewidth=4, marker='D', markersize=8, label='_nolegend_')
    
    plt.title('Green Patent Applications: Kazakhstan vs. Emerging Economies', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Total Patent Applications (Units)')
    plt.xlabel('Year')
    plt.xticks(plot_data_1['Year'].unique(), rotation=45)
    
    # Put legend outside
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    
    out_1 = out_dir / 'patent_benchmark_emerging.png'
    plt.savefig(out_1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_1.name}")
    
    # ---- PLOT 2: Kazakhstan's Internal Trend (Applications vs Grants) ----
    plt.figure(figsize=(10, 6))
    df_kz = df[df['Country'] == 'Kazakhstan'].groupby(['Year', 'Measure'])['Patents'].sum().reset_index()
    
    sns.barplot(data=df_kz, x='Year', y='Patents', hue='Measure', palette='Set2')
    
    plt.title('Kazakhstan: Green Patent Applications vs. Grants', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Patent Units')
    plt.xlabel('Year')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    out_2 = out_dir / 'patent_kz_internal_trend.png'
    plt.savefig(out_2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_2.name}")
    
    # ---- PLOT 3: Total Cumulative Green Patents (Bar Chart) ----
    plt.figure(figsize=(12, 8))
    
    # Calculate cumulative sums over the period
    all_selected = ['Kazakhstan'] + emerging_peers + leaders[:2] # Include a couple leaders for scale
    df_cum = df_agg[df_agg['Country'].isin(all_selected)].groupby('Country')['Patents'].sum().reset_index()
    df_cum = df_cum.sort_values('Patents', ascending=False)
    
    # Apply log scale if leaders are included because they skew it heavily
    # Or plot without leaders for better visibility of the lower end
    df_cum_emerging = df_agg[df_agg['Country'].isin(['Kazakhstan'] + emerging_peers)].groupby('Country')['Patents'].sum().reset_index()
    df_cum_emerging = df_cum_emerging.sort_values('Patents', ascending=False)
    
    colors = ['red' if c == 'Kazakhstan' else '#3498db' for c in df_cum_emerging['Country']]
    
    sns.barplot(data=df_cum_emerging, x='Patents', y='Country', palette=colors)
    
    plt.title(f'Cumulative Green Patent Applications (2009-{df_agg["Year"].max()})\nEmerging Economies Benchmark', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Total Cumulative Patent Applications')
    plt.ylabel('')
    
    for i, v in enumerate(df_cum_emerging['Patents']):
        plt.text(v + (df_cum_emerging['Patents'].max()*0.01), i, f'{int(v)}', va='center')
        
    sns.despine()
    plt.tight_layout()
    out_3 = out_dir / 'patent_cumulative_benchmark.png'
    plt.savefig(out_3, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_3.name}")
    
    # Save statistics for artifact
    kz_stats = df_agg[df_agg['Country'] == 'Kazakhstan']
    stats_out = out_dir / 'patent_kz_stats.csv'
    kz_stats.to_csv(stats_out, index=False)
    
    print("\nPatent benchmark analysis complete.")

if __name__ == '__main__':
    main()
