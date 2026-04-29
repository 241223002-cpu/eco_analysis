import pandas as pd
import numpy as np
import os
import shutil

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def clean_string(s):
    if pd.isna(s):
        return ""
    s = str(s).strip()
    if s.lower() == 'nan':
        return ""
    # Remove weird bullet points and non-breaking spaces
    s = s.replace('·', '').replace('', '').replace('\u2007', '').strip()
    return s

def process_agricultural_pse(base_dir, out_dir):
    print("Processing Agricultural PSE data...")
    src = os.path.join(base_dir, 'data', 'data.csv')
    dst = os.path.join(base_dir, 'data', 'data_actual.xlsx')
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    
    df = pd.read_excel(dst, engine='calamine', sheet_name='Table', header=None)
    
    # Row 4 contains years
    years_row = df.iloc[4].tolist()
    years = []
    year_cols = []
    for i, y in enumerate(years_row):
        if pd.notna(y) and str(y).replace('.0', '').isdigit() and int(str(y).replace('.0', '')) > 1900:
            years.append(str(y).replace('.0', ''))
            year_cols.append(i)
            
    # Row 5 has column headers for the first few cols
    measure_col = 1
    unit_col = 2
    
    data = []
    for i in range(6, len(df)):
        row = df.iloc[i]
        measure = clean_string(row[measure_col])
        unit = clean_string(row[unit_col])
        if measure and measure != 'nan' and 'Terms' not in measure:
            for y_idx, y in zip(year_cols, years):
                val = row[y_idx]
                if pd.notna(val) and str(val) != '..':
                    data.append({
                        'Measure': measure,
                        'Unit': unit,
                        'Year': int(y),
                        'Value': val
                    })
                    
    clean_df = pd.DataFrame(data)
    out_path = os.path.join(out_dir, 'agricultural_pse_clean.csv')
    clean_df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(clean_df)} records to {out_path}")


def process_green_growth(base_dir, out_dir):
    print("Processing Green Growth data...")
    path = os.path.join(base_dir, 'data', 'OECD', 'OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1,filtered,2026-04-27 19-28-01.xlsx')
    df = pd.read_excel(path, engine='calamine', sheet_name='Table', header=None)
    
    # Row 3 contains years
    years_row = df.iloc[3].tolist()
    years = []
    year_cols = []
    for i, y in enumerate(years_row):
        if pd.notna(y) and str(y).replace('.0', '').isdigit() and int(str(y).replace('.0', '')) > 1900:
            years.append(str(y).replace('.0', ''))
            year_cols.append(i)
            
    measure_col = 1
    unit_col = 2
    
    current_section = "General"
    data = []
    
    for i in range(5, len(df)):
        row = df.iloc[i]
        measure = clean_string(row[measure_col])
        unit = clean_string(row[unit_col])
        
        if not measure or measure == 'nan' or 'Terms' in measure:
            continue
            
        # Check if it's a section header (no unit, no data)
        has_data = any(pd.notna(row[idx]) and str(row[idx]) != '..' for idx in year_cols)
        if not has_data and not unit:
            current_section = measure
            continue
            
        for y_idx, y in zip(year_cols, years):
            val = row[y_idx]
            if pd.notna(val) and str(val) != '..':
                try:
                    val_float = float(val)
                    data.append({
                        'Section': current_section,
                        'Measure': measure,
                        'Unit': unit,
                        'Year': int(y),
                        'Value': val_float
                    })
                except ValueError:
                    pass
                    
    clean_df = pd.DataFrame(data)
    out_path = os.path.join(out_dir, 'green_growth_clean.csv')
    clean_df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(clean_df)} records to {out_path}")


def process_air_emissions(base_dir, out_dir):
    print("Processing Air Emissions data...")
    path = os.path.join(base_dir, 'data', 'OECD', 'OECD.SDD.NAD.SEEA,DSD_AEA@DF_AEA,1.2,filtered,2026-04-27 19-26-31.xlsx')
    df = pd.read_excel(path, engine='calamine', sheet_name='Table', header=None)
    
    # Find years row
    years_row_idx = -1
    for i in range(20):
        row_vals = [str(x) for x in df.iloc[i].tolist()]
        if any('Time period' in val for val in row_vals):
            years_row_idx = i
            break
            
    if years_row_idx == -1:
        print("  -> Could not find years row!")
        return

    years_row = df.iloc[years_row_idx].tolist()
    years = []
    year_cols = []
    for i, y in enumerate(years_row):
        if pd.notna(y):
            y_str = str(y).replace('.0', '').strip()
            if y_str.isdigit() and int(y_str) > 1900:
                years.append(y_str)
                year_cols.append(i)
            
    sector_col = 1
    data = []
    
    for i in range(years_row_idx + 2, len(df)):
        row = df.iloc[i]
        sector = clean_string(row[sector_col])
        
        if not sector or sector == 'nan' or 'Terms' in sector:
            continue
            
        for y_idx, y in zip(year_cols, years):
            val = row[y_idx]
            if pd.notna(val) and str(val) != '..':
                try:
                    val_float = float(val)
                    data.append({
                        'Sector': sector,
                        'Year': int(y),
                        'CO2_Emissions_Tonnes': val_float
                    })
                except ValueError:
                    pass
                    
    clean_df = pd.DataFrame(data)
    out_path = os.path.join(out_dir, 'air_emissions_clean.csv')
    clean_df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(clean_df)} records to {out_path}")


