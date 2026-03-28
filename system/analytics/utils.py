from collections import defaultdict
import pandas

from system import config


# Аналитика событий
def data_event_analytics(data_frame: pandas.DataFrame) -> None:
    # Словарь для работы
    result = defaultdict(float)

    # Список разниц
    delays = []

    title = config.Text.TABLE_AVERAGE_TIME_FREE   # Название метрики
    essence_type = config.Text.EssenceType.TABLE  # Тип сущности
    status_table_free = config.Text.Events.TABLE_FREE  # События освобождения столика
    status_table_busy = config.Text.Events.TABLE_BUSY  # События занятия столика

    # Фильтрация данных
    tables = data_frame[data_frame['essence_type'] == essence_type]                  # События только со столиком
    table_free_times = tables[tables['status'] == status_table_free]['time'].values  # Только события свободен
    table_busy_times = tables[tables['status'] == status_table_busy]['time'].values  # Только события занят

    for free_time in table_free_times:                              # Для каждого события свободен
        next_busy = table_busy_times[table_busy_times > free_time]  # Событие позднее

        if len(next_busy) > 0:                       # Если после освобождения есть занятие
            delays.append(next_busy[0] - free_time)  # Добавление в список разниц

    # Расчет среднего значения
    result[title] = sum(delays) / len(delays) if delays else 0

    # Преобразование в обычный dict
    analytics = dict(result)

    # Сохранение отчета
    save_data_xlsx(analytics=analytics)  # Сохранение таблицы
    save_data_txt(analytics=analytics)   # Сохранение текстового файла


# Сохранение таблицы
def save_data_xlsx(analytics: dict) -> None:
    title = config.Text.OutputAnalytics.NAME_XSLX  # Название файла
    name_list = config.Text.ANALYTICS_TITLE        # Название листа

    name_column_metric = config.Text.AnalyticsXLSXColumn.METRIC  # Название колонки метрик
    name_column_value = config.Text.AnalyticsXLSXColumn.VALUE    # Название колонки значений

    # Открытие и сохранение
    with pandas.ExcelWriter(title) as writer:
        df_analytics = pandas.DataFrame(list(analytics.items()), columns=[name_column_metric, name_column_value])  # Преобразование данных
        df_analytics.to_excel(writer, sheet_name=name_list, index=False)                                       # Сохранение данных в лист


# Сохранение текстового файла
def save_data_txt(analytics: dict) -> None:
    title = config.Text.OutputAnalytics.NAME_TXT  # Название файла
    name_group = config.Text.ANALYTICS_TITLE      # Название группы

    with open(title, 'w', encoding='utf-8') as f:  # Создание и отрытие файла
        f.write(f'{name_group}\n')                 # Печать названия группы

        for metric, value in analytics.items():    # Для каждой метрики
            f.write(f'{metric}: {value:.2f}\n')    # Печать метрики и значения
