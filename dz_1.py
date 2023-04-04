"""
Задача 1. Каждое из слов «разработка», «сокет», «декоратор» представить
в строковом формате и проверить тип и содержание соответствующих переменных.
Затем с помощью онлайн-конвертера преобразовать строковые представление
в набор кодовых точек Unicode и также проверить тип и содержимое переменных.
"""

STR_LIST = ['разработка','сокет', 'декоратор']

for i in STR_LIST:
    print(i)
    print(type(i))
 

UNICODE_LIST = ["\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430", "\u0441\u043e\u043a\u0435\u0442", 
             "\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440"]

for i in UNICODE_LIST:
    print(i, type(i))


"""
Задача 2. Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.
"""
words = [b'class', b'function', b'method']

for i in words:
    print("содержание переменной - ", i)
    print("тип переменной - ",type(i))
    print("длинна строки - ", len(i))

"""
Задача 3. Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b''.

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- Попробуйте усложнить задачу, "отлавливая" и обрабатывая исключение
"""

list = ['attribute', 'класс', 'функция', 'type']

for i in list:
    try:
        print(bytes(i, 'ascii'))
    except UnicodeEncodeError:
        print(f'Слово "{i}" невозможно записать в виде байтовой строки')

# ИСКЛЮЧЕНИЕ
# функция eval() интерпретирует строку как код
for i in list:
    try:
        print('Слово записано в байтовом типе:', eval(f'b"{i}"'))
    except SyntaxError:
        print(
            f'Слово "{i}" невозможно записать в байтовом типе с помощью префикса b')

"""
Задача 4. Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).
"""

word = ['разработка', 'администрирование', 'protocol', 'standard']

for i in word:
    en = i.encode('utf-8')
    de = bytes.decode(en, 'utf-8')
    print(en, type(en), de, type(de))

"""
Задача 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.
"""

import subprocess
import chardet

word_1 = ['ping', 'yandex.ru']
ping_1 = subprocess.Popen(word_1, stdout=subprocess.PIPE)
for p_1 in ping_1.stdout:
    result = chardet.detect(p_1)
    print(result)
    p_1 = p_1.decode(result['encoding']).encode('utf-8')
    print(p_1.decode('utf-8'))

word_2 = ['ping', 'youtube.com']
ping_2 = subprocess.Popen(word_2, stdout=subprocess.PIPE)
for p_2 in ping_2.stdout:
    result = chardet.detect(p_2)
    print(result)
    p_2 = p_2.decode(result['encoding']).encode('utf-8')
    print(p_2.decode('utf-8'))

"""
Задача 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""

import sys
import locale
import chardet
from locale import getdefaultlocale

getdefaultlocale = (lambda *args: ['en_US', 'utf-8'])

LINES_LST = ['сетевое программирование', 'сокет', 'декоратор']
with open('test_file.txt', 'w') as file:
    for line in LINES_LST:
        file.write(f'{line}\n')
file.close()

with open('test_file.txt', 'r') as file:
    CONTENT = file.read()
print(CONTENT)
