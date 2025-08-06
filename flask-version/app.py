from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Emoji mappings for different wellness metrics
EMOJIS = {
    "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
    "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
    "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
    "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
    "energy": {1: "🥱", 2: "😪", 3: "😐", 4: "😊", 5: "🤩"},
    "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
    "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
    "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"}
}

def calculate_wellness_score(data):
    """Calculate overall wellness score from user inputs"""
    mood = data['mood']
    stress = data['stress']
    focus = data['focus']
    sleep = data['sleep']
    energy = data['energy']
    motivation = data['motivation']
    anxiety = data['anxiety']
    appetite = data['appetite']
    
    # Reverse scoring for negative metrics
    stress_score = 6 - stress
    anxiety_score = 6 - anxiety
    appetite_score = 3 - abs(appetite - 3)
    
    # Calculate average wellness score
    wellness_score = (
        mood + stress_score + focus + sleep + 
        energy + motivation + anxiety_score + appetite_score
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

def get_resources(burnout_level):
    """Get University of Idaho specific resources based on burnout level"""
    resources = {
        "High": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {
                    "name": "🧠 Counseling Services",
                    "url": "https://www.uidaho.edu/current-students/cmhc",
                    "description": "Free short-term counseling, mental health support."
                },
                {
                    "name": "📘 TRIO Student Support Services",
                    "url": "https://www.uidaho.edu/current-students/academic-support/asp/sss",
                    "description": "Academic advising, tutoring, and life coaching for eligible students."
                },
                {
                    "name": "🏛️ Vandal Success Center",
                    "url": "https://www.uidaho.edu/current-students/academic-support/asp",
                    "description": "Help with tutoring, time management, and academic skills."
                }
            ]
        },
        "Moderate": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {
                    "name": "📚 Academic Coaching",
                    "description": ""
                },
                {
                    "name": "🧘 Mindfulness Workshops", 
                    "description": ""
                },
                {
                    "name": "📎 Tutoring Services",
                    "description": ""
                }
            ]
        },
        "Low": {
            "title": "🎯 Suggested Campus Resources",
            "items": [
                {
                    "name": "🎉 Keep up the great work!",
                    "description": ""
                },
                {
                    "name": "🤝 Peer Mentoring",
                    "description": ""
                },
                {
                    "name": "🗣️ Join a wellness event",
                    "description": ""
                }
            ]
        }
    }
    return resources.get(burnout_level, resources["Moderate"])

def generate_advanced_feedback(data):
    """Generate personalized feedback based on user inputs - Exact Streamlit logic"""
    feedback = []
    
    mood = data['mood']
    stress = data['stress']
    focus = data['focus']
    sleep = data['sleep']
    energy = data['energy']
    motivation = data['motivation']
    anxiety = data['anxiety']
    appetite = data['appetite']
    
    # 1. Red Flag: Multiple lows
    criticals = [mood, focus, sleep, energy, motivation]
    n_crit_low = sum(1 for v in criticals if v <= 2)
    
    if n_crit_low >= 3:
        feedback.append("🚩 Multiple areas are low. Please consider talking to a counselor or trusted person—you're not alone.")
    
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
        feedback.append("Very low sleep and energy: try to rest, even if it's a short nap.")
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
        feedback.append("Low appetite—don't skip meals; small snacks can help.")
    elif appetite >= 4:
        feedback.append("Strong appetite—opt for nourishing, balanced meals.")
    elif appetite == 3:
        feedback.append("Balanced appetite—this is a good wellness sign.")
    
    # 4. All thriving
    if (all(v >= 4 for v in [mood, sleep, energy, motivation]) and 
        stress <= 2 and anxiety <= 2 and focus >= 4 and appetite == 3):
        feedback.append("🌱 You're thriving across all areas! Keep up your healthy habits.")
    
    # 5. Catch-all
    if not feedback:
        feedback.append("Your responses look balanced today. Keep prioritizing your well-being!")
    
    # Return top 2 unique feedback items
    unique_feedback = []
    for tip in feedback:
        if tip not in unique_feedback:
            unique_feedback.append(tip)
        if len(unique_feedback) == 2:
            break
    
    return " ".join(unique_feedback)

def analyze_journal_emotion(journal_text):
    """Advanced emotion analysis using transformers - exact Streamlit logic"""
    if not journal_text.strip():
        return None
    
    try:
        # Check for negation patterns first (exact Streamlit logic)
        def override_emotion_with_negation(text):
            text = text.lower()
            if re.search(r"not[\s\w]*sad", text):
                return {"label": "neutral", "score": 1.0}
            elif re.search(r"not[\s\w]*happy", text) or re.search(r"not[\s\w]*good", text):
                return {"label": "sadness", "score": 0.9}
            elif re.search(r"not[\s\w]*stressed", text):
                return {"label": "calm", "score": 0.95}
            return None
        
        override = override_emotion_with_negation(journal_text)
        if override:
            return {"emotion": override["label"], "confidence": override["score"]}
        
        # Use the exact same model as Streamlit
        from transformers import pipeline
        emotion_pipeline = pipeline(
            "text-classification", 
            model="bhadresh-savani/distilbert-base-uncased-emotion", 
            return_all_scores=True
        )
        
        result = emotion_pipeline(journal_text)[0]
        sorted_result = sorted(result, key=lambda x: x['score'], reverse=True)
        top_emotion = sorted_result[0]
        
        return {"emotion": top_emotion['label'], "confidence": top_emotion['score']}
        
    except Exception as e:
        print(f"Error in emotion analysis: {e}")
        # Fallback to simple analysis if transformers fails
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
        
        # Validate that all required fields are present
        required_fields = ['mood', 'stress', 'focus', 'sleep', 'energy', 'motivation', 'anxiety', 'appetite']
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
        resources = get_resources(burnout_level)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)