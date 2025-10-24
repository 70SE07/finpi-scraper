import json
import os
from dotenv import load_dotenv
import time
import sys
import logging
import asyncio
import aiohttp
import aiofiles

# Импортируем фабрику скрейперов
from scrapers import get_scraper
from utils.categorization import categorize_product

# --- Константы ---
BATCH_SIZE = 2  # Количество одновременных запросов
REQUEST_TIMEOUT = 120  # Таймаут для каждого запроса в секундах
MAX_RETRIES = 3  # Максимальное количество повторных попыток
RETRY_DELAY = 5  # Задержка между повторными попытками в секундах

def get_scraperapi_url(site_config, page_url=None):
    """
    Преобразует целевой URL в URL для запроса к ScraperAPI.
    """
    load_dotenv()
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key or "ВАШ_API_КЛЮЧ" in api_key:
        logging.error("API-ключ ScraperAPI не найден или не изменен в .env файле.")
        return None
    
    target_url = page_url if page_url else site_config['url']
    country = site_config.get('country_code', 'ua')
    base_url = f'http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code={country}'
    
    if site_config.get('js_rendering', False):
        base_url += '&render=true'

    if site_config['site_name'] in ['tesco', 'winestyle', 'rozetka']:
        base_url += '&premium=true&render_wait=5000'
    
    return base_url

