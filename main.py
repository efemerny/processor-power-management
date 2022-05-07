import os
import sys
import winreg
import design
import ctypes
import subprocess
import qdarktheme
from elevate import elevate
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *


# Создание каталога и файла cfg
def get_config_path():
    l_filename = os.getenv("SystemDrive") + '/USERS/' + os.getlogin() + '/Documents' + '/PBM' '/cfg.txt'

    if not os.path.exists(os.path.dirname(l_filename)):
        l_dir_name = os.path.dirname(l_filename)
        os.makedirs(l_dir_name)

    return l_filename


# Взять путь из файла
def get_programs_from_file():
    with open(get_config_path()) as file:
        l_list_programs = file.read()

    return list(filter(None, str.split(l_list_programs, '\n')))


# Удаление дубликатов в файле
def delete_duplicates():
    l_program_list = get_programs_from_file()

    for i in l_program_list:
        count = 0
        for j in l_program_list:
            if j == i:
                count += 1

        if count > 1:
            l_without_duplicates = set(l_program_list)
            with open(get_config_path(), 'w') as file:
                for program in l_without_duplicates:
                    file.writelines(program + "\n")
            break



# Изменение параметра реестра на нужный
def get_reg_info():
    l_key_val = r'SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\be337238-0d82-4146-a960-4f3749d470c7'
    l_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, l_key_val)
    l_atr_value = winreg.QueryValueEx(l_key, "Attributes")[0]
    winreg.CloseKey(l_key)

    if l_atr_value != '2':
        l_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, l_key_val, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(l_key, 'Attributes', None, winreg.REG_DWORD, 2)
        winreg.CloseKey(l_key)


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


def run_programs():
    for program in get_programs_from_file():
        os.startfile(f"{program}")

class PBMapp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.listview_model = QtGui.QStandardItemModel(self)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.btn_bst_on.clicked.connect(self.set_boost_on)
        self.btn_bst_off.clicked.connect(self.set_boost_off)
        self.btn_path.clicked.connect(self.put_file_path)
        self.btn_ok_path.clicked.connect(self.save_file_path)
        self.btn_cancel_path.clicked.connect(self.cancel_file_path)
        self.btn_delete_prgm.clicked.connect(self.delete_file_path)
        self.check_setting_status()
        delete_duplicates()
        self.show_programs(get_programs_from_file())

    def show_msgbox(self, p_path):
        msg = QMessageBox()
        msg.setWindowTitle("Error. Duplicate found")
        msg.setText(f"{p_path}\nThis program path has already been selected by you")
        msg.setIcon(QMessageBox.Information)

        x = msg.exec_()

    def show_programs(self, p_list_programs):
        self.listview_model.clear()
        for program in p_list_programs:
            l_item = QtGui.QStandardItem(program)
            l_item.setData(program)
            self.listview_model.appendRow(l_item)
        self.listView.setModel(self.listview_model)

    def check_setting_status(self):
        param = get_console_info()
        if param == '0':
            self.label_status_value.setText("off")
            self.label_status_value.setStyleSheet("color: red")
        elif param == '1':
            self.label_status_value.setText("on")
            self.label_status_value.setStyleSheet("color: green")

    def set_boost_on(self):
        set_power_parameter(1)
        run_programs()
        self.check_setting_status()

    def set_boost_off(self):
        set_power_parameter(0)
        #    for process in (process for process in psutil.process_iter() if
        #                   process.name() == "Ryzen Controller.exe"): process.kill()
        self.check_setting_status()

    def put_file_path(self):
        l_file_path, _ = QFileDialog.getOpenFileName(self, "Choose file",
                                                     ".",
                                                     "Exe Files(*.exe);;All Files(*)")
        if l_file_path:
            self.lineEdit.setText(l_file_path)

    def save_file_path(self):
        l_path_program = self.lineEdit.text()
        self.lineEdit.clear()

        l_flag_duplicate = 'N'

        if l_path_program:
            for program in get_programs_from_file():
                if program == l_path_program:
                    l_flag_duplicate = 'Y'

            if l_flag_duplicate == 'N':
                with open(get_config_path(), "r+") as f:
                    f.seek(0, 2)
                    f.write(f"{l_path_program}" + '\n')
            else:
                self.show_msgbox(l_path_program)

            self.show_programs(get_programs_from_file())

    def cancel_file_path(self):
        self.lineEdit.clear()

    def delete_file_path(self):
        l_index = self.listView.currentIndex()
        l_selected_program = self.listview_model.data(l_index)
        l_list_programs = get_programs_from_file()
        with open(get_config_path(), 'w') as file:
            for program in l_list_programs:
                if program != l_selected_program:
                    file.writelines(program + "\n")

        self.show_programs(get_programs_from_file())

def main():
    elevate(show_console=False)  # Выдаем права администратора
    get_reg_info()  # Установка параметра реестра
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication\
    main_window = PBMapp()
    app.setStyleSheet(qdarktheme.load_stylesheet())
    main_window.show()  # Показываем окно
    sys.exit(app.exec())  # и запускаем приложение


if __name__ == '__main__':
    main()
