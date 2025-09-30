# eda.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------- Helper functions ----------------
def _format_time(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        if isinstance(val, pd.Timedelta):
            total = int(val.total_seconds())
            hh = total // 3600
            mm = (total % 3600) // 60
            ss = total % 60
            return f"{hh:02d}:{mm:02d}:{ss:02d}"
        s = str(val)
        if "days" in s:
            return s.split("days")[-1].strip()
        return s
    except:
        return str(val)

def _format_num(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        return f"{float(val):.2f}"
    except:
        return str(val)

# ---------------- Function to show metrics in box ----------------
def show_metrics_box(metrics):
    num_cols = len(metrics)
    cols = st.columns(num_cols)
    for col, (name, val) in zip(cols, metrics.items()):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center; background-color:#f9f9f9;">
                    <div style="font-size:14px; color:#555;">{name}</div>
                    <div style="font-size:20px; font-weight:bold; margin-top:5px;">{_format_num(val)}</div>
                </div>
                """, unsafe_allow_html=True
            )

# ---------------- Employee Summary ----------------
def show_employee_summary(emp_row):
    st.subheader("👤 Employee Summary")
    
    designation_col = next((c for c in emp_row.index if "Designation" in c), None)
    account_col = next((c for c in emp_row.index if "Account" in c), None)
    
    designation = emp_row[designation_col] if designation_col else "N/A"
    account = emp_row[account_col] if account_col else "N/A"

    st.write(f"**Designation:** {designation}")
    st.write(f"**Account:** {account}")
    st.write(f"**Avg In Time:** {_format_time(emp_row.get('Avg_In_Tim'))}")
    st.write(f"**Avg Out Time:** {_format_time(emp_row.get('Avg_Out_Tim'))}")

    metrics = {
        "Avg Office Hours": emp_row.get("Office_hr_hours",0),
        "Avg Bay Hours": emp_row.get("Bay_hr_hours",0),
        "Avg Break Hours": emp_row.get("Break_hr_hours",0),
        "Avg Cafeteria": emp_row.get("Cafeteria_hours",0),
        "Avg OOO Hours": emp_row.get("OOO_hr_hours",0),
        "Efficiency": emp_row.get("Efficiency",0),
        "Absenteeism ": emp_row.get("Absenteeism",0),
        "Burnout Hours": max(0, emp_row.get("Office_hr_hours",0)-9)
    }

    show_metrics_box(metrics)

    # Charts side by side
    col1, col2 = st.columns(2)

    with col1:
        # Bar chart: only main work hours
        bar_metrics = {
            "Office Hours": emp_row.get("Office_hr_hours",0),
            "Bay Hours": emp_row.get("Bay_hr_hours",0),
            "Break Hours": emp_row.get("Break_hr_hours",0),
            "Cafeteria": emp_row.get("Cafeteria_hours",0),
            "OOO Hours": emp_row.get("OOO_hr_hours",0)
        }
        fig, ax = plt.subplots(figsize=(4,3))
        ax.bar(bar_metrics.keys(), bar_metrics.values(), color=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'])
        ax.set_ylabel("Hours")
        ax.set_title("Work Hours Distribution")
        for i, v in enumerate(bar_metrics.values()):
            ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        # Pie chart (Bay/Break/Cafeteria)
        pie_metrics = {"Bay": emp_row.get("Bay_hr_hours",0),
                       "Break": emp_row.get("Break_hr_hours",0),
                       "Cafeteria": emp_row.get("Cafeteria_hours",0)}
        pie_metrics = {k:v for k,v in pie_metrics.items() if v>0}
        if sum(pie_metrics.values())>0:
            fig, ax = plt.subplots(figsize=(4,3))
            ax.pie(list(pie_metrics.values()), labels=list(pie_metrics.keys()), autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor':'white'})
            ax.set_title("Work Distribution (Bay/Break/Cafeteria)")
            st.pyplot(fig)
            plt.close(fig)

# ---------------- Organization Summary ----------------
def show_org_summary(df, account_choice=None):
    st.subheader(f"🏢 Organization Summary{(' - '+account_choice) if account_choice else ''}")

    metrics_cols = ["Office_hr_hours","Bay_hr_hours","Break_hr_hours","Cafeteria_hours","OOO_hr_hours","Efficiency","Absenteeism"]
    means = {m: df[m].dropna().mean() if m in df.columns else 0 for m in metrics_cols}

    metrics = {
        "Avg Office Hours": means["Office_hr_hours"],
        "Avg Bay Hours": means["Bay_hr_hours"],
        "Avg Break Hours": means["Break_hr_hours"],
        "Avg Cafeteria": means["Cafeteria_hours"],
        "Avg OOO Hours": means["OOO_hr_hours"],
        "Efficiency": means["Efficiency"],
        "Absenteeism ": means["Absenteeism"],
        "Burnout Hours": max(0, means["Office_hr_hours"]-9)
    }

    show_metrics_box(metrics)

    # Charts side by side
    col1, col2 = st.columns(2)

    with col1:
        # Bar chart: only main work hours
        bar_metrics = {
            "Office Hours": means["Office_hr_hours"],
            "Bay Hours": means["Bay_hr_hours"],
            "Break Hours": means["Break_hr_hours"],
            "Cafeteria": means["Cafeteria_hours"],
            "OOO Hours": means["OOO_hr_hours"]
        }
        fig, ax = plt.subplots(figsize=(4,3))
        ax.bar(bar_metrics.keys(), bar_metrics.values(), color=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'])
        ax.set_ylabel("Hours")
        ax.set_title("Avg Work Hours Distribution")
        for i, v in enumerate(bar_metrics.values()):
            ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        # Pie chart (Bay/Break/Cafeteria)
        pie_metrics = {"Bay": means["Bay_hr_hours"],
                       "Break": means["Break_hr_hours"],
                       "Cafeteria": means["Cafeteria_hours"]}
        pie_metrics = {k:v for k,v in pie_metrics.items() if v>0}
        if sum(pie_metrics.values())>0:
            fig, ax = plt.subplots(figsize=(4,3))
            ax.pie(list(pie_metrics.values()), labels=list(pie_metrics.keys()), autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor':'white'})
            ax.set_title("Work Distribution (Bay/Break/Cafeteria)")
            st.pyplot(fig)
            plt.close(fig)
