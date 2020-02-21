#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import telebot


class OtherFuncs:

    # Сравнение старых и текущих данных о пользователе
    @staticmethod
    def compare_user_data(old_user_data, new_user_data):
        if str(old_user_data[1]).strip() != new_user_data.from_user.username:
            return False
        if str(old_user_data[2]).strip() != new_user_data.from_user.first_name:
            return False
        if str(old_user_data[3]).strip() != new_user_data.from_user.last_name:
            return False
        if str(old_user_data[5]).strip() != new_user_data.from_user.language_code:
            return False
        if str(old_user_data[7]).strip() != new_user_data.from_user.is_bot:
            return False

        return True

    # Замена None за пустую строку
    @staticmethod
    def check_none(string):
        return '' if str(string).strip() == 'None' else str(string).strip()

    # Сортировка списка записей по времени по возрастанию
    @staticmethod
    def sort_times(times_data, type_func):
        new_times_data = []

        if type_func == 1:
            new_times_data = sorted(times_data, key=lambda row: (row[3], row[2], row[4]), reverse=False)
        elif type_func == 2:
            new_times_data = sorted(times_data, key=lambda row: (row[12], row[11], row[13]), reverse=False)

        return new_times_data

    # Преобразование к формату ЦЦ:ЦЦ
    @staticmethod
    def check_time_before(data_time):
        if len(data_time) == 5:
            if re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', data_time):
                return data_time.replace(' ', ':')
            return data_time
        elif len(data_time) == 4:
            if re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', data_time):
                return '0' + data_time.replace(' ', ':')
            return '0' + data_time
        elif len(data_time) == 2:
            return data_time + ':00'
        elif len(data_time) == 1:
            return '0' + data_time + ':00'
        elif len(data_time) == 0:
            return ''

    # Проверка границ введенного времени
    @staticmethod
    def check_inserted_time(time_data):
        return True if '00:00' <= time_data < '23:59' else False

    # Приведение дня и месяца к виду ЦЦ
    @staticmethod
    def check_date_format(date_data):
        if int(date_data) < 10:
            return '0' + str(date_data)
        else:
            return date_data

    # Основная клавиатура
    @staticmethod
    def get_start_keyboard():
        start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
        start_keyboard.row('Занять переговорку', 'Изменить запись', 'Удалить запись')
        start_keyboard.row('Моя занятость', 'Занятость переговорки')
        start_keyboard.row('Дата', 'Справка', 'Кот')

        return start_keyboard

    # Кнопка "Отмена"
    @staticmethod
    def get_cancel_button():
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.add('Отмена')

        return keyboard
