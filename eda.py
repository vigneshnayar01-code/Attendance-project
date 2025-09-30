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

# ---------------- Employee Summary ----------------
def show_employee_summary(emp_row):
    st.subheader("👤 Employee Summary")
    
    # Detect column dynamically
    designation_col = next((c for c in emp_row.index if "Designation" in c), None)
    account_col = next((c for c in emp_row.index if "Account" in c), None)
    
    designation = emp_row[designation_col] if designation_col else "N/A"
    account = emp_row[account_col] if account_col else "N/A"

    st.write(f"**Designation:** {designation}")
    st.write(f"**Account:** {account}")
    st.write(f"**Avg In Time:** {_format_time(emp_row.get('Avg_In_Tim'))}")
    st.write(f"**Avg Out Time:** {_format_time(emp_row.get('Avg_Out_Tim'))}")

    office = emp_row.get("Office_hr_hours",0)
    bay = emp_row.get("Bay_hr_hours",0)
    brk = emp_row.get("Break_hr_hours",0)
    cafe = emp_row.get("Cafeteria_hours",0)
    ooo = emp_row.get("OOO_hr_hours",0)
    eff = emp_row.get("Efficiency",0)
    absn = emp_row.get("Absenteeism",0)
    
    st.metric("Avg Office Hours", _format_num(office))
    st.metric("Avg Bay Hours", _format_num(bay))
    st.metric("Avg Break Hours", _format_num(brk))
    st.metric("Avg Cafeteria", _format_num(cafe))
    st.metric("Avg OOO Hours", _format_num(ooo))
    st.metric("Efficiency", _format_num(eff))
    st.metric("Absenteeism (days)", _format_num(absn))
    st.metric("Burnout Hours", _format_num(max(0, office-9)))

    # Bar chart
    metrics = {"Office Hours": office, "Bay Hours": bay, "Break Hours": brk, "Cafeteria": cafe, "OOO Hours": ooo}
    fig, ax = plt.subplots(figsize=(6,3))
    ax.bar(metrics.keys(), metrics.values(), color=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'])
    ax.set_ylabel("Hours")
    ax.set_title("Employee Work Hours Distribution")
    for i, v in enumerate(metrics.values()):
        ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close(fig)

    # Pie chart (Bay/Break/Cafeteria)
    pie_metrics = {"Bay Hours": bay, "Break Hours": brk, "Cafeteria": cafe}
    pie_metrics = {k:v for k,v in pie_metrics.items() if v>0}
    if sum(pie_metrics.values())>0:
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(list(pie_metrics.values()), labels=list(pie_metrics.keys()), autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor':'white'})
        ax.set_title("Work Distribution ")
        st.pyplot(fig)
        plt.close(fig)

# ---------------- Organization Summary ----------------
def show_org_summary(df, account_choice=None):
    st.subheader(f"🏢 Organization Summary{(' - '+account_choice) if account_choice else ''}")

    metrics = ["Office_hr_hours","Bay_hr_hours","Break_hr_hours","Cafeteria_hours","OOO_hr_hours","Efficiency","Absenteeism","Punctuality"]
    means = {m: df[m].dropna().mean() if m in df.columns else 0 for m in metrics}

    st.metric("Average Office Hours", _format_num(means["Office_hr_hours"]))
    st.metric("Average Bay Hours", _format_num(means["Bay_hr_hours"]))
    st.metric("Average Break Hours", _format_num(means["Break_hr_hours"]))
    st.metric("Average Cafeteria", _format_num(means["Cafeteria_hours"]))
    st.metric("Average OOO Hours", _format_num(means["OOO_hr_hours"]))
    st.metric("Average Efficiency", _format_num(means["Efficiency"]))
    st.metric("Average Absenteeism", _format_num(means["Absenteeism"]))
    st.metric("Burnout Hours", _format_num(max(0, means["Office_hr_hours"]-9)))

    # Bar chart
    bar_metrics = {
        "Office Hours": means["Office_hr_hours"],
        "Bay Hours": means["Bay_hr_hours"],
        "Break Hours": means["Break_hr_hours"],
        "Cafeteria": means["Cafeteria_hours"],
        "OOO Hours": means["OOO_hr_hours"]
    }
    fig, ax = plt.subplots(figsize=(6,3))
    ax.bar(bar_metrics.keys(), bar_metrics.values(), color=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'])
    ax.set_ylabel("Hours")
    ax.set_title("Organization Average Work Hours Distribution")
    for i, v in enumerate(bar_metrics.values()):
        ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close(fig)

    # Pie chart (Bay/Break/Cafeteria)
    pie_metrics = {"Bay Hours": means["Bay_hr_hours"], "Break Hours": means["Break_hr_hours"], "Cafeteria": means["Cafeteria_hours"]}
    pie_metrics = {k:v for k,v in pie_metrics.items() if v>0}
    if sum(pie_metrics.values())>0:
        fig, ax = plt.subplots(figsize=(4,3))
        ax.pie(list(pie_metrics.values()), labels=list(pie_metrics.keys()), autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor':'white'})
        ax.set_title("Organization Work Distribution ")
        st.pyplot(fig)
        plt.close(fig)
