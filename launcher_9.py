import os.path
import subprocess


def launcher():
    processes = []
    env = os.environ.copy()
    env['PATH'] = r"C:\Python\асинхронный чат\chat\venv\Scripts"
    action = input("Сколько клиентов запустить: ")
    try:
        action = int(action)
    except ValueError:
        action = None

    if action is not None:
        for i in range(action):
            start = ['google.ru', '2.2.2.2', '192.168.0.100', '192.168.0.101'
            #     r"C:\Python\ассинхронный чат\chat\venv\Scripts\python.exe",
            #     r"C:\Python\ассинхронный чат\chat\client.py",
            #     # r".\chat\venv\Scriptspython.exe",
            #     # r".\chatclient.py",
            #     "localhost"
            ]
            processes.append(subprocess.Popen(start, env=env, creationflags=subprocess.CREATE_NEW_CONSOLE))
    for process in processes:
        print(process.returncode)
        print(process.stdout)
    while True:
        action = input('Для закрытие клиентов введите "exit"')
        if action.lower() == 'exit':
            while processes:
                process = processes.pop()
                process.kill()


if __name__ == "__main__":
    launcher()