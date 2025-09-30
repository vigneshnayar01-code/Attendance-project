import numpy as np

def generate_recommendation(row, thresholds=None):
    """
    row: pd.Series representing single employee row
    thresholds: dict with keys:
       - burnout_hours (float)
       - punctuality_hours (float)
       - break_utilization (float)
       - absenteeism (float)
    """
    if thresholds is None:
        thresholds = {
            "burnout_hours": 10.5,
            "punctuality_hours": 2.0,
            "break_utilization": 0.2,
            "absenteeism": 10
        }

    recs = []

    def safe_get(k):
        try:
            v = row.get(k, None)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return None
            return v
        except Exception:
            return None

    office = safe_get("Office_hr_hours")
    punctuality = safe_get("Punctuality")
    break_util = safe_get("Break_Utilization")
    absenteeism = safe_get("Absenteeism")

    # Burnout
    if office is not None and office > thresholds["burnout_hours"]:
        recs.append(f"⚠️ Possible burnout (avg {office:.2f} hrs). Review workload distribution / consider rotation.")

    # Punctuality
    if punctuality is not None and punctuality > thresholds["punctuality_hours"]:
        recs.append(f"⚠️ Frequent late arrivals (avg {punctuality:.2f} hrs off). Coaching on time discipline recommended.")

    # Break utilization
    if break_util is not None and break_util > thresholds["break_utilization"]:
        recs.append(f"⚠️ High break/cafeteria usage ({break_util:.2%} of office time). Consider engagement checks or time management training.")

    # Absenteeism
    if absenteeism is not None and absenteeism > thresholds["absenteeism"]:
        recs.append(f"⚠️ High absenteeism ({absenteeism} days). HR discussion needed.")

    # Unbilled / Unallocated detection (generic columns)
    unbilled_col = next((c for c in row.index if "unbilled" in c.lower()), None)
    unalloc_col = next((c for c in row.index if "unalloc" in c.lower()), None)

    if unbilled_col and isinstance(row.get(unbilled_col, ""), str) and row.get(unbilled_col, "").strip().lower() == "unbilled":
        recs.append("⚠️ Resource shows as Unbilled — consider cross-account allocation or billing follow-up.")

    if unalloc_col and isinstance(row.get(unalloc_col, ""), str) and row.get(unalloc_col, "").strip().lower() in ("yes", "true", "1"):
        recs.append("⚠️ Resource unallocated — consider alternate deployment or assignment.")

    # If nothing flagged -> positive note
    if not recs:
        recs.append("✅ Balanced attendance and work discipline. Candidate for recognition / no immediate action required.")

    return recs
