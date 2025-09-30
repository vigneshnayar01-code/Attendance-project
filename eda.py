import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def _format(val):
    """Helper to format numbers to 2 decimals"""
    if pd.isna(val):
        return "N/A"
    try:
        return f"{float(val):.2f}"
    except:
        return val
def _format_time(val):
    """Helper to format timedelta or datetime to HH:MM:SS"""
    import pandas as pd
    if pd.isna(val) or val is None:
        return "N/A"
    try:
        val_str = str(val)
        # Handle "0 days 12:31:24" → "12:31:24"
        if "days" in val_str:
            return val_str.split("days")[-1].strip()
        return val_str.strip()
    except:
        return str(val)
def show_employee_summary(emp_data, designation_col, recruit_col, account_col):
    st.subheader("👤 Employee Summary")

    st.write(f"**Designation**: {emp_data.get(designation_col, 'N/A') if designation_col else 'N/A'}")
    st.write(f"**Recruitment Type**: {emp_data.get(recruit_col, 'N/A') if recruit_col else 'N/A'}")
    st.write(f"**Account**: {emp_data.get(account_col, 'N/A') if account_col else 'N/A'}")

    st.write(f"**Avg In Time**: {_format_time(emp_data.get('Avg_In_Tim'))}")
    st.write(f"**Avg Out Time**: {_format_time(emp_data.get('Avg_Out_Tim'))}")

    st.write(f"**Avg Office Hours**: {_format(emp_data.get('Office_hr_hours'))}")
    st.write(f"**Avg Bay Hours**: {_format(emp_data.get('Bay_hr_hours'))}")
    st.write(f"**Avg Break Hours**: {_format(emp_data.get('Break_hr_hours'))}")
    st.write(f"**Efficiency**: {_format(emp_data.get('Efficiency'))}")
    st.write(f"**Absenteeism**: {_format(emp_data.get('Absenteeism'))}")

    # Visualization
    st.subheader("📊 Work Pattern")
    metrics = {
        "Office Hours": emp_data.get("Office_hr_hours", 0),
        "Bay Hours": emp_data.get("Bay_hr_hours", 0),
        "Break Hours": emp_data.get("Break_hr_hours", 0),
        "Cafeteria": emp_data.get("Cafeteria_hours", 0),
        "OOO Hours": emp_data.get("OOO_hr_hours", 0),
    }
    fig, ax = plt.subplots(figsize=(6, 3))  # smaller width & height
    ax.bar(metrics.keys(), metrics.values())
    ax.set_ylabel("Hours")
    ax.set_title("Employee Work Distribution")
    st.pyplot(fig)
    fig, ax = plt.subplots(figsize=(5, 5))  # square shape for pie chart
    # Work distribution as % of Office Hours
    office_hours = emp_data.get("Office_hr_hours", 0) or 0
    distribution = {
        "Bay Hours": emp_data.get("Bay_hr_hours", 0) or 0,
        "Break Hours": emp_data.get("Break_hr_hours", 0) or 0,
        "Cafeteria": emp_data.get("Cafeteria_hours", 0) or 0,
    }

    # Add "Other" slice = remaining time not covered above
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.pie(
        distribution.values(),
        labels=distribution.keys(),
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white'}
    )
    ax.set_title("Employee Work Distribution (within Office Hours)")
    st.pyplot(fig)



def show_org_summary(df, account_choice):
    st.subheader(f"🏢 Organization Summary for {account_choice}")

    # High level KPIs (rounded to 2 decimals)
    st.metric("Average Office Hours", f"{df['Office_hr_hours'].mean():.2f}")
    st.metric("Average Efficiency", f"{df['Efficiency'].mean():.2f}")
    st.metric("Average Absenteeism", f"{df['Absenteeism'].mean():.2f}")

    # Visualization - Office vs Bay vs Break hours
    st.subheader("📊 Avg Hours Across This Account")
    avg_metrics = {
        "Office Hours": df['Office_hr_hours'].mean(),
        "Bay Hours": df['Bay_hr_hours'].mean(),
        "Break Hours": df['Break_hr_hours'].mean(),
        "Cafeteria": df['Cafeteria_hours'].mean(),
        "OOO Hours": df['OOO_hr_hours'].mean(),
    }
    fig, ax = plt.subplots()
    ax.bar(avg_metrics.keys(), avg_metrics.values())
    ax.set_ylabel("Hours")
    ax.set_title(f"Average Work Distribution - {account_choice}")
    st.pyplot(fig)
