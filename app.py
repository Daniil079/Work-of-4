import json
import random
import string
from datetime import datetime
import os

class URLShortener:
    def __init__(self, storage_file='urls.json'):
        self.storage_file = storage_file
        self.urls = self.load_urls()
    
    def load_urls(self):
        """Загружает URL из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_urls(self):
        """Сохраняет URL в файл"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.urls, f, indent=2)
    
    def generate_short_code(self, length=6):
        """Генерирует случайный короткий код"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def shorten_url(self, long_url, custom_code=None):
        """Создает короткую ссылку для длинного URL"""
        # Проверяем, существует ли уже такой URL
        for code, data in self.urls.items():
            if data['long_url'] == long_url:
                return code
        
        # Генерируем или используем пользовательский код
        if custom_code:
            if custom_code in self.urls:
                raise ValueError(f"Код '{custom_code}' уже используется")
            short_code = custom_code
        else:
            short_code = self.generate_short_code()
            # Убеждаемся, что код уникален
            while short_code in self.urls:
                short_code = self.generate_short_code()
        
        # Сохраняем URL
        self.urls[short_code] = {
            'long_url': long_url,
            'created_at': datetime.now().isoformat(),
            'clicks': 0
        }
        
        self.save_urls()
        return short_code
    
    def get_long_url(self, short_code):
        """Получает оригинальный URL по короткому коду"""
        if short_code in self.urls:
            self.urls[short_code]['clicks'] += 1
            self.save_urls()
            return self.urls[short_code]['long_url']
        return None
    
    def get_url_info(self, short_code):
        """Получает информацию о короткой ссылке"""
        return self.urls.get(short_code)
    
    def get_all_urls(self):
        """Возвращает все сохраненные URL"""
        return self.urls
    
    def delete_url(self, short_code):
        """Удаляет короткую ссылку"""
        if short_code in self.urls:
            del self.urls[short_code]
            self.save_urls()
            return True
        return False

def main():
    shortener = URLShortener()
    
    while True:
        print("\n=== URL Shortener ===")
        print("1. Создать короткую ссылку")
        print("2. Перейти по короткой ссылке")
        print("3. Показать все ссылки")
        print("4. Получить информацию о ссылке")
        print("5. Удалить ссылку")
        print("6. Выйти")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            long_url = input("Введите длинный URL: ").strip()
            if not long_url.startswith(('http://', 'https://')):
                long_url = 'https://' + long_url
            
            custom_code = input("Введите свой код (или оставьте пустым для автогенерации): ").strip()
            custom_code = custom_code if custom_code else None
            
            try:
                short_code = shortener.shorten_url(long_url, custom_code)
                print(f"Короткая ссылка создана: http://short.url/{short_code}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        
        elif choice == '2':
            short_code = input("Введите короткий код: ").strip()
            long_url = shortener.get_long_url(short_code)
            if long_url:
                print(f"Перенаправление на: {long_url}")
            else:
                print("Ссылка не найдена")
        
        elif choice == '3':
            urls = shortener.get_all_urls()
            if not urls:
                print("Нет сохраненных ссылок")
            else:
                print("\nВсе сохраненные ссылки:")
                for code, data in urls.items():
                    print(f"{code} -> {data['long_url']} (кликов: {data['clicks']})")
        
        elif choice == '4':
            short_code = input("Введите короткий код: ").strip()
            info = shortener.get_url_info(short_code)
            if info:
                print(f"Оригинальный URL: {info['long_url']}")
                print(f"Создана: {info['created_at']}")
                print(f"Кликов: {info['clicks']}")
            else:
                print("Ссылка не найдена")
        
        elif choice == '5':
            short_code = input("Введите короткий код для удаления: ").strip()
            if shortener.delete_url(short_code):
                print("Ссылка удалена")
            else:
                print("Ссылка не найдена")
        
        elif choice == '6':
            print("До свидания!")
            break
        
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()

