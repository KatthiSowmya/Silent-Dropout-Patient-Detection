import streamlit as st
import pandas as pd

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Silent Dropout Risk Prediction",
    layout="wide"
)

st.title("🩺 Silent Dropout Risk Prediction System")
st.write(
    "This application calculates the **Silent Dropout Score mathematically** "
    "using patient follow-up and engagement data, and then "
    "derives the **Risk Level (Low / Medium / High)**."
)

st.markdown("---")

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def normalize(val, max_val):
    """Normalize value between 0 and 1 with cap"""
    return min(val / max_val, 1.0)


def calculate_dropout_score(inputs):
    """
    FINAL DATASET-ALIGNED DROPOUT SCORE (0–100)
    """

    # Normalize risk-driving features
    late_follow = normalize(inputs["Late_Follow"], 50)
    refill_delay = normalize(inputs["Refill_Delay"], 60)
    since_last = normalize(inputs["Since_Last_Applied"], 90)
    missed_labs = normalize(inputs["Missed_Lab_Tests"], 10)
    p_between = normalize(inputs["p_Between"], 60)
    team_calls = normalize(inputs["Team_Calls"], 10)

    replied = 1 if inputs["Response"] == "Yes" else 0

    # Base risk score (major drivers)
    score = (
        0.25 * late_follow +
        0.25 * refill_delay +
        0.20 * since_last +
        0.10 * missed_labs +
        0.10 * p_between
    )

    # Engagement logic (CRITICAL)
    if replied == 1:
        score -= 0.10                 # reply reduces risk
        score -= 0.10 * team_calls    # calls + reply = good engagement
    else:
        score += 0.10                 # no reply penalty
        score += 0.15 * team_calls    # calls ignored = higher risk

    # Scale to 0–100 and cap
    dropout_score = max(0, min(score * 100, 100))

    return round(dropout_score, 2)


def map_risk_level(score):
    """Map score to risk label (updated to match dataset)"""
    if score < 35:
        return "Low"
    elif score < 60:
        return "Medium"
    else:
        return "High"


# -------------------------------------------------
# Input Section
# -------------------------------------------------
st.subheader("📥 Enter Patient Details")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=40)
    gender = st.selectbox("Gender", ["Male", "Female"])
    p_between = st.number_input("Expected Gap Between Visits (days)", min_value=0, value=30)
    late_follow = st.number_input("Days Late for Follow-Up", min_value=0, value=10)
    refill_delay = st.number_input("Medicine Refill Delay (days)", min_value=0, value=10)
    refill_source = st.selectbox("Refill Source", ["Hospital", "Online", "Local"])

with col2:
    since_last_applied = st.number_input(
        "Days Since Last Contact",
        min_value=0,
        value=30
    )
    missed_lab_tests = st.number_input(
        "Missed Lab Tests",
        min_value=0,
        value=1
    )
    team_calls = st.number_input(
        "Care Team Calls Made",
        min_value=0,
        value=2
    )
    response = st.selectbox(
        "Patient Replied to Last Contact",
        ["Yes", "No"]
    )

st.markdown("---")

# -------------------------------------------------
# Prediction
# -------------------------------------------------
if st.button("🔮 Calculate Dropout Score & Risk Level"):

    inputs = {
        "p_Between": p_between,
        "Late_Follow": late_follow,
        "Refill_Delay": refill_delay,
        "Since_Last_Applied": since_last_applied,
        "Missed_Lab_Tests": missed_lab_tests,
        "Team_Calls": team_calls,
        "Response": response
    }

    dropout_score = calculate_dropout_score(inputs)
    risk_level = map_risk_level(dropout_score)

    st.subheader("📊 Prediction Results")

    st.success(f"**Silent Dropout Score:** {dropout_score}")

    if risk_level == "Low":
        st.success("🟢 **Risk Level: LOW**")
    elif risk_level == "Medium":
        st.warning("🟡 **Risk Level: MEDIUM**")
    else:
        st.error("🔴 **Risk Level: HIGH**")

# -------------------------------------------------
# Explanation section
# -------------------------------------------------
st.markdown("---")
st.subheader("ℹ️ How the Score is Calculated")

st.markdown(
"""
### Major Risk Drivers
- ⏱ **Late follow-ups**
- 💊 **Refill delays**
- 📆 **Days since last contact**
- 🧪 **Missed lab tests**

### Engagement Logic (Most Important)
- ✅ **Replied + more team calls → risk decreases**
- ❌ **No reply + more team calls → risk increases**

### Final Output
- Score scaled to **0–100**
- Risk Levels:
  - **<35 → Low**
  - **35–59 → Medium**
  - **≥60 → High**
"""
)

st.caption("Rule-based, explainable, dataset-validated | Silent Dropout Prediction System")
