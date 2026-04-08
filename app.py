from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from googletrans import Translator   # ✅ Added for translation

# Configure the Generative AI with your API key
genai.configure(api_key="AIzaSyALv0mhxyGjhq_zaJlOHo4vakyYIV1AF_o")

app = Flask(__name__)
translator = Translator()  # ✅ Initialize translator

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    generation_config=generation_config,
)

# Dictionary to store chat sessions
chat_sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json.get("message")
    session_id = request.json.get("session_id")
    lang = request.json.get("lang", "en")  # ✅ Get selected language

    # Translate user message → English (if not already)
    if lang != "en":
        try:
            user_message_en = translator.translate(user_message, src=lang, dest="en").text
        except Exception:
            user_message_en = user_message  # fallback
    else:
        user_message_en = user_message

    # Initialize chat session if not already created
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "You are a helpful assistant for parents of autistic children. "
                        "Respond only to queries related to autism. For unrelated topics, reply: "
                        "'Please ask queries related to Autism only. I am not aware of any other information.' "
                        "Keep responses under 50 words."
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Okay. Ask me your questions about autism in children."
                    ],
                },
            ]
        )

    chat_session = chat_sessions[session_id]

    try:
        # Send translated message to chatbot
        response = chat_session.send_message(user_message_en)

        # Ensure proper text response
        reply = response.text if hasattr(response, "text") else str(response)

        # Translate reply → back to user’s language
        if lang != "en":
            try:
                reply = translator.translate(reply, src="en", dest=lang).text
            except Exception:
                pass  # fallback: keep English reply

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
