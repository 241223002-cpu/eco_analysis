import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

def get_project_root():
    return Path(__file__).resolve().parent.parent.parent

def main():
    root = get_project_root()
    data_path = root / 'data' / 'green_bond' / 'green-bond-issuances.csv'
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading green bond data...")
    df = pd.read_csv(data_path, sep=';')
    
    # Filter for Kazakhstan
    kz_data = df[df['Country'] == 'Kazakhstan, Rep. of'].copy()
    
    if kz_data.empty:
        print("No data found for Kazakhstan.")
        return
        
    # Convert values to millions for easier readability (currently in Billions)
    kz_data['Value_Millions'] = kz_data['Value'] * 1000
    
    # Sort by year
    kz_data = kz_data.sort_values('Year')
    
    # Set the style
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams['figure.figsize'] = (10, 6)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define colors based on Bond Type
    palette = {'Green Bonds': '#2ecc71', 'Sustainability Bond': '#3498db'}
    
    sns.barplot(data=kz_data, x='Year', y='Value_Millions', hue='Bond_Type', palette=palette, dodge=False, ax=ax)
    
    # Add data labels on top of bars
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f"${p.get_height():.1f}M", 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        xytext=(0, 5), textcoords='offset points',
                        fontweight='bold')
    
    ax.set_title('Kazakhstan: Green & Sustainability Bond Issuance Volume', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Issuance Volume (Million USD)', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    
    # Fix legend
    plt.legend(title='Bond Type', loc='upper left')
    
    sns.despine()
    plt.tight_layout()
    
    plot_out = out_dir / 'kz_green_bond_issuance.png'
    plt.savefig(plot_out, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved plot: {plot_out.name}")

if __name__ == '__main__':
    main()
