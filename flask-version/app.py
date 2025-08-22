from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import os
import hashlib
from datetime import date

EMOTION_PIPELINE = None
USE_EMOTION = os.getenv("USE_EMOTION", "0") in ("1", "true", "True")

app = Flask(__name__)
CORS(app)

# ---------- Constants
VANDAL_LINKS = {
    "athletics": "https://govandals.com",
    "swim": "https://www.uidaho.edu/recreation/swim-center",
    "rec": "https://www.uidaho.edu/recreation/rec-center",
}

# Emoji mappings for different wellness metrics
EMOJIS = {
    "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
    "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
    "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
    "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
    "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
    "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
    "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"},
    "food_security": {1: "🍽️", 2: "🥪", 3: "🙂", 4: "🧺", 5: "💳"},
}

# ---------- Helpers for varied text
def _pick(items, seed_key):
    """Deterministic picker for variety (stable per day + payload)."""
    if not items:
        return ""
    seed = int(hashlib.md5(seed_key.encode()).hexdigest(), 16)
    return items[seed % len(items)]

def _has(txt, *words):
    low = (txt or "").lower()
    return any(w in low for w in words)

# ---------- Scoring
def calculate_wellness_score(data):
    """Calculate overall wellness score from user inputs (average of 8 metrics)."""
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
    # Appetite: center at 3 is best → 0..3 scale
    appetite_score = 3 - abs(appetite - 3)

    wellness_score = (
        mood + stress_score + focus + sleep +
        motivation + anxiety_score + appetite_score + food_security
    ) / 8

    return wellness_score

def get_burnout_level(wellness_score):
    """Determine burnout risk level based on wellness score."""
    if wellness_score >= 4.0:
        return "Low"
    elif wellness_score >= 2.5:
        return "Moderate"
    else:
        return "High"

# ---------- Resources
def get_resources(burnout_level, data=None):
    VANDAL_LINKS = {
        "athletics": "https://govandals.com",
        "swim": "https://www.uidaho.edu/recreation/swim-center",
        "rec": "https://www.uidaho.edu/recreation/rec-center"
    }

    resources = {"title": "🎯 Suggested Campus Resources", "items": []}

    if burnout_level == "High":
        resources["items"].extend([
            {"name": "🧠 Counseling Services", "url": "https://www.uidaho.edu/current-students/cmhc",
             "description": "Free short-term counseling and mental health support."},
            {"name": "📘 TRIO Student Support Services", "url": "https://www.uidaho.edu/current-students/academic-support/asp/sss",
             "description": "Academic advising, tutoring, and life coaching for eligible students."},
            {"name": "🏛️ Vandal Success Center", "url": "https://www.uidaho.edu/current-students/academic-support/asp",
             "description": "Tutoring, time management, and academic skills help."},
        ])

    elif burnout_level == "Moderate":
        # Conditional adds
        if data:
            if data.get("stress", 3) >= 4 or data.get("anxiety", 3) >= 4:
                resources["items"].append({"name": "🧘 Mindfulness Workshops",
                                           "description": "Practical tools for stress & anxiety."})
            if data.get("focus", 3) <= 2 or data.get("sleep", 3) <= 2:
                resources["items"].append({"name": "📎 Tutoring Services",
                                           "description": "Extra support for challenging classes."})
            if data.get("motivation", 3) <= 2:
                resources["items"].append({"name": "📚 Academic Coaching",
                                           "description": "Accountability and strategies for staying on track."})

        # Add positive engagement
        resources["items"].extend([
            {"name": "🏋️ Student Rec Center", "url": VANDAL_LINKS["rec"],
             "description": "Gym, sports courts, and rock climbing wall."},
            {"name": "🏊 Swim Center (free with student ID)", "url": VANDAL_LINKS["swim"],
             "description": "Refresh yourself at open swim hours."}
        ])

    elif burnout_level == "Low":
        resources["items"].extend([
            {"name": "🎉 Keep up the great work!", "description": "Stay balanced and enjoy yourself."},
            {"name": "🏈 Vandal Athletics", "url": VANDAL_LINKS["athletics"],
             "description": "Check schedules for football, basketball, volleyball and more."},
            {"name": "🤝 Peer Mentoring", "description": "Support others and build connections."},
            {"name": "🏋️ Student Rec Center", "url": VANDAL_LINKS["rec"],
             "description": "Stay active with gym, games, or climbing."},
        ])

    # Food support if needed
    if data and data.get("food_security", 3) <= 2:
        resources["items"].insert(0, {
            "name": "🍽️ Vandal Food Pantry & Food Resources",
            "url": "https://www.uidaho.edu/current-students/dean-of-students/student-care/food-insecurity",
            "description": "Free groceries and support if money/food is tight."
        })

    # Cap at 4 items → keep it short and relevant
    resources["items"] = resources["items"][:4]

    return resources


