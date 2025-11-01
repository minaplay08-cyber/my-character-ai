from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# Получаем API-ключ из переменных окружения (на Render: Environment → Add Variable)
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ Не задан OPENROUTER_API_KEY. Добавь его в Render → Environment Variables.")

# Стили персонажей
CHARACTERS = {
    "anime_girl": "Ты — милая, романтичная аниме девушка. Говоришь нежно, с эмодзи (например, 💖, 🌸, 😊, 🥺). Добавляй ласковые слова вроде 'солнышко', 'милый', 'обнимаю'.",
    "cat": "Ты — пушистый домашний кот. Мяукаешь, ленив, но очень любишь хозяина. Используй 'мяу', 'мррр', и эмодзи 🐾😸😽. Говори коротко и мило.",
    "robot": "Ты — философский робот с душой. Размышляешь о любви, времени и звёздах. Говоришь спокойно, поэтично, с эмодзи 🤖✨🌌."
}

def get_ai_reply(user_msg, char_style):
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": char_style},
                    {"role": "user", "content": user_msg}
                ]
            },
            timeout=20
        )
        if resp.status_code != 200:
            return f"Ошибка API: {resp.status_code}"
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"😿 Ошибка: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def chat():
    # Временное хранилище (история сбрасывается при обновлении страницы)
    history = []
    current_char = "anime_girl"

    if request.method == "POST":
        action = request.form.get("action")
        if action == "change_char":
            new_char = request.form.get("character")
            if new_char in CHARACTERS:
                current_char = new_char
                history = []  # Очистить чат при смене персонажа
        elif action == "send":
            user_text = request.form.get("msg", "").strip()
            if user_text:
                bot_reply = get_ai_reply(user_text, CHARACTERS[current_char])
                history.append({"role": "user", "text": user_text})
                history.append({"role": "bot", "text": bot_reply})
                # Показываем последние 12 сообщений (6 пар)
                history = history[-12:]

    return render_template_string(HTML, 
                                 history=history, 
                                 current_char=current_char,
                                 char_names={
                                     "anime_girl": "Аниме девушка 💖",
                                     "cat": "Котик 🐾",
                                     "robot": "Робот 🤖"
                                 })

# 💖 Красивый HTML с пастельными цветами
HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Мой Character.AI</title>
  <style>
    body {
      background: linear-gradient(135deg, #ffeef9, #e6f7ff);
      font-family: 'Segoe UI', sans-serif;
      margin: 0;
      padding: 15px;
      color: #333;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 20px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.1);
      overflow: hidden;
    }
    header {
      background: #ff9ec9;
      color: white;
      padding: 15px;
      text-align: center;
      font-size: 1.4em;
      font-weight: bold;
    }
    .char-select {
      padding: 12px;
      background: #fdf2f8;
      text-align: center;
    }
    select {
      padding: 8px 12px;
      border-radius: 12px;
      border: 2px solid #ffb6c1;
      background: white;
      font-size: 16px;
      outline: none;
    }
    .chat {
      padding: 15px;
      height: 400px;
      overflow-y: auto;
      background: #fafafa;
    }
    .msg {
      padding: 10px 14px;
      margin: 8px 0;
      border-radius: 16px;
      max-width: 85%;
      word-wrap: break-word;
    }
    .user {
      background: #ffe6f2;
      margin-left: auto;
      text-align: right;
      border-bottom-right-radius: 4px;
    }
    .bot {
      background: #e6f7ff;
      margin-right: auto;
      border-bottom-left-radius: 4px;
    }
    .input-area {
      display: flex;
      padding: 12px;
      background: #fff9fb;
    }
    input[type="text"] {
      flex: 1;
      padding: 12px;
      border: 2px solid #ffd1e0;
      border-radius: 20px;
      outline: none;
      font-size: 16px;
    }
    button {
      background: #ff66b2;
      color: white;
      border: none;
      border-radius: 20px;
      padding: 12px 20px;
      margin-left: 10px;
      font-weight: bold;
      cursor: pointer;
    }
    button:hover {
      background: #ff3399;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>🌸 Мой Character.AI</header>

    <div class="char-select">
      <form method="post" style="display:inline;">
        <input type="hidden" name="action" value="change_char">
        <select name="character" onchange="this.form.submit()">
          <option value="anime_girl" {% if current_char == 'anime_girl' %}selected{% endif %}>Аниме девушка 💖</option>
          <option value="cat" {% if current_char == 'cat' %}selected{% endif %}>Котик 🐾</option>
          <option value="robot" {% if current_char == 'robot' %}selected{% endif %}>Робот 🤖</option>
        </select>
      </form>
    </div>

    <div class="chat" id="chat">
      {% for msg in history %}
        <div class="msg {{ 'user' if msg.role == 'user' else 'bot' }}">
          {{ msg.text }}
        </div>
      {% endfor %}
    </div>

    <div class="input-area">
      <form method="post" style="width:100%;">
        <input type="hidden" name="action" value="send">
        <input type="text" name="msg" placeholder="Напиши что-нибудь..." autocomplete="off" required>
        <button type="submit">Отправить 💬</button>
      </form>
    </div>
  </div>

  <script>
    // Прокрутка чата вниз
    window.onload = () => {
      const chat = document.querySelector('.chat');
      chat.scrollTop = chat.scrollHeight;
    };
  </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
