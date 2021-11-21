import os
import sys
import design
import ctypes
import psutil
import subprocess
from PyQt5 import QtWidgets
from darktheme.widget_template import DarkPalette


# Получение информации с консоли
def get_console_info():
    # Кодировка консоли
    l_encoding = ctypes.windll.kernel32.GetConsoleOutputCP()
    # Вызов нужной команды
    l_call = subprocess.Popen(["powercfg", "/query",
                               "381b4222-f694-41f0-9685-ff5bb260df2e",
                               "54533251-82be-4824-96c1-47b60b740d00",
                               "be337238-0d82-4146-a960-4f3749d470c7"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True,
                              encoding=str(l_encoding))

    l_output, l_errors = l_call.communicate()

    # Разделяем по строкам
    l_console_list = l_output.splitlines()

    # Парсим строку, убираем лишние пробелы
    for i, val in enumerate(l_console_list):
        l_console_list[i] = list(filter(None, val.split(' ')))

    # Убираем оставшиеся пустые значения списка
    l_console_list = [value for value in l_console_list if value != []]

    # Две последние строки записываем в новую переменную
    l_parameters = l_console_list[-2:]
    l_charger = l_parameters[0]
    # l_battery = l_parameters[1] - данный параметр по идее не нужен, но пусть будет:)

    return l_charger[-1][-1]


def set_power_parameter(p_charger):
    os.system(f"Powercfg -setacvalueindex scheme_current sub_processor PERFBOOSTMODE {p_charger}")
    os.system("Powercfg -setactive scheme_current")


class PBMapp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton.clicked.connect(self.set_boost_on)
        self.pushButton_2.clicked.connect(self.set_boost_off)
        self.check_setting_status()

    def check_setting_status(self):
        param = get_console_info()
        if param == '0':
            self.label_3.setText("off")
            self.label_3.setStyleSheet("color: red")
        elif param == '1':
            self.label_3.setText("on")
            self.label_3.setStyleSheet("color: green")

    def set_boost_on(self):
        set_power_parameter(1)
        os.startfile("C:\Program Files\Ryzen Controller\Ryzen Controller.exe")
        os.startfile("C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
        self.check_setting_status()

    def set_boost_off(self):
        set_power_parameter(0)
        for process in (process for process in psutil.process_iter() if
                        process.name() == "Ryzen Controller.exe"): process.kill()
        self.check_setting_status()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication\
    app.setPalette(DarkPalette())
    window = PBMapp()
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':
    main()
