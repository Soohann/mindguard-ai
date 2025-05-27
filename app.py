import streamlit as st

st.set_page_config(page_title="MindGuard", layout="centered")
st.title("🧠 MindGuard")
st.subheader("AI-Powered Burnout Detection for Students")

st.markdown("Please complete your daily wellness check-in below:")

mood = st.slider("Mood", 1, 5, 3)
stress = st.slider("Stress", 1, 5, 3)
focus = st.slider("Focus", 1, 5, 3)


sleep = st.slider("Sleep Quality", 1, 5, 3)
energy = st.slider("Energy Level", 1, 5, 3)

journal = st.text_area("Optional: How are you feeling today?")

if st.button("Submit Check-In"):
    st.success("✅ Check-in submitted!")
    st.markdown("### Burnout Risk: **Moderate**")
    st.markdown("### Suggested Resources:\n- Academic Coaching\n- Counseling Services\n- Vandal Success Center")
