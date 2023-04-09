"""
2. Задание на закрепление знаний по модулю json. Есть файл orders
в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий
его заполнение данными.

Для этого:
Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date). Функция должна предусматривать запись
данных в виде словаря в файл orders.json. При записи данных указать
величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра.
"""
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def write_order_to_json(item, quantity, price, buyer, date ):
    filename = os.path.join(current_dir, 'orders.json')
    if os.path.exists(filename):
        data = {}
        with open(filename, encoding="utf-8") as f_n:
            data = json.loads(f_n.read())
        data['orders'].append({'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date})
        with open(filename, "w", encoding="utf-8") as f_n:
            json.dump(data, f_n, indent=4, separators=(',', ': '), ensure_ascii=False)
        print(f'Данные добавлены в {filename}')
        with open(filename) as f_n:
            objs = json.load(f_n)
            for section, commands in data.items():
                return commands

    else:
        return f'Файл по пути {filename} не найден'


write_order_to_json('телефон', '2', '20000', 'Иванов', '28.01.2023')
write_order_to_json('автомобиль', '1', '2000000', 'Рыбовв', '26.01.2023')