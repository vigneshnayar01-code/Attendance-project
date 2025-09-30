# preprocess.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(".", "", regex=False)
    return df

def add_features(df):
    # Convert time columns
    for col in ['Avg_In_Tim', 'Avg_Out_Tim']:
        if col in df.columns:
            df[col] = pd.to_timedelta(df[col].astype(str), errors="coerce")

    # Decimal hour columns
    hour_cols = ['Avg_Office_hr', 'Avg_Bay_hr', 'Avg_Break_hr', 'Avg_Cafeteria', 'Avg_OOO_hr']
    for col in hour_cols:
        if col in df.columns:
            decimal_col_name = col.replace('Avg_', '') + '_hours'
            df[decimal_col_name] = pd.to_timedelta(df[col].astype(str), errors="coerce").dt.total_seconds() / 3600

    # Punctuality
    if 'Avg_In_Tim' in df.columns:
        df['Punctuality'] = (abs(df['Avg_In_Tim'] - pd.to_timedelta("09:00:00")).dt.total_seconds() / 3600)
    else:
        df['Punctuality'] = 0

    # Break utilization
    df['Break_Utilization'] = ((df.get('Break_hr_hours', 0).fillna(0) + df.get('Cafeteria_hours', 0).fillna(0))
                               / df.get('Office_hr_hours', 1))
    df['Break_Utilization'] = df['Break_Utilization'].replace([float('inf'), float('-inf')], float('nan'))

    # Absenteeism
    if 'Half_Day' in df.columns and 'Full_Day' in df.columns:
        df['Absenteeism'] = (df['Half_Day']*2 + df['Full_Day'])
    else:
        df['Absenteeism'] = 0

    # Efficiency
    df['Efficiency'] = df.get('Bay_hr_hours', 0) / df.get('Office_hr_hours', 1)
    df['Efficiency'] = df['Efficiency'].replace([float('inf'), float('-inf')], float('nan'))

    return df
