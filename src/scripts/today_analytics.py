from src.services.yandex_metrika import YandexMetrikaAPI
import pandas as pd
from datetime import datetime

def get_today_analytics():
    """
    Получение детальной аналитики за сегодня
    """
    # Инициализация клиента
    token = 'y0_AgAAAAAIQVdQAAzyygAAAAEcFYUiAACbs5T2SZBAtbCrBXrF7T-3NHSfVw'
    counter_id = 26416359
    
    try:
        metrika = YandexMetrikaAPI(token, counter_id)
        today = 'today'
        
        # 1. Данные по заказам и доходам
        print("\n💰 Общая статистика по заказам:")
        ecommerce_params = {
            'date1': today,
            'date2': today,
            'metrics': 'ym:s:visits,ym:s:ecommercePurchases,ym:s:ecommerceKZTConvertedRevenue',
            'dimensions': 'ym:s:date',
        }
        ecommerce_data = metrika._make_request(ecommerce_params)
        if ecommerce_data['data']:
            visits = ecommerce_data['data'][0]['metrics'][0]
            purchases = ecommerce_data['data'][0]['metrics'][1]
            revenue = ecommerce_data['data'][0]['metrics'][2]
            conversion = (purchases / visits * 100) if visits > 0 else 0
            print(f"Количество визитов: {visits:,.0f}")
            print(f"Количество заказов: {purchases:,.0f}")
            print(f"Конверсия: {conversion:.1f}%")
            print(f"Общий доход: {revenue:,.0f} тг")
            if purchases > 0:
                print(f"Средний чек: {revenue/purchases:,.0f} тг")
        
        # 2. Детальная информация по заказам
        print("\n📦 Детальная информация по заказам:")
        orders_params = {
            'date1': today,
            'date2': today,
            'metrics': 'ym:s:ecommerceKZTConvertedRevenue',
            'dimensions': 'ym:s:purchaseID,ym:s:lastTrafficSource',
            'sort': '-ym:s:ecommerceKZTConvertedRevenue'
        }
        orders_data = metrika._make_request(orders_params)
        
        if orders_data['data']:
            orders_df = pd.DataFrame([
                {
                    'Номер заказа': item['dimensions'][0]['name'],
                    'Источник': item['dimensions'][1]['name'],
                    'Сумма': f"{item['metrics'][0]:,.0f} тг",
                }
                for item in orders_data['data']
            ])
            print("\nСписок заказов:")
            print(orders_df.to_string(index=False))
        else:
            print("Заказов за сегодня не найдено")
        
        # 3. Статистика по каналам
        print("\n📊 Статистика по каналам:")
        channel_params = {
            'date1': today,
            'date2': today,
            'metrics': 'ym:s:visits,ym:s:ecommercePurchases,ym:s:ecommerceKZTConvertedRevenue',
            'dimensions': 'ym:s:trafficSource',
            'sort': '-ym:s:ecommerceKZTConvertedRevenue'
        }
        channels_data = metrika._make_request(channel_params)
        
        channels_df = pd.DataFrame([
            {
                'Канал': item['dimensions'][0]['name'],
                'Визиты': item['metrics'][0],
                'Заказы': item['metrics'][1],
                'Конверсия': f"{(item['metrics'][1]/item['metrics'][0]*100):.2f}%" if item['metrics'][0] > 0 else "0%",
                'Доход': f"{item['metrics'][2]:,.0f} тг",
            }
            for item in channels_data['data']
        ])
        
        print("\nДетальная статистика по каналам:")
        print(channels_df.to_string(index=False))
        
        # 4. Сохранение отчета
        print("\n💾 Сохраняем отчет...")
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # Создаем директорию если её нет
        import os
        os.makedirs('reports', exist_ok=True)
        
        with pd.ExcelWriter(f'reports/ecommerce_report_{today_str}.xlsx') as writer:
            if 'orders_df' in locals():
                orders_df.to_excel(writer, sheet_name='Заказы', index=False)
            channels_df.to_excel(writer, sheet_name='Каналы', index=False)
            
        print(f"✅ Отчет сохранен в файл: ecommerce_report_{today_str}.xlsx")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    get_today_analytics()
