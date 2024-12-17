#!/usr/bin/env python3
"""
Скрипт для выгрузки позиций из Google Search Console в Google Sheets
"""
import logging
import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Области доступа для API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/webmasters.readonly'
]

# ID таблицы для обновления
SPREADSHEET_ID = '1O66mydYj9B85vciCab9CkZVqjbZTMPMAtn99GZnXA3M'

def create_services(credentials):
    """
    Создание сервисов Google Sheets, Search Console и Drive
    
    Args:
        credentials: Учетные данные сервисного аккаунта
        
    Returns:
        tuple: (sheets_service, webmasters_service, drive_service)
    """
    sheets_service = build('sheets', 'v4', credentials=credentials)
    webmasters_service = build('searchconsole', 'v1', credentials=credentials)
    
    return sheets_service, webmasters_service

def is_branded_query(query):
    """
    Проверяет, является ли запрос брендовым
    
    Args:
        query: Поисковый запрос
        
    Returns:
        bool: True если запрос брендовый
    """
    brand_terms = ['cvety.kz', 'цветы.кз', 'цветыкз', 'cvetykz', 'цветы кз']
    query = query.lower()
    return any(term in query for term in brand_terms)

def get_search_analytics_data(webmasters_service, site_url, start_date, end_date):
    """
    Получение данных о позициях из Search Console
    
    Args:
        webmasters_service: Сервис Search Console
        site_url: URL сайта
        start_date: Начальная дата
        end_date: Конечная дата
        
    Returns:
        list: Список данных о позициях
    """
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query', 'date', 'page'],
        'rowLimit': 25000,
        'startRow': 0,
        'searchType': 'web',
        'aggregationType': 'auto'
    }
    
    response = webmasters_service.searchanalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()
    
    # Получаем все запросы с их суммарными кликами
    query_clicks = {}
    for row in response.get('rows', []):
        query = row['keys'][0]
        page = row['keys'][2]
        
        # Пропускаем брендовые запросы
        if is_branded_query(query):
            continue
            
        if query not in query_clicks:
            query_clicks[query] = {
                'clicks': row['clicks'],
                'page': page,
                'rows': []
            }
        else:
            query_clicks[query]['clicks'] += row['clicks']
        
        query_clicks[query]['rows'].append(row)
    
    # Сортируем запросы по кликам и берем топ-200
    top_queries = sorted(query_clicks.items(), key=lambda x: x[1]['clicks'], reverse=True)[:200]
    
    # Собираем все строки для топ-200 запросов
    filtered_rows = []
    for query, data in top_queries:
        for row in data['rows']:
            row['page'] = data['page']
        filtered_rows.extend(data['rows'])
    
    return filtered_rows

def prepare_data_for_sheets(data, dates):
    """
    Подготовка данных для записи в таблицу
    
    Args:
        data: Данные из Search Console
        dates: Список дат
        
    Returns:
        tuple: (заголовки, строки данных)
    """
    # Группируем данные по запросу
    query_data = {}
    for row in data:
        query = row['keys'][0]
        date = row['keys'][1]
        url = row['page']
        
        if query not in query_data:
            query_data[query] = {
                'url': url,
                'dates': {},
                'total_clicks': 0,
                'total_impressions': 0
            }
        
        query_data[query]['dates'][date] = row['position']
        query_data[query]['total_clicks'] += row['clicks']
        query_data[query]['total_impressions'] += row['impressions']
    
    # Создаем заголовки
    headers = ['Запрос', 'URL', 'Клики', 'Показы'] + dates
    
    # Создаем строки данных
    rows = []
    for query, data in sorted(query_data.items(), key=lambda x: x[1]['total_clicks'], reverse=True):
        row = [
            query,
            data['url'],
            data['total_clicks'],
            data['total_impressions']
        ]
        
        # Добавляем позиции по датам
        for date in dates:
            row.append(round(data['dates'].get(date, ''), 1) if date in data['dates'] else '')
        
        rows.append(row)
    
    return headers, rows

def update_sheets(sheets_service, spreadsheet_id, data, city=None):
    """
    Обновление данных в таблице
    
    Args:
        sheets_service: Сервис Google Sheets
        spreadsheet_id: ID таблицы
        data: Данные для записи
        city: Город (None для общей таблицы)
    """
    sheet_title = 'Sheet1' if not city else city
    
    # Проверяем существование листа и получаем его ID
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_title:
            sheet_id = sheet['properties']['sheetId']
            break
    
    # Если лист не существует, создаем его
    if sheet_id is None:
        request = {
            'addSheet': {
                'properties': {
                    'title': sheet_title
                }
            }
        }
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        sheet_id = result['replies'][0]['addSheet']['properties']['sheetId']
    
    # Очищаем существующие данные
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_title}!A1:Z1000'
    ).execute()
    
    # Обновляем заголовок таблицы
    title = f'Топ 200 запросов по кликам (без брендовых) за последние 7 дней'
    if city:
        title += f' - {city}'
    
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_title}!A1',
        valueInputOption='RAW',
        body={'values': [[title]]}
    ).execute()
    
    # Записываем данные
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_title}!A2',
        valueInputOption='RAW',
        body={'values': data}
    ).execute()
    
    # Форматируем таблицу
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 2,
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }
    ]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

def filter_data_by_city(data, city):
    """
    Фильтрация данных по городу
    
    Args:
        data: Исходные данные
        city: Город (Астана или Алматы)
    
    Returns:
        list: Отфильтрованные данные
    """
    city_keywords = {
        'Астана': ['астана', 'нур-султан'],
        'Алматы': ['алматы', 'алмата']
    }
    
    filtered_data = []
    for row in data:
        query = row['keys'][0].lower()
        url = row['page'].lower()
        
        # Проверяем наличие города в запросе или URL
        if any(kw in query or kw in url for kw in city_keywords[city]):
            filtered_data.append(row)
    
    return filtered_data

def main():
    try:
        # Путь к файлу сервисного аккаунта
        service_account_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'dashbords-373217-20faafe15e3f.json'
        )
        
        # Создаем credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )
        
        # Создаем сервисы
        sheets_service, webmasters_service = create_services(credentials)
        
        # Параметры для выгрузки
        site_url = 'sc-domain:cvety.kz'
        end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d')
        
        # Получаем данные из Search Console
        logger.info(f"Получаем данные из Search Console за период {start_date} - {end_date}")
        data = get_search_analytics_data(webmasters_service, site_url, start_date, end_date)
        
        # Подготавливаем список дат
        dates = []
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        # Обновляем общую таблицу
        logger.info(f"Обновляем таблицу: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        headers, rows = prepare_data_for_sheets(data, dates)
        all_rows = [headers] + rows
        update_sheets(sheets_service, SPREADSHEET_ID, all_rows)
        
        # Обновляем таблицы по городам
        for city in ['Астана', 'Алматы']:
            logger.info(f"Обновляем данные для города {city}")
            city_data = filter_data_by_city(data, city)
            headers, rows = prepare_data_for_sheets(city_data, dates)
            all_rows = [headers] + rows
            update_sheets(sheets_service, SPREADSHEET_ID, all_rows, city)
        
        logger.info(f"Данные успешно обновлены")
        
    except Exception as e:
        logger.error(f"Ошибка при работе со скриптом: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