def process_gdp_income(base_dir, out_dir):
    print("Processing GDP Income data...")
    path = os.path.join(base_dir, 'data', 'OECD', 'OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_INCOME,2.0,filtered,2026-04-24 20-42-01.xlsx')
    df = pd.read_excel(path, engine='calamine', sheet_name='Table', header=None)
    
    # Row 5 contains years
    years_row = df.iloc[5].tolist()
    years = []
    year_cols = []
    for i, y in enumerate(years_row):
        if pd.notna(y) and str(y).replace('.0', '').isdigit() and int(str(y).replace('.0', '')) > 1900:
            years.append(str(y).replace('.0', ''))
            year_cols.append(i)
            
    measure_col = 1
    sector_col = 2
    unit_col = 3
    data = []
    
    current_unit = "National Currency"
    for i in range(7, len(df)):
        row = df.iloc[i]
        measure = clean_string(row[measure_col])
        
        if 'Unit of measure:' in measure:
            current_unit = measure.replace('Unit of measure:', '').strip()
            continue
            
        if not measure or measure == 'nan' or 'Terms' in measure:
            continue
            
        sector = clean_string(row[sector_col])
        unit = clean_string(row[unit_col])
        if not unit: unit = current_unit
            
        for y_idx, y in zip(year_cols, years):
            val = row[y_idx]
            if pd.notna(val) and str(val) != '..':
                try:
                    val_float = float(val)
                    data.append({
                        'Measure': measure,
                        'Sector': sector,
                        'Unit': unit,
                        'Year': int(y),
                        'Value': val_float
                    })
                except ValueError:
                    pass
                    
    clean_df = pd.DataFrame(data)
    out_path = os.path.join(out_dir, 'gdp_income_clean.csv')
    clean_df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(clean_df)} records to {out_path}")


def process_patents(base_dir, out_dir):
    print("Processing Patents data...")
    path = os.path.join(base_dir, 'data', 'OECD', 'OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_ENVIROMENT,1.0,filtered,2026-04-27 19-19-04.xlsx')
    df = pd.read_excel(path, engine='calamine', sheet_name='Table', header=None)
    
    # Row 6 has years, Row 7 has authorities, Row 8 has measure
    years_row = df.iloc[6].tolist()
    auth_row = df.iloc[7].tolist()
    measure_row = df.iloc[8].tolist()
    
    data = []
    for i in range(10, len(df)):
        row = df.iloc[i]
        country = clean_string(row[1])
        
        if not country or country == 'nan' or 'Terms' in country:
            continue
            
        for col_idx in range(2, len(row)):
            year = clean_string(years_row[col_idx])
            auth = clean_string(auth_row[col_idx])
            measure = clean_string(measure_row[col_idx])
            val = row[col_idx]
            
            if year and year.isdigit() and pd.notna(val) and str(val) != '..':
                try:
                    val_float = float(val)
                    data.append({
                        'Country': country,
                        'Authority': auth,
                        'Measure': measure,
                        'Year': int(year),
                        'Patents': val_float
                    })
                except ValueError:
                    pass
                    
    clean_df = pd.DataFrame(data)
    out_path = os.path.join(out_dir, 'patents_clean.csv')
    clean_df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(clean_df)} records to {out_path}")


def main():
    base_dir = get_project_root()
    out_dir = os.path.join(base_dir, 'data', 'cleaned')
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Saving cleaned files to: {out_dir}\n")
    
    try: process_agricultural_pse(base_dir, out_dir)
    except Exception as e: print(f"Error processing Agricultural PSE: {e}")
    
    try: process_green_growth(base_dir, out_dir)
    except Exception as e: print(f"Error processing Green Growth: {e}")
    
    try: process_air_emissions(base_dir, out_dir)
    except Exception as e: print(f"Error processing Air Emissions: {e}")
    
    try: process_gdp_income(base_dir, out_dir)
    except Exception as e: print(f"Error processing GDP Income: {e}")
    
    try: process_patents(base_dir, out_dir)
    except Exception as e: print(f"Error processing Patents: {e}")
    
    print("\nData cleaning complete!")

if __name__ == "__main__":
    main()
