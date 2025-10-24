import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def get_scraperapi_url(site_config):
    """
    Преобразует целевой URL в URL для запроса к ScraperAPI,
    добавляя рендеринг JS при необходимости.
    """
    load_dotenv()
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key or "ВАШ_API_КЛЮЧ" in api_key:
        print("Ошибка: API-ключ ScraperAPI не найден или не изменен в .env файле.")
        return None
    
    target_url = site_config['url']
    base_url = f'http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ua'
    
    # Проверяем, нужно ли включать JS Rendering для этого сайта
    if site_config.get('js_rendering', False ):
        print(f"[{site_config['site_name']}] Включаю JS Rendering.")
        return f'{base_url}&render=true'
    
    return base_url

def parse_site_with_api(site_config ):
    """
    Универсальная функция для парсинга одного сайта через ScraperAPI.
    """
    site_name = site_config['site_name']
    target_url = site_config['url']
    selector = site_config['product_name_selector']
    
    print(f"--- [ScraperAPI] Начинаю парсинг сайта: {site_name} ---")
    
    api_url = get_scraperapi_url(site_config)
    if not api_url:
        return []

    product_names = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"[{site_name}] Отправляю запрос для {target_url}...")
        response = requests.get(api_url, headers=headers, timeout=120)
        response.raise_for_status()
        
        print(f"[{site_name}] Ответ получен. Начинаю парсинг HTML...")
        html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        product_elements = soup.select(selector)
        
        product_names = [elem.get_text(strip=True) for elem in product_elements if elem.get_text(strip=True)]
        
    except requests.exceptions.RequestException as e:
        print(f"[{site_name}] Ошибка сетевого запроса: {e}")
    except Exception as e:
        print(f"[{site_name}] Произошла непредвиденная ошибка: {e}")
    finally:
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_filename = os.path.join(output_dir, f"output_{site_name}.txt")
        with open(output_filename, 'w', encoding='utf-8') as f:
            for name in product_names:
                f.write(name + '\n')

        print(f"--- Парсинг сайта {site_name} завершен. Найдено: {len(product_names)} товаров. ---")
        print(f"Результаты сохранены в файл: {output_filename}")
        return product_names

def main():
    """
    Основная функция для запуска парсеров для всех сайтов в конфиге.
    """
    with open('config.json', 'r', encoding='utf-8') as f:
        configs = json.load(f)
    
    all_results = {}
    
    for site_config in configs:
        names = parse_site_with_api(site_config)
        all_results[site_config['site_name']] = names
        
    print("\n\n--- ИТОГОВЫЙ РЕЗУЛЬТАТ ---")
    for site, names in all_results.items():
        print(f"Сайт: {site}, Найдено товаров: {len(names)}")

if __name__ == "__main__":
    main()
