from flask import Flask, request, jsonify, redirect, render_template_string
import json
import random
import string
from datetime import datetime
import os

app = Flask(__name__)

class URLShortener:
    def __init__(self, storage_file='urls.json'):
        self.storage_file = storage_file
        self.urls = self.load_urls()
    
    def load_urls(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_urls(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.urls, f, indent=2)
    
    def generate_short_code(self, length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def shorten_url(self, long_url, custom_code=None):
        for code, data in self.urls.items():
            if data['long_url'] == long_url:
                return code
        
        if custom_code:
            if custom_code in self.urls:
                raise ValueError(f"Код '{custom_code}' уже используется")
            short_code = custom_code
        else:
            short_code = self.generate_short_code()
            while short_code in self.urls:
                short_code = self.generate_short_code()
        
        self.urls[short_code] = {
            'long_url': long_url,
            'created_at': datetime.now().isoformat(),
            'clicks': 0
        }
        
        self.save_urls()
        return short_code
    
    def get_long_url(self, short_code):
        if short_code in self.urls:
            self.urls[short_code]['clicks'] += 1
            self.save_urls()
            return self.urls[short_code]['long_url']
        return None
    
    def get_url_info(self, short_code):
        return self.urls.get(short_code)
    
    def get_all_urls(self):
        return self.urls
    
    def delete_url(self, short_code):
        if short_code in self.urls:
            del self.urls[short_code]
            self.save_urls()
            return True
        return False

# Создаем экземпляр коротера
shortener = URLShortener()

# HTML шаблон для веб-интерфейса
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #333; 
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"] { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            border-color: #667eea;
            outline: none;
        }
        button { 
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #764ba2;
        }
        .result {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }
        .url-list {
            margin-top: 30px;
        }
        .url-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 URL Shortener</h1>
        
        <form action="/shorten" method="post">
            <div class="form-group">
                <label for="long_url">Длинный URL:</label>
                <input type="text" id="long_url" name="long_url" 
                       placeholder="https://example.com/very-long-url" required>
            </div>
            
            <div class="form-group">
                <label for="custom_code">Свой код (необязательно):</label>
                <input type="text" id="custom_code" name="custom_code" 
                       placeholder="my-link">
            </div>
            
            <button type="submit">Сократить URL</button>
        </form>
        
        {% if short_url %}
        <div class="result">
            <strong>✅ Короткая ссылка создана!</strong><br>
            <a href="{{ short_url }}" target="_blank" style="font-size: 18px;">
                {{ short_url }}
            </a>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="error">
            <strong>❌ Ошибка:</strong> {{ error }}
        </div>
        {% endif %}
        
        <div class="url-list">
            <h3>📊 Все сокращенные ссылки:</h3>
            {% if urls %}
                {% for code, data in urls.items() %}
                <div class="url-item">
                    <strong>{{ code }}</strong> → 
                    <a href="{{ data.long_url }}" target="_blank">{{ data.long_url[:50] }}...</a><br>
                    <small>👆 Кликов: {{ data.clicks }} | 📅 Создана: {{ data.created_at[:16] }}</small>
                </div>
                {% endfor %}
            {% else %}
                <p>Пока нет сокращенных ссылок</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Главная страница с формой"""
    urls = shortener.get_all_urls()
    return render_template_string(HTML_TEMPLATE, urls=urls, short_url=None, error=None)

@app.route('/shorten', methods=['POST'])
def shorten():
    """Обработка создания короткой ссылки"""
    long_url = request.form['long_url']
    custom_code = request.form['custom_code'] or None
    
    # Добавляем http:// если отсутствует
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url
    
    try:
        short_code = shortener.shorten_url(long_url, custom_code)
        short_url = f"http://localhost:5000/{short_code}"
        urls = shortener.get_all_urls()
        return render_template_string(HTML_TEMPLATE, urls=urls, short_url=short_url, error=None)
    except ValueError as e:
        urls = shortener.get_all_urls()
        return render_template_string(HTML_TEMPLATE, urls=urls, short_url=None, error=str(e))

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    """Перенаправление по короткой ссылке"""
    long_url = shortener.get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    return "Ссылка не найдена", 404

@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    """API для создания коротких ссылок"""
    data = request.get_json()
    long_url = data.get('long_url')
    custom_code = data.get('custom_code')
    
    if not long_url:
        return jsonify({'error': 'long_url обязателен'}), 400
    
    try:
        short_code = shortener.shorten_url(long_url, custom_code)
        return jsonify({
            'short_code': short_code,
            'short_url': f"http://localhost:5000/{short_code}",
            'long_url': long_url
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)