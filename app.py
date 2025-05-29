import streamlit as st

# Setup
st.set_page_config(page_title="MindGuard", layout="centered")

# Header
st.title("🧠 MindGuard")
st.subheader("AI-Powered Burnout Detection for Students")
st.markdown("---")

st.markdown("Welcome! MindGuard helps you check in with your mental wellness and offers guidance to help prevent burnout. All data is anonymous.")

# Sliders Section
st.markdown("## 🌡️ Daily Wellness Check-In")
st.caption("Use the sliders to reflect on your current state (1 = low, 5 = high).")

col1, col2 = st.columns(2)

with col1:
    mood = st.slider("🙂 Mood", 1, 5, 3, help="1 = Very bad, 5 = Excellent")
    stress = st.slider("😣 Stress", 1, 5, 3, help="1 = No stress, 5 = Extreme stress")
    focus = st.slider("🎯 Focus", 1, 5, 3, help="1 = Can't focus, 5 = Fully focused")

with col2:
    sleep = st.slider("💤 Sleep Quality", 1, 5, 3, help="1 = Very poor, 5 = Well-rested")
    energy = st.slider("⚡ Energy Level", 1, 5, 3, help="1 = Exhausted, 5 = Very energetic")

# Journal
st.markdown("## 📝 Optional Journal Entry")
journal = st.text_area("How are you feeling today?", placeholder="E.g., I'm feeling a bit overwhelmed but trying to stay focused.")

# Submission
st.markdown("---")
if st.button("✅ Submit Check-In"):
    # Guard against unchanged inputs
    if mood == stress == focus == sleep == energy == 3:
        st.warning("It looks like you haven't updated any inputs. Please adjust them to reflect your current state.")
    else:
        st.success("✅ Check-in submitted!")

        # Logic
        stress_score = 6 - stress
        wellness_score = (mood + stress_score + focus + sleep + energy) / 5

        if wellness_score >= 4.0:
            burnout = "Low"
        elif wellness_score >= 2.5:
            burnout = "Moderate"
        else:
            burnout = "High"

        # Results
        st.markdown(f"### 🔥 Burnout Risk Level: **{burnout}**")

        st.markdown("#### 🎯 Suggested Campus Resources")
        if burnout == "High":
            st.markdown("**🧠 [Counseling Services](https://www.uidaho.edu/current-students/cmhc)**  \nFree short-term counseling, mental health support.")
            st.markdown("**📘 [TRIO Student Support Services](https://www.uidaho.edu/current-students/academic-support/asp/sss)**  \nAcademic advising, tutoring, and life coaching for eligible students.")
            st.markdown("**🏛️ [Vandal Success Center](https://www.uidaho.edu/current-students/academic-support/asp)**  \nHelp with tutoring, time management, and academic skills.")
        elif burnout == "Moderate":
            st.markdown("- 📚 Academic Coaching\n- 🧘 Mindfulness Workshops\n- 📎 Tutoring Services")
        else:
            st.markdown("- 🎉 Keep up the great work!\n- 🤝 Peer Mentoring\n- 🗣️ Join a wellness event")

# Footer
st.markdown("---")
st.caption("🔒 Your data stays private. No names, IDs, or personal information are stored.")
