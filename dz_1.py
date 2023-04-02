# """
# Задача 1. Каждое из слов «разработка», «сокет», «декоратор» представить
# в строковом формате и проверить тип и содержание соответствующих переменных.
# Затем с помощью онлайн-конвертера преобразовать строковые представление
# в набор кодовых точек Unicode и также проверить тип и содержимое переменных.
# """

# STR_LIST = ['разработка','сокет', 'декоратор']

# for i in STR_LIST:
#     print(i)
#     print(type(i))
 

# UNICODE_LIST = ["\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430", "\u0441\u043e\u043a\u0435\u0442", 
#              "\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440"]

# for i in UNICODE_LIST:
#     print(i, type(i))


# """
# Задача 2. Каждое из слов «class», «function», «method» записать в байтовом формате
# без преобразования в последовательность кодов
# не используя методы encode и decode)
# и определить тип, содержимое и длину соответствующих переменных.
# """
# words = [b'class', b'function', b'method']

# for i in words:
#     print("содержание переменной - ", i)
#     print("тип переменной - ",type(i))
#     print("длинна строки - ", len(i))

# """
# Задача 3. Определить, какие из слов «attribute», «класс», «функция», «type»
# невозможно записать в байтовом типе с помощью маркировки b''.

# Подсказки:
# --- используйте списки и циклы, не дублируйте функции
# --- Попробуйте усложнить задачу, "отлавливая" и обрабатывая исключение
# """

# list = ['attribute', 'класс', 'функция', 'type']

# for i in list:
#     try:
#         print(bytes(i, 'ascii'))
#     except UnicodeEncodeError:
#         print(f'Слово "{i}" невозможно записать в виде байтовой строки')

# # ИСКЛЮЧЕНИЕ
# # функция eval() интерпретирует строку как код
# for i in list:
#     try:
#         print('Слово записано в байтовом типе:', eval(f'b"{i}"'))
#     except SyntaxError:
#         print(
#             f'Слово "{i}" невозможно записать в байтовом типе с помощью префикса b')

# """
# Задача 4. Преобразовать слова «разработка», «администрирование», «protocol»,
# «standard» из строкового представления в байтовое и выполнить
# обратное преобразование (используя методы encode и decode).

# Подсказки:
# --- используйте списки и циклы, не дублируйте функции
# """

# word = ['разработка', 'администрирование', 'protocol', 'standard']

# for i in word:
#     en = i.encode('utf-8')
#     de = bytes.decode(en, 'utf-8')
#     print(en, type(en), de, type(de))

# """
# Задача 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
# преобразовать результаты из байтовового в строковый тип на кириллице.
# """

# import subprocess
# import chardet

# word_1 = ['ping', 'yandex.ru']
# ping_1 = subprocess.Popen(word_1, stdout=subprocess.PIPE)
# for p_1 in ping_1.stdout:
#     result = chardet.detect(p_1)
#     print(result)
#     p_1 = p_1.decode(result['encoding']).encode('utf-8')
#     print(p_1).decode('utf-8')

# word_2 = ['ping', 'youtube.com']
# ping_2 = subprocess.Popen(word_2, stdout=subprocess.PIPE)
# for p_2 in ping_2.stdout:
#     result = chardet.detect(p_2)
#     print(result)
#     p_2 = p_2.decode(result['encoding']).encode('utf-8')
#     print(p_2.decode('utf-8'))

"""
Задача 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""
from chardet import detect

with open('test.txt', encoding='utf-8') as file:
    for line in file.read():
        print(line)
file.close()

# UnicodeDecodeError: 'utf-8' codec can't decode
# byte 0xf0 in position 0: invalid continuation byte


# открываем файл в правильной кодировке
file = open('test.txt', 'rb')
for line in file:
    print(line.decode(encoding='utf-8'))


from chardet.universaldetector import UniversalDetector

LINES_LST = ['сетевое программирование', 'сокет', 'декоратор']
with open('test.txt', 'w') as file:
    for line in LINES_LST:
        file.write(f'{line}\n')
file.close()

# узнаем кодировку файла

"""
Если файл имеет большой размер, то вместо считывания его целиком в строку
и использования функции detect() можно воспользоваться классом UniversalDetector.
В этом случае можно читать файл построчно и передавать текущую строку методу feed().
Если определение кодировки прошло успешно, атрибут done будет иметь значение True.
Это условие можно использовать для выхода из цикла.
После окончания проверки следует вызвать метод close().
Получить результат определения кодировки позволяет атрибут result
"""

DETECTOR = UniversalDetector()
with open('test.txt', 'rb') as test_file:
    for i in test_file:
        DETECTOR.feed(i)
        if DETECTOR.done:
            break
    DETECTOR.close()
print(DETECTOR.result['encoding'])

# открываем файл в правильной кодировке
with open('test.txt', 'r', encoding=DETECTOR.result['encoding']) as file:
    CONTENT = file.read()
print(CONTENT)



from chardet import detect

#with open('test.txt', encoding='utf-8') as file:
    #for line in file.read():
        #print(line)
#file.close()

# UnicodeDecodeError: 'utf-8' codec can't decode
# byte 0xf0 in position 0: invalid continuation byte


def encoding_convert():
    """Конвертация"""
    with open('test.txt', 'rb') as f_obj:
        content_bytes = f_obj.read()
    detected = detect(content_bytes)
    print(detected)
    encoding = detected['encoding']
    content_text = content_bytes.decode(encoding)
    with open('test.txt', 'w', encoding='utf-8') as f_obj:
        f_obj.write(content_text)

encoding_convert()

# открываем файл в правильной кодировке
with open('test.txt', encoding='utf-8') as file:
    CONTENT = file.read()
print(CONTENT)

import sys
from _locale import _getdefaultlocale

# изменение кодировки локали

_getdefaultlocale = (lambda *args: ['en_US', 'utf-8'])

LINES_LST = ['сетевое программирование', 'сокет', 'декоратор']
with open('test.txt', 'w') as file:
    for line in LINES_LST:
        file.write(f'{line}\n')
file.close()

# открываем файл в правильной кодировке
with open('test.txt', 'r') as file:
    CONTENT = file.read()
print(CONTENT)

from chardet import detect

# узнаем кодировку файла
with open('44444', 'rb') as file:
    CONTENT = file.read()

print(detect(CONTENT))
ENCODING = detect(CONTENT)['encoding']
print(ENCODING)

# открываем файл в правильной кодировке
with open('44444', 'r', encoding=ENCODING) as file:
    CONTENT = file.read()
print(CONTENT)

a = 'weqr4ee'
NEWFILE = open('test.txt', 'w')
NEWFILE.write('сетевое программирование\nсокет\nдекоратор')
NEWFILE.close()

with open('test.txt') as codedFile:
    print(f'Кодировка файла: {codedFile.encoding}')
    for line in codedFile:
        # преобразуем содержимое в utf-8
        encd_line = line.encode('utf-8')
        # декодируем содержимое
        dcd_line = encd_line.decode('utf-8')
        print(dcd_line)