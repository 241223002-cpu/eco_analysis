
import pandas as pd
import os
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:/Users/sejha/OneDrive/Рабочий стол/analysis_final_project/paper/eco_analysis'

# ============================================================
# 1. data.csv (actually an xlsx)
# ============================================================
print("\n" + "="*70)
print("FILE: data/data.csv (actually XLSX - Agricultural Policy / PSE data)")
print("="*70)
agri_path = os.path.join(BASE, 'data', 'data_actual.xlsx')
agri = pd.read_excel(agri_path, engine='calamine', sheet_name='Table', header=None)
print(f"Rows: {len(agri)}, Cols: {agri.shape[1]}")
print("\nAll measures found:")
for i in range(5, len(agri)):
    row = agri.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null and len(non_null) > 1:
        measure = non_null[0].strip()
        unit = non_null[1].strip() if len(non_null) > 1 else 'n/a'
        print(f"  [{i:3d}] {measure[:70]}  |  {unit}")
    elif non_null and 'OECD' not in non_null[0] and 'Terms' not in non_null[0]:
        print(f"  [{i:3d}] [SECTION] {non_null[0][:80]}")

# ============================================================
# 2. OECD Green Growth (Kazakhstan)
# ============================================================
print("\n" + "="*70)
print("FILE: OECD Green Growth (Kazakhstan, 2009-2025)")
print("="*70)
gg_path = os.path.join(BASE, 'data', 'OECD', 'OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1,filtered,2026-04-27 19-28-01.xlsx')
gg = pd.read_excel(gg_path, engine='calamine', sheet_name='Table', header=None)
print(f"Rows: {len(gg)}, Cols: {gg.shape[1]}")
print("\nAll measures found:")
for i in range(5, len(gg)):
    row = gg.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null and len(non_null) > 1:
        measure = non_null[0].strip()
        unit = non_null[1].strip() if len(non_null) > 1 else 'n/a'
        print(f"  [{i:3d}] {measure[:70]}  |  {unit}")
    elif non_null and 'Terms' not in non_null[0]:
        print(f"  [{i:3d}] [SECTION] {non_null[0][:80]}")

# ============================================================
# 3. Air Emissions Accounts (Kazakhstan)
# ============================================================
print("\n" + "="*70)
print("FILE: OECD Air Emissions Accounts (Kazakhstan)")
print("="*70)
aea_path = os.path.join(BASE, 'data', 'OECD', 'OECD.SDD.NAD.SEEA,DSD_AEA@DF_AEA,1.2,filtered,2026-04-27 19-26-31.xlsx')
aea = pd.read_excel(aea_path, engine='calamine', sheet_name='Table', header=None)
print(f"Rows: {len(aea)}, Cols: {aea.shape[1]}")
for i in range(0, len(aea)):
    row = aea.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null:
        print(f"  [{i:3d}] {str(non_null)[:100]}")

# ============================================================
# 4. GDP Income (Kazakhstan)
# ============================================================
print("\n" + "="*70)
print("FILE: OECD Annual GDP - Income (Kazakhstan)")
print("="*70)
gdp_path = os.path.join(BASE, 'data', 'OECD', 'OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_INCOME,2.0,filtered,2026-04-24 20-42-01.xlsx')
gdp = pd.read_excel(gdp_path, engine='calamine', sheet_name='Table', header=None)
print(f"Rows: {len(gdp)}, Cols: {gdp.shape[1]}")
for i in range(0, len(gdp)):
    row = gdp.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null:
        print(f"  [{i:3d}] {str(non_null)[:120]}")

# ============================================================
# 5. Environment-related Patents
# ============================================================
print("\n" + "="*70)
print("FILE: OECD Environment-related Technology Patents")
print("="*70)
pat_path = os.path.join(BASE, 'data', 'OECD', 'OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_ENVIROMENT,1.0,filtered,2026-04-27 19-19-04.xlsx')
pat = pd.read_excel(pat_path, engine='calamine', sheet_name='Table', header=None)
print(f"Rows: {len(pat)}, Cols: {pat.shape[1]}")
for i in range(0, min(20, len(pat))):
    row = pat.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null:
        print(f"  [{i:3d}] {str(non_null)[:120]}")
# Find header row and unique measures
print("\n  ... finding data rows ...")
header_row = 6
years = [str(x) for x in pat.iloc[header_row].tolist() if str(x) != 'nan']
print(f"  Header row {header_row}: {years[:10]} ...")
measures = []
for i in range(header_row+1, len(pat)):
    row = pat.iloc[i].tolist()
    non_null = [str(x) for x in row if str(x) != 'nan']
    if non_null:
        measures.append(non_null[0][:80])
print(f"\n  Unique measures/countries ({len(measures)}):")
for m in measures[:30]:
    print(f"    - {m}")
