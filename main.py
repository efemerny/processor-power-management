import sqlite3
import os
import subprocess
import sys  # sys нужен для передачи argv в QApplication
import design  # Это наш конвертированный файл дизайна
from PyQt5 import QtWidgets


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton.clicked.connect(self.turn_boost_on)
        self.pushButton_2.clicked.connect(self.turn_boost_off)
        if not os.path.exists("my-test.db"):
            self.db_usage()
        else:
            self.check_status()

    def db_usage(self):
        connection = sqlite3.connect("my-test.db")
        crsr = connection.cursor()
        sql_command = """
                CREATE TABLE CHECKER(
                    id INTEGER NOT NULL
                ); """
        crsr.execute(sql_command)
        sql_command = 'INSERT INTO CHECKER values (0)'
        crsr.execute(sql_command)
        connection.commit()
        self.label_3.setText("off")
        self.label_3.setStyleSheet("color: red")
        connection.close()

    def turn_boost_on(self):
        self.set_status(1)
        os.system("Powercfg -setacvalueindex scheme_current sub_processor PERFBOOSTMODE 1")
        os.system("Powercfg -setactive scheme_current")
        os.startfile("C:\Program Files\Ryzen Controller\Ryzen Controller.exe")
        # тут надо вызывать команду для получения текущего статуса питания проца
        #call = subprocess.run(["powercfg", "/query", "381b4222-f694-41f0-9685-ff5bb260df2e", "54533251-82be-4824-96c1-47b60b740d00", "be337238-0d82-4146-a960-4f3749d470c7"], )
        self.check_status()
        self.close()

    def turn_boost_off(self):
        self.set_status(0)
        os.system("Powercfg -setacvalueindex scheme_current sub_processor PERFBOOSTMODE 0")
        os.system("Powercfg -setactive scheme_current")
        self.check_status()
        self.close()

    def set_status(self, p):
        connection = sqlite3.connect("my-test.db")
        crsr = connection.cursor()
        zapr = "UPDATE CHECKER SET id={0}".format(p)
        crsr.execute(zapr)
        connection.commit()
        select = 'SELECT id FROM CHECKER'
        crsr.execute(select)
        status = crsr.fetchone()
        connection.close()

    def check_status(self):
        connection = sqlite3.connect("my-test.db")
        crsr = connection.cursor()
        select = 'SELECT id FROM CHECKER'
        crsr.execute(select)
        status = crsr.fetchone()
        if status[0] == 1:
            self.label_3.setText("on")
            self.label_3.setStyleSheet("color: green")
            connection.close()
        elif status[0] == 0:
            self.label_3.setText("off")
            self.label_3.setStyleSheet("color: red")
            connection.close()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication\
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
