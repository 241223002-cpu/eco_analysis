import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
import os

def get_project_root():
    return Path(__file__).resolve().parent.parent.parent

def main():
    root = get_project_root()
    data_dir = root / 'data' / 'cleaned'
    out_dir = root / 'outputs'
    
    # 1. Load Data
    decoupling = pd.read_csv(out_dir / 'decoupling_analysis.csv')
    green_growth = pd.read_csv(data_dir / 'green_growth_clean.csv')
    patents = pd.read_csv(data_dir / 'patents_clean.csv')
    
    # 2. Prepare Variables per year (2009-2024)
    # A. Decoupling & Emissions
    df_reg = decoupling[['Year', 'Value_GDP', 'Value_CO2', 'Tapio_Elasticity']].copy()
    
    # B. Green Growth Variables
    # Energy Productivity
    ep_df = green_growth[green_growth['Measure'] == 'Energy productivity, GDP per unit of TES 1']
    ep_yearly = ep_df.groupby('Year')['Value'].mean().rename('Energy_Productivity')
    
    # Renewable Electricity
    ren_df = green_growth[green_growth['Measure'] == 'Renewable electricity generation 2']
    ren_yearly = ren_df.groupby('Year')['Value'].mean().rename('Renewable_Share')
    
    # Environment Taxes
    tax_df = green_growth[green_growth['Measure'] == 'Environment related tax revenue 2']
    tax_yearly = tax_df.groupby('Year')['Value'].mean().rename('Env_Taxes')
    
    # C. Patents (Kazakhstan only, applications)
    pat_kz = patents[(patents['Country'] == 'Kazakhstan') & (patents['Measure'] == 'Patent applications')]
    pat_yearly = pat_kz.groupby('Year')['Patents'].sum().rename('Green_Patents')
    
    # Merge all
    for s in [ep_yearly, ren_yearly, tax_yearly, pat_yearly]:
        df_reg = df_reg.merge(s, on='Year', how='left')
        
    df_reg = df_reg.dropna().reset_index(drop=True)
    
    if df_reg.empty:
        print("Data merging resulted in empty dataframe. Cannot run regression.")
        return
        
    # 3. Run OLS Regressions
    # Model 1: Predicting CO2 Emissions
    # Dependent Variable: Value_CO2
    # Independent Variables: Value_GDP, Energy_Productivity, Renewable_Share, Green_Patents
    
    X1 = df_reg[['Value_GDP', 'Energy_Productivity', 'Renewable_Share', 'Green_Patents']]
    X1 = sm.add_constant(X1)
    y1 = df_reg['Value_CO2']
    
    model1 = sm.OLS(y1, X1).fit()
    
    with open(out_dir / 'regression_results.txt', 'w') as f:
        f.write("MACROECONOMIC REGRESSION RESULTS FOR KAZAKHSTAN (2010-2023)\n")
        f.write("="*60 + "\n\n")
        f.write("Model 1: Determinants of CO2 Emissions\n")
        f.write(model1.summary().as_text())
        f.write("\n\n")
        
    print("Regression analysis complete. Results saved to outputs/regression_results.txt")
    print(model1.summary())

if __name__ == '__main__':
    main()
