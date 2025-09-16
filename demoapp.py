from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)

# Configuration
EXTERNAL_AI_API = "https://website-1-f6l8.onrender.com/api/generate-reply-prompt"

@app.route('/api/generate-reply-prompt', methods=['POST', 'OPTIONS'])
def generate_reply_prompt():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        # Call the external AI API
        response = requests.post(
            EXTERNAL_AI_API,
            json={"prompt": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "AI service unavailable",
                "fallback_response": generate_fallback_response(prompt)
            }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "AI service timeout",
            "fallback_response": generate_fallback_response(prompt)
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"AI service error: {str(e)}",
            "fallback_response": generate_fallback_response(prompt)
        }), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def generate_fallback_response(prompt):
    """Generate a simple fallback response when the AI service is unavailable"""
    return {
        "reply": f"Hi there! Thanks for your message about the open house. I'd be happy to help you with your real estate needs. When were you thinking of coming by for a viewing?",
        "follow_ups": [
            "Just following up on your interest in our open house. Did you have a chance to think about scheduling a viewing?",
            "I wanted to check in again about the property. We've had quite a bit of interest, so let me know if you'd like me to hold a specific time for you!",
            "Final follow-up about the property. We're finalizing viewings this week, so please let me know if you're still interested."
        ]
    }

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "replyzeai-demo"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', False))
