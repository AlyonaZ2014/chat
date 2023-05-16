"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from ipaddress import ip_address
from task_9_1 import host_ping


def host_range_ping():
    while True:
        start = input('Введите первоначальный адрес: ')
        try:
            octet = int(start.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        end_ip = input('Сколько адресов проверить?: ')
        if not end_ip.isnumeric():
            print('Необходимо ввести число: ')
        else:
            if (octet+int(end_ip)) > 254:
                print(f"Можем менять только последний октет, т.е. "
                      f"максимальное число хостов для проверки: {254-octet}")
            else:
                break

    host_list = []
    [host_list.append(str(ip_address(start)+x)) for x in range(int(end_ip))]
    return host_ping(host_list)


if __name__== "__main__":
    host_range_ping()