# ---------- Feedback
def generate_advanced_feedback(data, emotion=None):
    """
    Build short, varied, targeted feedback based on slider signals + journal.
    Returns 2–4 sentences, plus Farmers Market suggestion when appetite is low.
    """
    mood = data['mood']
    stress = data['stress']
    focus = data['focus']
    sleep = data['sleep']
    motivation = data['motivation']
    anxiety = data['anxiety']
    appetite = data['appetite']
    food_security = data.get('food_security', 3)
    journal = (data.get('journal') or "").strip()

    hi = lambda v: v >= 4
    lo = lambda v: v <= 2
    ok = lambda v: v == 3

    signals = {
        "mood_hi": hi(mood), "mood_lo": lo(mood),
        "stress_hi": hi(stress), "stress_lo": lo(stress),
        "focus_hi": hi(focus), "focus_lo": lo(focus),
        "sleep_hi": hi(sleep), "sleep_lo": lo(sleep),
        "motivation_hi": hi(motivation), "motivation_lo": lo(motivation),
        "anxiety_hi": hi(anxiety), "anxiety_lo": lo(anxiety),
        "appetite_hi": hi(appetite), "appetite_lo": lo(appetite), "appetite_ok": ok(appetite),
        "food_low": food_security <= 2,
    }

    # Priority care if multiple core areas low
    core = [mood, focus, sleep, motivation]
    priority = []
    if sum(1 for v in core if v <= 2) >= 3:
        priority.append(_pick([
            "🚩 Several areas look tough today. Consider reaching out to a counselor or a trusted person—support can make things lighter.",
            "🚩 You flagged a few low spots. A quick check-in with campus support or a friend could really help right now."
        ], f"{date.today()}-priority"))

    # Combo tips
    combos = []
    if signals["stress_hi"] and signals["sleep_lo"]:
        combos.append(_pick([
            "High stress + poor sleep—try a gentle wind-down tonight and limit screens 60 minutes before bed.",
            "Stress and sleep are clashing—short breathing sets and a set lights-out time can help."
        ], f"{date.today()}-combo1"))

    if signals["mood_hi"] and signals["focus_lo"]:
        combos.append(_pick([
            "Mood is good but focus is off—try a 20-minute distraction-free block to get rolling.",
            "Feeling upbeat but unfocused—set one tiny, clear task and start there."
        ], f"{date.today()}-combo2"))

    if signals["motivation_lo"] and signals["appetite_lo"]:
        combos.append(_pick([
            "Motivation and appetite are low—take it easy and aim for small, regular snacks.",
            "Low drive + low appetite—be kind to yourself; quick, simple nutrition can help your energy."
        ], f"{date.today()}-combo3"))

    if signals["appetite_lo"] and signals["stress_hi"]:
        combos.append("Poor appetite with high stress—schedule small snacks and hydration breaks.")
    if signals["anxiety_hi"] and signals["sleep_lo"]:
        combos.append("High anxiety and rough sleep—try a calming routine before bed (dim lights, slow breaths).")
    if signals["motivation_lo"] and signals["mood_lo"]:
        combos.append("Motivation and mood are both low—pick a super-small win to start momentum.")
    if signals["stress_hi"] and signals["anxiety_hi"]:
        combos.append("Stress and anxiety are high—2–3 minutes of paced breathing can help ground you.")
    if signals["mood_hi"] and signals["stress_hi"]:
        combos.append("Good mood under stress—keep leaning on the coping skills that are working.")

    # Single-slider tips (short + positive)
    singles = []
    if signals["mood_lo"]:
        singles.append("Mood is low—tiny pleasures or a quick chat with a friend can help.")
    elif signals["mood_hi"]:
        singles.append("Great mood—keep feeding it with things that feel good.")
    if signals["stress_hi"]:
        singles.append("Stress is high—take a 5-minute breathing or stretch break.")
    elif signals["stress_lo"]:
        singles.append("Low stress—nice work pacing your workload.")
    if signals["focus_lo"]:
        singles.append("Focus is low—try a Pomodoro block with notifications off.")
    elif signals["focus_hi"]:
        singles.append("Focus looks strong—tackle a priority while the groove is there.")
    if signals["sleep_lo"]:
        singles.append("Sleep was rough—if possible, plan a wind-down and protect tonight’s rest.")
    elif signals["sleep_hi"]:
        singles.append("Great sleep—everything benefits from that.")
    if signals["motivation_lo"]:
        singles.append("Motivation is low—set a 2-minute starter task.")
    elif signals["motivation_hi"]:
        singles.append("Motivation is high—aim it at your most important task.")
    if signals["anxiety_hi"]:
        singles.append("Anxiety is high—try a short grounding exercise (5-4-3-2-1).")
    elif signals["anxiety_lo"]:
        singles.append("Low anxiety—keep up what’s helping you stay calm.")
    if signals["appetite_lo"]:
        singles.append("Appetite is low—don’t skip meals; light, regular snacks help.")
    elif signals["appetite_hi"]:
        singles.append("Strong appetite—lean into nourishing, balanced meals.")
    elif signals["appetite_ok"]:
        singles.append("Balanced appetite—good sign for steady energy.")

    # Journal-aware nudges
    journal_lines = []
    low = journal.lower()
    if _has(low, "exam", "midterm", "final", "quiz", "deadline", "assignment", "paper"):
        journal_lines.append("Deadlines ahead—map the next small step and a short, focused block.")
    if _has(low, "money", "rent", "bills", "food", "groceries"):
        journal_lines.append("Money stress is heavy—if food feels tight, campus resources can help.")
    if _has(low, "roommate", "conflict", "fight", "argue"):
        journal_lines.append("Roommate tension—try a calm check-in or ask a neutral friend/RA for perspective.")
    if _has(low, "homesick", "lonely", "alone"):
        journal_lines.append("Homesick happens—brief social time or a familiar routine can help.")

    # Emotion tone softener
    if emotion and emotion.get("emotion") in {"sadness", "fear", "anger", "anxiety"} and emotion.get("confidence", 0) > 0.7:
        journal_lines.append("Thanks for sharing—what you're feeling makes sense. Small steps count.")

    # Risk-gated campus suggestion
    wellness_score = calculate_wellness_score(data)
    level = get_burnout_level(wellness_score)
    campus = []
    if level in ("Low", "Moderate"):
        campus_pools = [
            f"Recharge with something fun—check Vandal Athletics at <a href='{VANDAL_LINKS['athletics']}' target='_blank' rel='noopener'>govandals.com</a> and catch a game.",
            f"Swim is free for students during public hours—see <a href='{VANDAL_LINKS['swim']}' target='_blank' rel='noopener'>Swim Center</a> info.",
            f"Drop by the Student Rec Center—gym, courts, even climbing: <a href='{VANDAL_LINKS['rec']}' target='_blank' rel='noopener'>Rec Center</a>."
        ]
        campus.append(_pick(campus_pools, f"{date.today()}-campus"))

    # Food security mention
    food_lines = []
    if signals["food_low"]:
        food_lines.append("If meals are tight, you’re not alone—campus and local options can help with groceries.")

    # Assemble final 2–4 sentences (priority → one combo → one single → maybe journal → maybe campus → maybe food)
    seed_key = f"{date.today()}-{mood}{stress}{focus}{sleep}{motivation}{anxiety}{appetite}{food_security}-{journal[:40]}"
    lines = []
    if priority:
        lines.append(priority[0])
    if combos:
        lines.append(combos[0])
    if singles:
        lines.append(_pick(singles, seed_key))
    if journal_lines:
        lines.append(_pick(journal_lines, seed_key))
    if campus:
        lines.append(campus[0])
    if food_lines:
        lines.append(food_lines[0])

    # Farmers Market add-on if appetite low
    farmers_market_message = None
    if appetite <= 2:
        farmers_market_message = (
            "🍎 To gently spark appetite, try the "
            "<a href='https://www.ci.moscow.id.us/197/Community-Events-Moscow-Farmers-Market' "
            "target='_blank' rel='noopener'>Moscow Farmers Market</a> on Saturdays (May–Oct, 8am–1pm)."
        )

    # De-dupe, trim
    seen = set(); final = []
    for s in lines:
        if s and s not in seen:
            final.append(s); seen.add(s)
    final = final[:4]
    if not final:
        final = ["Your responses look balanced today. Keep prioritizing your well-being!"]
    if farmers_market_message:
        final.append(farmers_market_message)

    return " ".join(final)

# ---------- Optional journal emotion
def analyze_journal_emotion(journal_text):
    """Emotion analysis with simple negation overrides; lazily load transformer."""
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

# ---------- Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit_checkin():
    """Process wellness check-in submission."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['mood', 'stress', 'focus', 'sleep', 'motivation', 'anxiety', 'appetite', 'food_security']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Reject all-default (3) submissions
        if all(data[field] == 3 for field in required_fields):
            return jsonify({
                'error': "It looks like you haven't updated any inputs. Please adjust them to reflect your current state.",
                'type': 'validation'
            }), 400

        # Calculate core metrics
        wellness_score = calculate_wellness_score(data)
        burnout_level = get_burnout_level(wellness_score)

        # Emotion (if any) BEFORE feedback so we can use it
        emotion_analysis = None
        if 'journal' in data and (data['journal'] or '').strip():
            emotion_analysis = analyze_journal_emotion(data['journal'])

        # Personalized feedback + resources
        feedback = generate_advanced_feedback(data, emotion=emotion_analysis)
        resources = get_resources(burnout_level, data)

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
    return jsonify(EMOJIS)

@app.route('/health')
def health():
    return jsonify({"ok": True}), 200

if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port)
