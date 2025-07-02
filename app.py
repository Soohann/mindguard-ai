import streamlit as st
import re

st.set_page_config(page_title="MindGuard", layout="centered")

st.title("🧠 MindGuard")
st.subheader("AI-Powered Burnout Detection for Students")
st.markdown("---")
st.markdown("Welcome! MindGuard helps you check in with your mental wellness and offers guidance to help prevent burnout. All data is anonymous.")

st.markdown("## 🌡️ Daily Wellness Check-In")
st.caption("Use the sliders to reflect on your current state (1 = low, 5 = high).")

def get_emoji(slider_name, value):
    emojis = {
        "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
        "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
        "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
        "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
        "energy": {1: "🥱", 2: "😪", 3: "😐", 4: "😊", 5: "🤩"},
        "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
        "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
        "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"},
    }
    return emojis[slider_name][value]

# ----------- ADVANCED FEEDBACK SYSTEM ------------
def advanced_feedback(
    mood, stress, focus, sleep, energy, motivation, anxiety, appetite
):
    feedback = []

    # 1. Red Flag: Multiple lows
    criticals = [mood, focus, sleep, energy, motivation]
    n_crit_low = sum(v <= 2 for v in criticals)
    if n_crit_low >= 3:
        feedback.append("🚩 Multiple areas are low. Please consider talking to a counselor or trusted person—you’re not alone.")

    # 2. Key combos (ordered by importance)
    if stress >= 4 and sleep <= 2:
        feedback.append("High stress and poor sleep—try winding down early and limit screens before bed.")
    if mood >= 4 and focus <= 2:
        feedback.append("Good mood but low focus? Try a quick mindfulness break or set a tiny, clear goal.")
    if energy <= 2 and anxiety >= 4:
        feedback.append("Low energy and high anxiety—gentle movement like a short walk can help.")
    if motivation <= 2 and appetite <= 2:
        feedback.append("Low motivation and low appetite—give yourself permission to take it easy and reach out if needed.")
    if appetite <= 2 and stress >= 4:
        feedback.append("Poor appetite and high stress: regular, small snacks and hydration can help.")
    if sleep <= 2 and energy <= 2:
        feedback.append("Very low sleep and energy: try to rest, even if it’s a short nap.")
    if anxiety >= 4 and sleep <= 2:
        feedback.append("High anxiety and poor sleep—try calming routines before bed.")
    if motivation <= 2 and mood <= 2:
        feedback.append("Both mood and motivation are low. Start with a small, easy win.")
    if stress >= 4 and anxiety >= 4:
        feedback.append("High stress and anxiety—try breathing exercises or grounding techniques.")
    if mood >= 4 and stress >= 4:
        feedback.append("Positive mood even under stress—keep using your coping skills!")

    # 3. Individual sliders (short tips)
    if mood <= 2:
        feedback.append("Mood is low—small pleasures or talking to a friend might help.")
    elif mood >= 4:
        feedback.append("Great mood! Keep nurturing it with things you enjoy.")
    if stress >= 4:
        feedback.append("High stress: take 5 minutes to breathe deeply or walk.")
    elif stress <= 2:
        feedback.append("Low stress—good job managing your workload.")
    if focus <= 2:
        feedback.append("Focus is low—try a distraction-free work block or Pomodoro technique.")
    elif focus >= 4:
        feedback.append("High focus—this is a good time for important work.")
    if sleep <= 2:
        feedback.append("Very poor sleep—rest tonight if you can.")
    elif sleep >= 4:
        feedback.append("Great sleep—good rest helps everything.")
    if energy <= 2:
        feedback.append("Low energy: hydrate, stretch, and get fresh air.")
    elif energy >= 4:
        feedback.append("High energy! Channel it into something fun or productive.")
    if motivation <= 2:
        feedback.append("Motivation is low—set a super-easy task to build momentum.")
    elif motivation >= 4:
        feedback.append("Highly motivated! Use that drive on your priorities.")
    if anxiety >= 4:
        feedback.append("Anxiety is high—try breathing exercises or talk to someone.")
    elif anxiety <= 2:
        feedback.append("Low anxiety—keep up your calming routines.")
    if appetite <= 2:
        feedback.append("Low appetite—don’t skip meals; small snacks can help.")
    elif appetite >= 4:
        feedback.append("Strong appetite—opt for nourishing, balanced meals.")
    elif appetite == 3:
        feedback.append("Balanced appetite—this is a good wellness sign.")

    # 4. All thriving
    if (
        all(v >= 4 for v in [mood, sleep, energy, motivation])
        and stress <= 2
        and anxiety <= 2
        and focus >= 4
        and appetite == 3
    ):
        feedback.append("🌱 You're thriving across all areas! Keep up your healthy habits.")

    # 5. Catch-all
    if not feedback:
        feedback.append("Your responses look balanced today. Keep prioritizing your well-being!")

    # Only show the top 2 unique, nonempty feedbacks
    shown = []
    for tip in feedback:
        if tip not in shown:
            shown.append(tip)
        if len(shown) == 2:
            break

    st.info(" ".join(shown))
