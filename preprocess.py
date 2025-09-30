import pandas as pd
import numpy as np
import re
import streamlit as st

@st.cache_data
def load_data(uploaded_file):
    # uploaded_file is a Streamlit UploadedFile (file-like). Use name to detect type.
    name = getattr(uploaded_file, "name", "")
    ext = name.split(".")[-1].lower() if name and "." in name else ""

    try:
        if ext in ("xls", "xlsx"):
            df = pd.read_excel(uploaded_file)
        elif ext in ("csv", "tsv", "txt"):
            # try to infer delimiter. pandas can auto-detect with sep=None + python engine
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine="python")
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file)
        else:
            # fallback: try excel then csv
            try:
                df = pd.read_excel(uploaded_file)
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine="python")
    except Exception as e:
        raise ValueError(f"Could not parse uploaded file: {e}")

    # Normalize column names
    def clean_col(c):
        c = str(c).strip()
        c = re.sub(r"[ \t\r\n]+", "_", c)
        c = re.sub(r"[^\w_]", "", c)  # remove punctuation except underscore
        return c

    df.columns = [clean_col(c) for c in df.columns]
    return df


def add_features(df):
    df = df.copy()
    # helper to parse hour-like values into decimal hours
    def parse_hour_val(x):
        if pd.isna(x):
            return np.nan
        if isinstance(x, (int, float, np.number)):
            return float(x)
        s = str(x).strip()
        # if time-like "HH:MM" or "HH:MM:SS"
        try:
            if ":" in s:
                td = pd.to_timedelta(s)
                return td.total_seconds() / 3600.0
            # sometimes in format '8.5' or '8,5'
            s2 = s.replace(",", ".")
            return float(re.sub(r"[^\d\.\-]", "", s2))
        except Exception:
            return np.nan

    # Convert Avg_In_Tim / Avg_Out_Tim to timedelta (if present)
    for col in ["Avg_In_Tim", "Avg_Out_Tim"]:
        if col in df.columns:
            # attempt conversion, keep as timedelta series (NaT where invalid)
            df[col] = pd.to_timedelta(df[col].astype(str), errors="coerce")

    # Handle hour-like columns and create consistent decimal-hour columns
    hour_cols = ["Avg_Office_hr", "Avg_Bay_hr", "Avg_Break_hr", "Avg_Cafeteria", "Avg_OOO_hr"]
    for col in hour_cols:
        if col in df.columns:
            base = col.replace("Avg_", "")
            newcol = f"{base}_hours"
            df[newcol] = df[col].apply(parse_hour_val)

    # Ensure column names referenced later exist (create with NaN if missing)
    for expected in ["Office_hr_hours", "Bay_hr_hours", "Break_hr_hours", "Cafeteria_hours"]:
        if expected not in df.columns:
            df[expected] = np.nan

    # Punctuality: absolute hours difference from 09:00:00 if Avg_In_Tim exists
    if "Avg_In_Tim" in df.columns:
        ref = pd.to_timedelta("09:00:00")
        # Avg_In_Tim is a timedelta series; compute difference and convert to decimal hours
        try:
            df["Punctuality"] = (df["Avg_In_Tim"].dt.components["hours"].fillna(0) * 1.0 +
                                 df["Avg_In_Tim"].dt.components["minutes"].fillna(0) / 60.0 +
                                 df["Avg_In_Tim"].dt.components["seconds"].fillna(0) / 3600.0)
            # But easier to compute absolute diff in seconds:
            df["Punctuality"] = (df["Avg_In_Tim"] - ref).abs().dt.total_seconds() / 3600.0
        except Exception:
            df["Punctuality"] = np.nan
    else:
        df["Punctuality"] = np.nan

    # Break utilization
    df["Break_Utilization"] = (df.get("Break_hr_hours", 0).fillna(0) + df.get("Cafeteria_hours", 0).fillna(0)) / df.get("Office_hr_hours", np.nan)
    df["Break_Utilization"].replace([np.inf, -np.inf], np.nan, inplace=True)

    # Absenteeism: prefer Half_Day & Full_Day if available
    if "Half_Day" in df.columns and "Full_Day" in df.columns:
        try:
            df["Absenteeism"] = df["Half_Day"].fillna(0) * 2 + df["Full_Day"].fillna(0)
        except Exception:
            df["Absenteeism"] = np.nan
    else:
        # fallback: try presence/absent columns or default to 0
        df["Absenteeism"] = np.nan

    # Efficiency: ratio Bay_hours / Office_hours
    df["Efficiency"] = df.get("Bay_hr_hours", 0) / df.get("Office_hr_hours", np.nan)
    df["Efficiency"].replace([np.inf, -np.inf], np.nan, inplace=True)

    return df
