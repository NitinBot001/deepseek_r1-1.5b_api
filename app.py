from flask import Flask, request, jsonify
from llama_cpp import Llama
import os
import threading
import requests

# 🔹 Flask App
app = Flask(__name__)

# 🔹 Model Path (GitHub Secrets से लिया गया)
MODEL_PATH = "model/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
# 🔹 Context File URL
CONTEXT_URL = "https://raw.githubusercontent.com/NitinBot001/Unlimitedrdp/refs/heads/main/context.txt"
CONTEXT_FILE = "context.txt"

# 🔹 Load Context File from GitHub
def download_context():
    try:
        response = requests.get(CONTEXT_URL)
        if response.status_code == 200:
            with open(CONTEXT_FILE, "w", encoding="utf-8") as file:
                file.write(response.text)
            print("✅ Context file downloaded successfully!")
        else:
            print(f"⚠️ Failed to download context file! Status Code: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error downloading context file: {str(e)}")

# 🔹 Load Context from File
def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    return ""

# 🔹 Load Llama Model
print(f"🔄 Loading model from: {MODEL_PATH} ...")
llm = Llama(model_path=MODEL_PATH, n_ctx=8192)  # 🔥 ज्यादा कॉन्टेक्स्ट लेंथ
print("✅ Model Loaded Successfully!")

# 🔹 Download Context on Startup
download_context()
CONTEXT_DATA = load_context()

# 🔹 AI मॉडल से जवाब पाने का फंक्शन
def get_ai_response(prompt):
    full_prompt = f"{CONTEXT_DATA}\n\nUser: {prompt}\nAI:"
    response = llm(
        full_prompt, 
        max_tokens=256, 
        stop=["\n", "User:"],  
        echo=False
    )
    return response["choices"][0]["text"].strip()

# 🔹 API Route - सवाल पूछो, जवाब पाओ
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "Question is required!"}), 400

        print(f"🤖 AI Processing: {question}")
        response = get_ai_response(question)

        return jsonify({"question": question, "answer": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Root Route - हेल्थ चेक
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ AI Model is Running with Context!"})

# 🔹 Flask Server को बैकग्राउंड में चलाने के लिए
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
