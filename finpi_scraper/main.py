import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

def get_scraperapi_url(site_config, page_url=None):
    """
    Преобразует целевой URL в URL для запроса к ScraperAPI,
    добавляя рендеринг JS при необходимости.
    """
    load_dotenv()
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key or "ВАШ_API_КЛЮЧ" in api_key:
        print("Ошибка: API-ключ ScraperAPI не найден или не изменен в .env файле.")
        return None
    
    target_url = page_url if page_url else site_config['url']
    base_url = f'http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ua'
    
    # Проверяем, нужно ли включать JS Rendering для этого сайта
    if site_config.get('js_rendering', False):
        print(f"[{site_config['site_name']}] Включаю JS Rendering.")
        return f'{base_url}&render=true'
    
    return base_url

def create_category_folders(category_path):
    """
    Создает иерархию папок по category_path.
    Например: GOODS/GROCERIES/BEVERAGES
    """
    output_dir = "output"
    full_path = os.path.join(output_dir, category_path)
    
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
        print(f"Создана папка: {full_path}")
    
    return full_path

def parse_site_with_pagination(site_config):
    """
    Универсальная функция для парсинга сайта с пагинацией и контролем количества товаров.
    """
    site_name = site_config['site_name']
    category_name = site_config['category_name']
    target_count = site_config['target_count']
    selector = site_config['product_name_selector']
    pagination_template = site_config['pagination_template']
    category_path = site_config['category_path']
    
    print(f"--- [ScraperAPI] Начинаю парсинг сайта: {site_name} ({category_name}) ---")
    print(f"Цель: собрать {target_count} товаров")
    
    # Создаем папки для категории
    output_path = create_category_folders(category_path)
    
    # Формируем имя файла
    filename = f"{site_name}_{category_name}.txt"
    output_filename = os.path.join(output_path, filename)
    
    all_product_names = []
    page = 1
    max_pages = 50  # Защита от бесконечного цикла
    
    while len(all_product_names) < target_count and page <= max_pages:
        print(f"[{site_name}] Страница {page}...")
        
        # Формируем URL для страницы
        if page == 1:
            page_url = site_config['url']
        else:
            if pagination_template.startswith('/'):
                # Для Rozetka: /page=2/
                page_url = site_config['url'].rstrip('/') + pagination_template.format(page=page)
            else:
                # Для Tesco: ?page=2
                if '?' in site_config['url']:
                    page_url = site_config['url'] + '&' + pagination_template.format(page=page)
                else:
                    page_url = site_config['url'] + pagination_template.format(page=page)
        
        print(f"[{site_name}] URL страницы: {page_url}")
        
        api_url = get_scraperapi_url(site_config, page_url)
        if not api_url:
            break
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(api_url, headers=headers, timeout=120)
            response.raise_for_status()
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            product_elements = soup.select(selector)
            
            page_products = [elem.get_text(strip=True) for elem in product_elements if elem.get_text(strip=True)]
            
            if not page_products:
                print(f"[{site_name}] На странице {page} товары не найдены. Завершаю парсинг.")
                break
            
            # Добавляем только новые товары (избегаем дубликатов) с контролем количества
            new_products = []
            for product in page_products:
                if product not in all_product_names:
                    new_products.append(product)
                    all_product_names.append(product)
                    
                    # Проверяем, достигли ли целевого количества
                    if len(all_product_names) >= target_count:
                        print(f"[{site_name}] ✅ Достигнуто целевое количество: {len(all_product_names)} товаров")
                        break
            
            print(f"[{site_name}] Страница {page}: найдено {len(page_products)} товаров, новых: {len(new_products)}")
            print(f"[{site_name}] Всего собрано: {len(all_product_names)} из {target_count}")
            
            # Если достигли целевого количества, выходим из цикла
            if len(all_product_names) >= target_count:
                break
            
            # Если на странице нет новых товаров, возможно, мы достигли конца
            if not new_products:
                print(f"[{site_name}] Новых товаров на странице {page} не найдено. Завершаю парсинг.")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"[{site_name}] Ошибка сетевого запроса на странице {page}: {e}")
            break
        except Exception as e:
            print(f"[{site_name}] Произошла непредвиденная ошибка на странице {page}: {e}")
            break
        
        page += 1
        time.sleep(2)  # Пауза между запросами
    
    # Сохраняем результаты
    with open(output_filename, 'w', encoding='utf-8') as f:
        for name in all_product_names:
            f.write(name + '\n')
    
    print(f"--- Парсинг сайта {site_name} завершен. Найдено: {len(all_product_names)} товаров. ---")
    print(f"Результаты сохранены в файл: {output_filename}")
    return all_product_names

def main():
    """
    Основная функция для запуска парсеров для всех сайтов в конфиге.
    """
    with open('config.json', 'r', encoding='utf-8') as f:
        configs = json.load(f)
    
    all_results = {}
    
    for site_config in configs:
        site_name = site_config['site_name']
        category_name = site_config['category_name']
        target_count = site_config['target_count']
        
        print(f"\n{'='*60}")
        print(f"НАЧИНАЮ ПАРСИНГ: {site_name.upper()} - {category_name.upper()}")
        print(f"ЦЕЛЬ: {target_count} товаров")
        print(f"{'='*60}")
        
        names = parse_site_with_pagination(site_config)
        all_results[f"{site_name}_{category_name}"] = names
        
    print(f"\n\n{'='*60}")
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print(f"{'='*60}")
    
    total_products = 0
    for site_category, names in all_results.items():
        print(f"{site_category}: {len(names)} товаров")
        total_products += len(names)
    
    print(f"\nОБЩИЙ ИТОГ: {total_products} товаров")
    print(f"Результаты сохранены в папке output/")

if __name__ == "__main__":
    main()
