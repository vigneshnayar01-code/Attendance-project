# app.py
import streamlit as st
from preprocess import load_data, add_features
from recommender import generate_recommendation
from eda import show_employee_summary, show_org_summary

def main():
    st.set_page_config(page_title="Next Best Action Recommender", layout="wide")
    st.title("Next Best Action Recommender (Attendance Data)")
    st.markdown("This tool helps HoRM take data-backed resource decisions.")

    uploaded_file = st.file_uploader("Upload Attendance File (Optional)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        file_path_or_buffer = uploaded_file
    else:
        st.info("No file uploaded. Using default dataset.")
        file_path_or_buffer = "data/Cleaned_Attendance_Data.xlsx"

    try:
        df = load_data(file_path_or_buffer)
        df = add_features(df)
        st.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return

    emp_id_col = next((c for c in df.columns if "Fake" in c or "ID" in c), None)
    account_col = next((c for c in df.columns if "Account" in c), None)
    if emp_id_col is None or account_col is None:
        st.error("Required columns missing in dataset (Employee ID / Account)")
        return

    tab1, tab2 = st.tabs(["🔎 Employee View", "🏢 Organization View"])

    with tab1:
        emp_id = st.text_input("Enter Employee ID")
        if emp_id:
            emp_ids = df[emp_id_col].astype(str).values
            if emp_id not in emp_ids:
                st.error("Employee ID not found in data")
            else:
                emp_data = df[df[emp_id_col].astype(str)==emp_id].iloc[0]
                show_employee_summary(emp_data)
                recs = generate_recommendation(emp_data)
                st.subheader("📌 Next Best Action")
                for r in recs:
                    st.write("- ", r)

    with tab2:
        account_choice = st.selectbox("Select Account", df[account_col].dropna().unique())
        if account_choice:
            df_account = df[df[account_col]==account_choice]
            show_org_summary(df_account, account_choice)

if __name__ == "__main__":
    main()