# ----------- END ADVANCED FEEDBACK SYSTEM ------------

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {get_emoji('mood', st.session_state.get('mood', 3))} Mood")
    mood = st.slider("", 1, 5, 3, key="mood", label_visibility="collapsed", help="1 = Very bad, 5 = Excellent")

    st.markdown(f"### {get_emoji('stress', st.session_state.get('stress', 3))} Stress")
    stress = st.slider("", 1, 5, 3, key="stress", label_visibility="collapsed", help="1 = No stress, 5 = Extreme stress")

    st.markdown(f"### {get_emoji('focus', st.session_state.get('focus', 3))} Focus")
    focus = st.slider("", 1, 5, 3, key="focus", label_visibility="collapsed", help="1 = Can't focus, 5 = Fully focused")
    
    st.markdown(f"### {get_emoji('motivation', st.session_state.get('motivation', 3))} Motivation")
    motivation = st.slider("", 1, 5, 3, key="motivation", label_visibility="collapsed", help="1 = No motivation, 5 = Highly motivated")

with col2:
    st.markdown(f"### {get_emoji('sleep', st.session_state.get('sleep', 3))} Sleep Quality")
    sleep = st.slider("", 1, 5, 3, key="sleep", label_visibility="collapsed", help="1 = Very poor, 5 = Well-rested")

    st.markdown(f"### {get_emoji('energy', st.session_state.get('energy', 3))} Energy Level")
    energy = st.slider("", 1, 5, 3, key="energy", label_visibility="collapsed", help="1 = Exhausted, 5 = Very energetic")

    st.markdown(f"### {get_emoji('anxiety', st.session_state.get('anxiety', 3))} Anxiety")
    anxiety = st.slider("", 1, 5, 3, key="anxiety", label_visibility="collapsed", help="1 = Calm, 5 = Extremely anxious")

    st.markdown(f"### {get_emoji('appetite', st.session_state.get('appetite', 3))} Appetite")
    appetite = st.slider("", 1, 5, 3, key="appetite", label_visibility="collapsed", help="1 = Poor appetite, 5 = Very strong appetite")

st.markdown("## 📝 Optional Journal Entry")
journal = st.text_area("How are you feeling today?", placeholder="E.g., I'm feeling a bit overwhelmed but trying to stay focused.")

st.markdown("---")
if st.button("✅ Submit Check-In"):
    if (mood == stress == focus == sleep == energy == motivation == anxiety == appetite == 3):
        st.warning("It looks like you haven't updated any inputs. Please adjust them to reflect your current state.")
    else:
        st.success("✅ Check-in submitted!")

        stress_score = 6 - stress
        anxiety_score = 6 - anxiety
        appetite_score = 3 - abs(appetite - 3)
        wellness_score = (
            mood + stress_score + focus + sleep + energy + motivation + anxiety_score + appetite_score
        ) / 8

        if wellness_score >= 4.0:
            burnout = "Low"
        elif wellness_score >= 2.5:
            burnout = "Moderate"
        else:
            burnout = "High"

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

        # -------- CALL THE ADVANCED FEEDBACK FUNCTION HERE --------
        advanced_feedback(mood, stress, focus, sleep, energy, motivation, anxiety, appetite)

        if journal.strip():
            def override_emotion_with_negation(text):
                text = text.lower()
                if re.search(r"not[\s\w]*sad", text):
                    return {"label": "neutral", "score": 1.0}
                elif re.search(r"not[\s\w]*happy", text) or re.search(r"not[\s\w]*good", text):
                    return {"label": "sadness", "score": 0.9}
                elif re.search(r"not[\s\w]*stressed", text):
                    return {"label": "calm", "score": 0.95}
                return None

            from transformers import pipeline

            with st.spinner("Analyzing your journal entry..."):
                emotion_pipeline = pipeline(
                    "text-classification", 
                    model="bhadresh-savani/distilbert-base-uncased-emotion", 
                    return_all_scores=True)
                override = override_emotion_with_negation(journal)
                if override:
                    top_emotion = override
                else:
                    result = emotion_pipeline(journal)[0]
                    sorted_result = sorted(result, key=lambda x: x['score'], reverse=True)
                    top_emotion = sorted_result[0]

            st.markdown("#### 📝 Emotion Analysis")
            st.markdown(f"**Detected Emotion:** {top_emotion['label']} (confidence: {top_emotion['score']:.2f})")

st.markdown("---")
st.caption("🔒 Your data stays private. No names, IDs, or personal information are stored.")