async def create_category_folders(category_path):
    """
    Асинхронно создает иерархию папок.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    full_path = os.path.join(output_dir, category_path)
    
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
        logging.info(f"Создана папка: {category_path}")
    
    return full_path

async def load_existing_products(output_filename):
    """
    Асинхронно загружает уже существующие товары из файла.
    """
    if not os.path.exists(output_filename):
        logging.info(f"Файл {os.path.basename(output_filename)} не существует. Начинаю с нуля.")
        return []
    
    try:
        async with aiofiles.open(output_filename, 'r', encoding='utf-8') as f:
            lines = await f.readlines()
            existing_products = [line.strip() for line in lines if line.strip()]
        
        logging.info(f"📁 Найдено {len(existing_products)} существующих товаров в файле {os.path.basename(output_filename)}")
        return existing_products
    except Exception as e:
        logging.error(f"Ошибка чтения файла {os.path.basename(output_filename)}: {e}")
        return []

async def load_external_keywords(keywords_file):
    """
    Асинхронно загружает весь файл ключевых слов как есть.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_keywords_path = os.path.join(script_dir, keywords_file)

    if not os.path.exists(full_keywords_path):
        logging.warning(f"Файл ключевых слов не найден: {keywords_file}")
        return None
    
    try:
        async with aiofiles.open(full_keywords_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        logging.error(f"Ошибка загрузки ключевых слов из {keywords_file}: {e}")
        return None



async def save_products_by_subcategory(all_products, site_name, group_name, category_path, subcategory_keywords, lang):
    """
    Асинхронно сохраняет товары в отдельные файлы по подкатегориям.
    """
    output_path = await create_category_folders(category_path)
    
    # Группировка товаров
    subcategory_products = {}
    if subcategory_keywords:
        for product in all_products:
            subcategory = categorize_product(product, subcategory_keywords, lang)
            if subcategory not in subcategory_products:
                subcategory_products[subcategory] = []
            subcategory_products[subcategory].append(product)
    else:
        # Если нет ключевых слов, используем имя группы как одну категорию
        subcategory_products[group_name] = all_products

    # Асинхронное сохранение файлов
    tasks = []
    for subcategory, products in subcategory_products.items():
        # Используем group_name для основного имени файла
        filename = f"{site_name}_{group_name}_{subcategory}.txt"
        output_filename = os.path.join(output_path, filename)
        
        async def write_file(fname, prods):
            # Используем 'a' для дозаписи, если нужно объединять, но 'w' проще для перезаписи группы
            async with aiofiles.open(fname, 'w', encoding='utf-8') as f:
                await f.write('\n'.join(prods) + '\n')
            logging.info(f"💾 {subcategory.upper()}: {len(prods)} товаров → {os.path.basename(fname)}")
        
        tasks.append(write_file(output_filename, products))
    
    await asyncio.gather(*tasks)
    logging.info(f"📊 Всего подкатегорий: {len(subcategory_products)}")

    # Анализ 'other' для пополнения базы знаний
    if subcategory_keywords and 'other' in subcategory_products and len(subcategory_products['other']) > 0:
        logging.info(f"🔍 Запускаю гибридный анализ для {len(subcategory_products['other'])} товаров из OTHER...")
        try:
            from utils.keyword_extractor import analyze_other_products, update_suggested_stopwords
            
            other_file = os.path.join(output_path, f"{site_name}_{group_name}_other.txt")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            new_keywords, stopword_candidates = analyze_other_products(other_file, lang)
            
            # Сохраняем результаты анализа в отдельный файл, а не в основной
            if new_keywords:
                analysis_results_path = os.path.join(script_dir, "keywords", "other_analysis_results.json")
                async with aiofiles.open(analysis_results_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(new_keywords, ensure_ascii=False, indent=2))
                logging.info(f"📝 Результаты анализа сохранены в {os.path.basename(analysis_results_path)}")

            if stopword_candidates:
                suggested_stopwords_path = os.path.join(script_dir, "keywords/suggested_stopwords.json")
                update_suggested_stopwords(suggested_stopwords_path, stopword_candidates)

        except Exception as e:
            logging.warning(f"Ошибка при анализе OTHER: {e}", exc_info=True)

async def fetch_page(session, url, site_name, page_num):
    """Асинхронно запрашивает одну страницу с логикой повторных попыток."""
    if not url:
        return None
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                logging.info(f"[{site_name}] Стр. {page_num}: успешно загружена (статус {response.status})")
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < MAX_RETRIES - 1:
                logging.warning(f"[{site_name}] Стр. {page_num}: ошибка '{e}', попытка {attempt + 1} из {MAX_RETRIES}. Повтор через {RETRY_DELAY} сек...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                logging.error(f"[{site_name}] Стр. {page_num}: не удалось загрузить после {MAX_RETRIES} попыток. Ошибка: {e}")
                return None
    return None

async def parse_site_with_pagination(site_config, existing_products_set):
    """
    Асинхронно парсит сайт с пагинацией, используя пакетные запросы.
    Возвращает список новых найденных товаров.
    """
    site_name = site_config['site_name']
    category_name = site_config['category_name']
    target_count = site_config['target_count']
    
    logging.info(f"--- Начинаю парсинг: {site_name} ({category_name}) ---")
    logging.info(f"Цель: {target_count} товаров")

    try:
        scraper = get_scraper(site_config)
    except ValueError as e:
        logging.error(e)
        return []

    page = 1
    max_pages = 100
    
    # Используем переданный set, чтобы не было дублей между категориями в одной группе
    local_product_names = set()

    async with aiohttp.ClientSession() as session:
        while len(local_product_names) < target_count and page <= max_pages:
            
            tasks = []
            page_numbers = range(page, page + BATCH_SIZE)
            logging.info(f"[{site_name} - {category_name}] Готовлю пакет запросов для страниц {page}-{page + BATCH_SIZE - 1}...")

            for p_num in page_numbers:
                page_url = scraper.get_page_url(p_num)
                api_url = get_scraperapi_url(site_config, page_url)
                tasks.append(fetch_page(session, api_url, site_name, p_num))

            results = await asyncio.gather(*tasks)
            
            new_products_found_in_batch = False
            for html_content in results:
                if html_content:
                    page_products = scraper.parse(html_content)
                    newly_added = 0
                    for product in page_products:
                        # Проверяем и в глобальном, и в локальном set
                        if product not in existing_products_set and product not in local_product_names:
                            local_product_names.add(product)
                            newly_added += 1
                            new_products_found_in_batch = True
                    
                    if newly_added > 0:
                        logging.info(f"[{site_name} - {category_name}] Найдено {len(page_products)} товаров, новых: {newly_added}")

                if len(local_product_names) >= target_count:
                    logging.info(f"[{site_name} - {category_name}] ✅ Достигнуто целевое количество: {len(local_product_names)} товаров")
                    break
            
            if not new_products_found_in_batch and page > 1:
                logging.warning(f"[{site_name} - {category_name}] Новых товаров не найдено в пакете. Завершаю парсинг.")
                break

            if len(local_product_names) >= target_count:
                break

            page += BATCH_SIZE
            await asyncio.sleep(2) # Увеличим паузу между пакетами

    logging.info(f"--- Парсинг {site_name} ({category_name}) завершен. Собрано: {len(local_product_names)} ---")
    return list(local_product_names)

async def process_config_group(group_key, configs):
    """
    Обрабатывает группу конфигураций (например, все алкогольные напитки с одного сайта).
    """
    site_name, group_name = group_key
    logging.info(f"\n{'='*60}\n🚀 Начинаю обработку группы: {site_name.upper()} - {group_name.upper()}\n{'='*60}")

    all_products_in_group = set()
    
    # Сначала загружаем существующие продукты для этой группы, если они есть
    # (предполагаем, что первая конфигурация репрезентативна для путей)
    base_config = configs[0]
    category_path = base_config['category_path']
    output_path = await create_category_folders(category_path)
    
    # Загружаем все файлы, относящиеся к этой группе, чтобы избежать дублей
    # Пример: rozetka_alcohol_*.txt
    import glob
    existing_files = glob.glob(os.path.join(output_path, f"{site_name}_{group_name}_*.txt"))
    for f in existing_files:
        existing_products = await load_existing_products(f)
        all_products_in_group.update(existing_products)

    initial_count = len(all_products_in_group)
    logging.info(f"[{site_name} - {group_name}] Изначально найдено {initial_count} уникальных товаров в группе.")

    # Последовательно парсим каждую категорию в группе
    for config in configs:
        new_products = await parse_site_with_pagination(config, all_products_in_group)
        all_products_in_group.update(new_products)

    final_product_list = list(all_products_in_group)
    
    # Сохраняем все собранные товары после завершения парсинга всей группы
    if final_product_list:
        subcategory_keywords = await load_external_keywords(base_config.get('external_keywords_file', ''))
        lang = base_config.get("language", "en")
        await save_products_by_subcategory(final_product_list, site_name, group_name, category_path, subcategory_keywords, lang)

    newly_added_count = len(final_product_list) - initial_count
    logging.info(f"--- Обработка группы {site_name.upper()} - {group_name.upper()} завершена. ---")
    logging.info(f"📊 Всего товаров в группе: {len(final_product_list)} (добавлено новых: {newly_added_count})")
    
    return final_product_list


async def main_async():
    """
    Асинхронная основная функция для запуска парсеров.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except Exception as e:
        logging.error(f"Ошибка чтения config.json: {e}")
        return

    if len(sys.argv) > 1:
        target_site_name = sys.argv[1]
        configs = [c for c in configs if c['site_name'] == target_site_name]
        if not configs:
            logging.error(f"Сайт '{target_site_name}' не найден в config.json.")
            return
    
    # Группируем конфигурации по сайту и группе
    grouped_configs = {}
    for config in configs:
        if config.get('enabled', True):
            group_name = config.get('group', config['category_name'])
            site_name = config['site_name']
            key = (site_name, group_name)
            if key not in grouped_configs:
                grouped_configs[key] = []
            grouped_configs[key].append(config)
        else:
            logging.warning(f"ПРОПУСКАЮ: {config['site_name'].upper()} ({config['category_name']}) (отключен)")

    all_results = {}
    for group_key, configs_in_group in grouped_configs.items():
        group_products = await process_config_group(group_key, configs_in_group)
        all_results[f"{group_key[0]}_{group_key[1]}"] = group_products

    # ... (остальная логика)

def main():
    # Настройка логирования
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'scraper.log')
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    console_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Запуск асинхронного кода
    asyncio.run(main_async())

    # Синхронная часть после парсинга
    logging.info(f"\n{'='*60}")
    logging.info("🧹 АВТОМАТИЧЕСКАЯ ОЧИСТКА ТОВАРОВ")
    logging.info(f"{ '='*60}")
    try:
        from utils.clean_products import clean_file
        import glob
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        pattern = os.path.join(output_dir, "**", "*.txt")
        files = glob.glob(pattern, recursive=True)
        if files:
            logging.info(f"📁 Найдено файлов для очистки: {len(files)}")
            success_count = sum(1 for file_path in files if clean_file(file_path))
            logging.info(f"\n✅ ОЧИСТКА ЗАВЕРШЕНА! Успешно обработано: {success_count} из {len(files)} файлов")
        else:
            logging.warning("❌ Файлы для очистки не найдены")
    except Exception as e:
        logging.error(f"❌ Ошибка при автоматической очистке: {e}", exc_info=True)

if __name__ == "__main__":
    main()