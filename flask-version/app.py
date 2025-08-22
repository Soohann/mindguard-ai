from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import os

EMOTION_PIPELINE = None
USE_EMOTION = os.getenv("USE_EMOTION", "0") in ("1", "true", "True")

app = Flask(__name__)
CORS(app)

# Emoji mappings for different wellness metrics (Energy removed)
EMOJIS = {
    "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
    "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
    "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
    "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
    "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
    "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
    "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"},
    "food_security": {1: "🍽️", 2: "🥪", 3: "🙂", 4: "🧺", 5: "💳"}
}

def calculate_wellness_score(data):
    """Calculate overall wellness score from user inputs (Energy removed; divide by 8)."""
    mood = data['mood']
    stress = data['stress']
    focus = data['focus']
    sleep = data['sleep']
    motivation = data['motivation']
    anxiety = data['anxiety']
    appetite = data['appetite']
    food_security = data.get('food_security', 3)

    # Reverse scoring for negative metrics
    stress_score = 6 - stress
    anxiety_score = 6 - anxiety
    # Appetite: center at 3 is best (your current 0–3 mapping retained)
    appetite_score = 3 - abs(appetite - 3)

    # Calculate average wellness score across 8 metrics
    wellness_score = (
        mood + stress_score + focus + sleep +
        motivation + anxiety_score + appetite_score + food_security
    ) / 8

    return wellness_score

def get_burnout_level(wellness_score):
    """Determine burnout risk level based on wellness score"""
    if wellness_score >= 4.0:
        return "Low"
    elif wellness_score >= 2.5:
        return "Moderate"
    else:
        return "High"

def get_resources(burnout_level, data=None):
    """Campus resources; adds food support if food_security is low."""
    resources = {
        "High": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {"name": "🧠 Counseling Services", "url": "https://www.uidaho.edu/current-students/cmhc",
                 "description": "Free short-term counseling, mental health support."},
                {"name": "📘 TRIO Student Support Services", "url": "https://www.uidaho.edu/current-students/academic-support/asp/sss",
                 "description": "Academic advising, tutoring, and life coaching for eligible students."},
                {"name": "🏛️ Vandal Success Center", "url": "https://www.uidaho.edu/current-students/academic-support/asp",
                 "description": "Help with tutoring, time management, and academic skills."},
            ]
        },
        "Moderate": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {"name": "📚 Academic Coaching", "description": ""},
                {"name": "🧘 Mindfulness Workshops", "description": ""},
                {"name": "📎 Tutoring Services", "description": ""},
            ]
        },
        "Low": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {"name": "🎉 Keep up the great work!", "description": ""},
                {"name": "🤝 Peer Mentoring", "description": ""},
                {"name": "🗣️ Join a wellness event", "description": ""},
            ]
        }
    }

    out = resources.get(burnout_level, resources["Moderate"])

    # Add food support card if relevant
    if data and data.get("food_security", 3) <= 2:
        out = dict(out)  # shallow copy
        out.setdefault("items", [])
        out["items"].insert(0, {
            "name": "🍽️ Vandal Food Pantry & Food Resources",
            "url": "https://www.uidaho.edu/current-students/dean-of-students/student-care/food-insecurity",
            "description": "Free groceries and support if money/food is tight."
        })
    return out

