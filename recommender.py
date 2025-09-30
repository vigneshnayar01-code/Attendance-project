# recommender.py
def generate_recommendation(row):
    recs = []

    # Burnout
    if row.get('Office_hr_hours', 0) > 10.5:
        recs.append("⚠️ Possible burnout: review workload distribution.")

    # Punctuality
    if row.get('Punctuality', 0) > 2:
        recs.append("⚠️ Frequent late arrivals: coaching needed on time discipline.")

    # Inefficiency
    if row.get('Break_Utilization', 0) > 0.2:
        recs.append("⚠️ High break/cafeteria usage: review engagement.")

    # Absenteeism
    if row.get('Absenteeism', 0) > 10:
        recs.append("⚠️ High absenteeism: have discussion with employee.")

    # Unbilled / Unallocated
    unbilled_col = next((c for c in row.index if "Unbilled" in c), None)
    unalloc_col = next((c for c in row.index if "Unalloc" in c), None)

    if unbilled_col and str(row[unbilled_col]).lower() == "unbilled":
        recs.append("⚠️ Resource unbilled: consider cross-account allocation.")

    if unalloc_col and str(row[unalloc_col]).lower() == "yes":
        recs.append("⚠️ Resource unallocated: consider alternate deployment.")

    # Positive case
    if not recs:
        recs.append("✅ Balanced attendance and work discipline. Candidate for recognition.")

    return recs
