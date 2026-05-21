from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Yandex Cloud настройки (используем переменные окружения для безопасности)
FOLDER_ID = os.environ.get('FOLDER_ID', 'b1go78v36a0sl6cqlcqu')
API_KEY = os.environ.get('API_KEY', 'AQVN0ZUJcws7xQCMCyZj8ake1p-9v5PtqvsNIHPz')
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def query_yandex_gpt(prompt, temperature=0.1):
    """Запрос к Yandex GPT"""
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": 300
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты - лингвистический эксперт. Отвечай ТОЛЬКО списком слов через запятую. Никаких пояснений, номеров, точек в конце. Если ничего нет, напиши 'нет'."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }
    
    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=body, timeout=15)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            answer = answer.strip().lower()
            answer = re.sub(r'^\d+[\.\)]\s*', '', answer)
            answer = re.sub(r'\n\d+[\.\)]\s*', ', ', answer)
            answer = re.sub(r'[\.!?;:]$', '', answer)
            return answer
        else:
            print(f"API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def clean_response(response_text):
    """Очистка ответа от лишних символов"""
    if not response_text or response_text == 'нет':
        return []
    
    items = [item.strip() for item in response_text.split(',')]
    
    cleaned = []
    for item in items:
        if item and len(item) < 30 and not item.startswith('корень') and not item.startswith('окончание'):
            item = re.sub(r'^[«"\'\(\)\s]+|[»"\'\(\)\s]+$', '', item)
            if item and len(item) < 20:
                cleaned.append(item)
    
    return list(set(cleaned))[:7]

def analyze_word_linguistically(word):
    """Лингвистический анализ слова через Yandex GPT"""
    
    synonyms_str = query_yandex_gpt(f"Найди 5 синонимов к слову '{word}'. Только список через запятую.")
    synonyms = clean_response(synonyms_str)
    
    antonyms_str = query_yandex_gpt(f"Найди 3 антонима к слову '{word}'. Только список через запятую.")
    antonyms = clean_response(antonyms_str)
    
    homonyms_str = query_yandex_gpt(f"Есть ли у слова '{word}' омонимы? Если да, перечисли через запятую. Если нет, ответь 'нет'.")
    homonyms = clean_response(homonyms_str)
    
    paronyms_str = query_yandex_gpt(f"Найди 3 паронима к слову '{word}'. Только список через запятую.")
    paronyms = clean_response(paronyms_str)
    
    hyperonyms_str = query_yandex_gpt(f"Какой гипероним (общее понятие) у слова '{word}'? Только 1 слово.")
    hyperonyms = clean_response(hyperonyms_str)
    
    hyponyms_str = query_yandex_gpt(f"Найди 3 гипонима (конкретных понятия) для слова '{word}'. Только список через запятую.")
    hyponyms = clean_response(hyponyms_str)
    
    meronyms_str = query_yandex_gpt(f"Найди 3 части (меронима) для слова '{word}'. Только список слов через запятую. Без пояснений.")
    meronyms = clean_response(meronyms_str)
    if meronyms:
        meronyms = [m for m in meronyms if len(m) < 15 and m not in ['корень', 'основа', 'окончание', 'приставка', 'суффикс']]
    
    homographs_str = query_yandex_gpt(f"Есть ли у слова '{word}' омографы? Если да, напиши пары через запятую. Если нет, ответь 'нет'.")
    homographs = clean_response(homographs_str)
    
    enantiosemy_str = query_yandex_gpt(f"Есть ли у слова '{word}' энантиосемия? Если да, напиши примеры. Если нет, ответь 'нет'.")
    enantiosemy = clean_response(enantiosemy_str)
    
    quasisynonyms_str = query_yandex_gpt(f"Найди 3 квазисинонима к слову '{word}'. Только список через запятую.")
    quasisynonyms = clean_response(quasisynonyms_str)
    
    stylistics_str = query_yandex_gpt(f"Найди стилистические синонимы для слова '{word}'. Только список через запятую.")
    stylistics = clean_response(stylistics_str)
    
    absolute_str = query_yandex_gpt(f"Есть ли у слова '{word}' абсолютные синонимы? Если да, перечисли через запятую. Если нет, ответь 'нет'.")
    absolute = clean_response(absolute_str)
    
    variants_str = query_yandex_gpt(f"Есть ли у слова '{word}' лексические варианты? Если да, перечисли через запятую. Если нет, ответь 'нет'.")
    variants = clean_response(variants_str)
    
    conversives_str = query_yandex_gpt(f"Есть ли у слова '{word}' конверсивы? Если да, перечисли через запятую. Если нет, ответь 'нет'.")
    conversives = clean_response(conversives_str)
    
    functional_str = query_yandex_gpt(f"Может ли слово '{word}' быть функциональным омонимом? Если да, напиши примеры. Если нет, ответь 'нет'.")
    functional = clean_response(functional_str)
    
    return {
        "статус": "успех",
        "слово": word,
        "результаты": {
            "синонимы": synonyms if synonyms else ["не найдены"],
            "антонимы": antonyms if antonyms else ["не найдены"],
            "омонимы": homonyms if homonyms else ["не найдены"],
            "паронимы": paronyms if paronyms else ["не найдены"],
            "гиперонимы": hyperonyms if hyperonyms else ["не найдены"],
            "гипонимы": hyponyms if hyponyms else ["не найдены"],
            "меронимы": meronyms if meronyms else ["не найдены"],
            "омографы": homographs if homographs else ["не найдены"],
            "энантиосемия": enantiosemy if enantiosemy else ["не найдены"],
            "квазисинонимы": quasisynonyms if quasisynonyms else ["не найдены"],
            "стилистические_синонимы": stylistics if stylistics else ["не найдены"],
            "абсолютные_синонимы": absolute if absolute else ["не найдены"],
            "лексические_варианты": variants if variants else ["не найдены"],
            "конверсивы": conversives if conversives else ["не найдены"],
            "функциональные_омонимы": functional if functional else ["не найдены"]
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        word = data.get('word', '').strip().lower()
        
        if not word:
            return jsonify({"статус": "ошибка", "сообщение": "Введите слово"}), 400
        
        print(f"🔍 Анализируем слово: {word}")
        result = analyze_word_linguistically(word)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return jsonify({"статус": "ошибка", "сообщение": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"статус": "ok", "сервис": "Yandex GPT"})

@app.route('/test_all', methods=['GET'])
def test_all():
    """Тестирование всех типов отношений"""
    test_cases = [
        {"word": "замок", "check": ["омографы"]},
        {"word": "прослушать", "check": ["энантиосемия"]},
        {"word": "продать", "check": ["конверсивы"]},
        {"word": "столовая", "check": ["функциональные_омонимы"]},
        {"word": "дерево", "check": ["меронимы"]},
        {"word": "собака", "check": ["гиперонимы", "гипонимы"]},
        {"word": "красный", "check": ["квазисинонимы"]},
        {"word": "лицо", "check": ["стилистические_синонимы"]},
        {"word": "бегемот", "check": ["абсолютные_синонимы"]},
        {"word": "галоша", "check": ["лексические_варианты"]}
    ]
    
    results = {}
    for test in test_cases:
        word = test["word"]
        result = analyze_word_linguistically(word)
        checked_fields = {}
        for field in test["check"]:
            checked_fields[field] = result["результаты"].get(field, [])
        results[word] = checked_fields
    
    return jsonify({"статус": "тест завершен", "результаты": results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Запуск лингвистического сервиса на порту {port}")
    app.run(debug=False, host='0.0.0.0', port=port)