def generate_advanced_feedback(data):
    """Generate personalized feedback based on user inputs (Energy removed)."""
    feedback = []

    mood = data['mood']
    stress = data['stress']
    focus = data['focus']
    sleep = data['sleep']
    motivation = data['motivation']
    anxiety = data['anxiety']
    appetite = data['appetite']
    food_security = data.get('food_security', 3)

    # 1. Red Flag: Multiple lows
    criticals = [mood, focus, sleep, motivation]
    n_crit_low = sum(1 for v in criticals if v <= 2)
    if n_crit_low >= 3:
        feedback.append("🚩 Multiple areas are low. Please consider talking to a counselor or trusted person—you're not alone.")

    # 2. Key combos (ordered by importance)
    if stress >= 4 and sleep <= 2:
        feedback.append("High stress and poor sleep—try winding down early and limit screens before bed.")
    if mood >= 4 and focus <= 2:
        feedback.append("Good mood but low focus? Try a quick mindfulness break or set a tiny, clear goal.")
    if motivation <= 2 and appetite <= 2:
        feedback.append("Low motivation and low appetite—give yourself permission to take it easy and reach out if needed.")
    if appetite <= 2 and stress >= 4:
        feedback.append("Poor appetite and high stress: regular, small snacks and hydration can help.")
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

    if motivation <= 2:
        feedback.append("Motivation is low—set a super-easy task to build momentum.")
    elif motivation >= 4:
        feedback.append("Highly motivated! Use that drive on your priorities.")

    if anxiety >= 4:
        feedback.append("Anxiety is high—try breathing exercises or talk to someone.")
    elif anxiety <= 2:
        feedback.append("Low anxiety—keep up your calming routines.")

    if appetite <= 2:
        feedback.append("Low appetite—don't skip meals; small snacks can help.")
    elif appetite >= 4:
        feedback.append("Strong appetite—opt for nourishing, balanced meals.")
    elif appetite == 3:
        feedback.append("Balanced appetite—this is a good wellness sign.")

    # 4. All thriving (Energy removed)
    if (all(v >= 4 for v in [mood, sleep, motivation]) and
        stress <= 2 and anxiety <= 2 and focus >= 4 and appetite == 3 and food_security >= 4):
        feedback.append("🌱 You're thriving across all areas! Keep up your healthy habits.")

    # 5. Catch-all
    if not feedback:
        feedback.append("Your responses look balanced today. Keep prioritizing your well-being!")

    # 3b. Food security (optional slider)
    if food_security is not None:
        if food_security <= 2:
            feedback.append(
                "If money is tight for meals, you’re not alone—please consider campus and local resources that can help with groceries or meal support."
            )
        elif food_security == 3:
            feedback.append("Food budget feels tight—planning simple, low-cost meals might reduce stress.")
        elif food_security >= 4:
            feedback.append("Great that your food budget feels okay—keeping easy, nourishing snacks handy can support energy.")

    # Return top 2 unique feedback items
    unique_feedback = []
    for tip in feedback:
        if tip not in unique_feedback:
            unique_feedback.append(tip)
        if len(unique_feedback) == 2:
            break

    final_feedback = " ".join(unique_feedback)

    # Always add Farmers Market suggestion if appetite is low
    if appetite <= 2:
        farmers_market_message = (
            " 🍎 Looking for ways to gently boost your appetite? "
            "Try exploring the <a href='https://www.ci.moscow.id.us/197/Community-Events-Moscow-Farmers-Market' "
            "target='_blank' rel='noopener noreferrer'>Moscow Farmers Market</a> — a lively Saturday morning event in downtown Moscow "
            "filled with local produce, artisan foods, and friendly faces. Open May–October, 8:00 AM to 1:00 PM."
        )
        final_feedback += " " + farmers_market_message

    return final_feedback

def analyze_journal_emotion(journal_text):
    """Emotion analysis with negation overrides; lazily load transformer."""
    txt = (journal_text or "").strip()
    if not txt or not USE_EMOTION:
        return None

    try:
        low = txt.lower()
        if re.search(r"not[\s\w]*sad", low):
            return {"emotion": "neutral", "confidence": 1.0}
        if re.search(r"not[\s\w]*(happy|good)", low):
            return {"emotion": "sadness", "confidence": 0.9}
        if re.search(r"not[\s\w]*stressed", low):
            return {"emotion": "calm", "confidence": 0.95}

        global EMOTION_PIPELINE
        if EMOTION_PIPELINE is None:
            from transformers import pipeline
            EMOTION_PIPELINE = pipeline(
                "text-classification",
                model="bhadresh-savani/distilbert-base-uncased-emotion",
                return_all_scores=True
            )

        result = EMOTION_PIPELINE(txt)[0]
        top = max(result, key=lambda x: x['score'])
        return {"emotion": top['label'], "confidence": float(top['score'])}
    except Exception as e:
        print(f"[emotion] error: {e}")
        return {"emotion": "neutral", "confidence": 0.5}

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit_checkin():
    """Process wellness check-in submission"""
    try:
        data = request.get_json()

        # Validate that all required fields are present (Energy removed)
        required_fields = ['mood', 'stress', 'focus', 'sleep', 'motivation', 'anxiety', 'appetite', 'food_security']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Check if all values are default (3)
        all_default = all(data[field] == 3 for field in required_fields)
        if all_default:
            return jsonify({
                'error': 'It looks like you haven\'t updated any inputs. Please adjust them to reflect your current state.',
                'type': 'validation'
            }), 400

        # Calculate wellness metrics
        wellness_score = calculate_wellness_score(data)
        burnout_level = get_burnout_level(wellness_score)
        resources = get_resources(burnout_level, data)
        feedback = generate_advanced_feedback(data)

        # Analyze journal if provided
        emotion_analysis = None
        if 'journal' in data and data['journal'].strip():
            emotion_analysis = analyze_journal_emotion(data['journal'])

        # Prepare response
        response = {
            'success': True,
            'wellness_score': round(wellness_score, 2),
            'burnout_level': burnout_level,
            'resources': resources,
            'feedback': feedback,
            'emotion_analysis': emotion_analysis
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emojis')
def get_emojis():
    """Get emoji mappings for frontend"""
    return jsonify(EMOJIS)

@app.route('/health')
def health():
    return jsonify({"ok": True}), 200

if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port)
