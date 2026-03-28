import pandas

from system import config
from .utils import *


events = []  # Кеш событий


# Сохранения события
def event_save(frame: int, essence_type: str, essence_id: int, status: str) -> None:
    events.append({
        'frame': frame,                # Номер кадра
        'essence_type': essence_type,  # Тип сущности
        'essence_id': essence_id,      # Идентификатор
        'status': status               # Ивент текст статуса
    })


# Запуск аналитики
def start_analytics(fps: int) -> None:
    events_new = []

    # Преобразование данных
    for event in events:                            # Для каждого события
        time = event['frame'] / fps                 # Время события. Номер кадра / FPS
        events_new.append({                         # Запись данных
            'time': time,                           # Время события
            'essence_type': event['essence_type'],  # Тип сущности
            'essence_id': event['essence_id'],      # Идентификатор
            'status': event['status']}              # Ивент текст статуса
        )

    data_frame = pandas.DataFrame(events_new)    # Сохранение в виде DataFrame
    data_event_analytics(data_frame=data_frame)  # Аналитика событий
