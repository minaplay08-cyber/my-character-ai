from flask import Flask, request, render_template_string
from replit import db
import requests
import os

app = Flask(__name__)

# Получаем API-ключ из Secrets (Replit → 🔒 Secrets)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Добавь OPENROUTER_API_KEY в Secrets!")

# Стили персонажей
CHARACTERS = {
    "anime_girl": "Ты — милая аниме девушка. Говоришь романтично, игриво, с эмодзи (например, 💖, 🌸, 😊).",
    "cat": "Ты — ласковый домашний кот. Мяукаешь, любишь ласку, немного ленив, но очень заботливый. Используй 'мяу' и эмодзи 🐾😸.",
    "robot": "Ты — философский робот. Размышляешь о жизни, любви и смысле бытия. Говоришь спокойно, с глубиной и немного поэтично. 🤖✨"
}

def get_ai_response(prompt, char_key):
    system_prompt = CHARACTERS.get(char_key, CHARACTERS["anime_girl"])
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    chat_history = db.get("history", [])
    selected_char = db.get("character", "anime_girl")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "set_char":
            selected_char = request.form.get("character")
            db["character"] = selected_char
            chat_history = []  # Очистить историю при смене персонажа
            db["history"] = chat_history
        elif action == "send_msg":
            user_msg = request.form.get("message", "").strip()
            if user_msg:
                bot_reply = get_ai_response(user_msg, selected_char)
                chat_history.append({"role": "user", "text": user_msg})
                chat_history.append({"role": "bot", "text": bot_reply})
                db["history"] = chat_history[-10:]  # Храним последние 10 сообщений

    return render_template_string(HTML_TEMPLATE, 
                                 history=chat_history, 
                                 char=selected_char,
                                 chars=CHARACTERS)

# Простой HTML-шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
  <title>Мой Character.AI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 20px auto; padding: 10px; }
    .msg { padding: 8px; margin: 6px 0; border-radius: 10px; }
    .user { background: #d1e7ff; text-align: right; }
    .bot { background: #f0f0f0; }
    select, button, input { padding: 8px; margin: 5px 0; font-size: 16px; }
    input[type="text"] { width: 70%; }
    button[type="submit"] { width: 28%; }
  </style>
</head>
<body>
  <h2>💬 Мой Character.AI</h2>

  <form method="post">
    <input type="hidden" name="action" value="set_char">
    <select name="character" onchange="this.form.submit()">
      <option value="anime_girl" {% if char == 'anime_girl' %}selected{% endif %}>Аниме девушка 💖</option>
      <option value="cat" {% if char == 'cat' %}selected{% endif %}>Кот 🐾</option>
      <option value="robot" {% if char == 'robot' %}selected{% endif %}>Робот 🤖</option>
    </select>
  </form>

  <div id="chat">
    {% for msg in history %}
      <div class="msg {{ msg.role }}">{{ msg.text }}</div>
    {% endfor %}
  </div>

  <form method="post">
    <input type="hidden" name="action" value="send_msg">
    <input type="text" name="message" placeholder="Напиши что-нибудь..." autocomplete="off" required>
    <button type="submit">Отправить</button>
  </form>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
