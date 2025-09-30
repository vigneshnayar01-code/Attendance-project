import streamlit as st
from preprocess import load_data, add_features
from recommender import generate_recommendation
from eda import show_employee_summary, show_org_summary

def main():
    st.set_page_config(page_title="Next Best Action Recommender", layout="wide")

    st.title("Next Best Action Recommender (Attendance Data)")
    st.markdown("This tool helps HoRM take data-backed resource decisions.")

    uploaded_file = st.file_uploader("Upload Attendance File", type=["xlsx", "csv"])
    if uploaded_file:
        try:
            df = load_data(uploaded_file)
            st.success("Data loaded successfully!")

            df = add_features(df)

            emp_id_col = next((c for c in df.columns if "Fake" in c or "ID" in c), None)
            account_col = next((c for c in df.columns if "Account" in c), None)

            if not emp_id_col:
                st.error("Employee ID column not found. Please ensure your file has a column with 'Fake' or 'ID' in the name.")
                return
            if not account_col:
                st.error("Account column not found. Please ensure your file has a column named 'Account'.")
                return

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return

        # --- Tabs for Employee vs Org view ---
        tab1, tab2 = st.tabs(["🔎 Employee View", "🏢 Organization View"])

        with tab1:
            emp_id = st.text_input("Enter Employee ID")
            if emp_id:
                if emp_id not in df[emp_id_col].astype(str).values:
                    st.error("Employee ID not found in data")
                else:
                    emp_data = df[df[emp_id_col].astype(str) == emp_id].iloc[0]

                    designation_col = next((c for c in df.columns if "Designation" in c), None)
                    recruit_col = next((c for c in df.columns if "Recruitment" in c), None)

                    show_employee_summary(emp_data, designation_col, recruit_col, account_col)

                    st.subheader("📌 Next Best Action")
                    recs = generate_recommendation(emp_data)
                    for r in recs:
                        st.write("- ", r)

                    # Download summary
                    st.download_button(
                        label="⬇️ Download Employee Summary",
                        data=str(emp_data.to_dict()) + "\nRecommendations:\n" + "\n".join(recs),
                        file_name=f"{emp_id}_summary.txt",
                        mime="text/plain"
                    )

        with tab2:
            account_choice = st.selectbox("Select Account", df[account_col].dropna().unique())
            if account_choice:
                df_account = df[df[account_col] == account_choice]
                show_org_summary(df_account, account_choice)

if __name__ == "__main__":
    main()
