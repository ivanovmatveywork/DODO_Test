import time

from shapely.geometry import Polygon
from shapely.ops import orient
import numpy
import torch
import cv2

from system.rule import Markings, Person, Table, PersonStatus, TableStatus
from system.analytics import event_save
from system import config
from .display import *
from .auxiliary import *


# Получение данных видео
def get_video_data(video: cv2.VideoCapture) -> tuple[int, int, int, int]:
    video_fps = int(video.get(cv2.CAP_PROP_FPS))                  # Количество кадров
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))        # Ширина
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))      # Высота
    video_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # Количество кадров

    # Возвращение данных
    return video_fps, video_width, video_height, video_frame_count


# Получение оборудования для работы (GPU/CPU)
def device_check() -> tuple[str, str]:
    if torch.cuda.is_available():                   # Есть ли КУДА ядра
        device_log = config.Text.LOG_DEVICE_US_GPU  # Лог текст
        device = '0'                                # Видеокарта
    else:
        device_log = config.Text.LOG_DEVICE_US_CPU  # Лог текст
        device = 'cpu'                              # Процессор

    # Возвращение текста и типа оборудования
    return device_log, device


# Расчет зоны интереса
def get_area_interest_coordinates(table_coordinates: list[list[int, int]]) -> list[list[int, int]]:
    # Размер отступа
    padding = config.Tech.AreaInterest.SIZE

    # Создание полигона
    poly = Polygon(table_coordinates)
    poly = orient(poly, sign=1.0)      # Упорядочивание

    expanded_poly = poly.buffer(
        distance=padding,    # Отступ от стола
        resolution=16,       # Сглаживание углов. Лучше не делать меньше 16. даже при прямых углах
        cap_style=1,         # Форма концов линий
        join_style='mitre',  # Тип соединения углов
        mitre_limit=2.0      # Ограничение вытягивания
    )

    # Получение списка координат (нормализация)
    area_interest_coordinates = [
        [int(x), int(y)]
        for x, y in expanded_poly.exterior.coords[:-1]
    ]

    # Возвращение координат
    return area_interest_coordinates


# Получение ID и координат обнаруженных посетителей
def persons_detection(results) -> dict[list[list[int, int]]]:
    persons = {}

    if results[0].boxes is not None:  # Если есть обнаружения
        for box in results[0].boxes:  # Если есть бокс
            if box.id is None:        # Если нет идентификатора, то пропуск
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])                  # Получение координат
            person_id = int(box.id[0])                              # Получение идентификатора
            coordinates = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]  # Группирование координат

            persons[person_id] = coordinates

    # Возвращение списка данных посетителей
    return persons


# Сортировка посетителей на группы (В зоне интереса, Вне зоны интереса)
def persons_sort(
    persons: list[Person],
    area_interest_coordinates: list[list[int, int]]
) -> tuple[dict[list[list[int, int]]], dict[list[list[int, int]]]]:

    persons_involved = {}
    persons_free = {}

    for person in persons:                                                                                       # Для каждого посетителя
        if person_over_table(person_bbox=persons[person], area_interest_coordinates=area_interest_coordinates):  # Если пересекается
            persons_involved[person] = persons[person]                                                           # Добавляем в группу пересекающих
        else:                                                                                                    # Если не пересекается
            persons_free[person] = persons[person]                                                               # Добавляем в группу не пересекающих

    # Возвращение списков групп
    return persons_free, persons_involved


# Обновление данных посетителей в кеше
def person_data_update(
    frames_score: int,
    persons_global: dict[Person],
    persons_free: dict[list[list[int, int]]],
    persons_involved: dict[list[list[int, int]]]
) -> dict[int, Person]:

    persons_visibility_id = []
    persons_global_new = {}

    # Категория сущности
    essence_type = config.Text.EssenceType.PERSON

    # Получение списка посетителей, которых видно. Нужно для определения "не видимых" (отсутствующих) посетителей
    for person_id in persons_free:
        persons_visibility_id.append(person_id)
    for person_id in persons_involved:
        persons_visibility_id.append(person_id)

    # Обновление отсутствующих посетителей
    person_data_update_invisibility(persons_global=persons_global, persons_global_new=persons_global_new, persons_visibility_id=persons_visibility_id)

    # Обновление свободных посетителей
    person_data_update_free(persons_global=persons_global, persons_global_new=persons_global_new, persons_free=persons_free)

    # Обновление посетителей в зоне интереса
    person_data_update_involved(persons_global=persons_global, persons_global_new=persons_global_new, persons_involved=persons_involved)

    # Сохранение событий
    for person_id, person in persons_global_new.items():  # Для каждого посетителя
        event_save(                                       # Сохранение события
            frame=frames_score,                           # Номер кадра
            essence_type=essence_type,                    # Тип сущности
            essence_id=person_id,                         # Идентификатор
            status=person.status.text_event               # Ивент текст статуса
        )

    # Возвращение сущностей посетителей
    return persons_global_new


# Обновление данных стола
def table_data_update(
    frames_score: int,
    table_coordinates: list[list[int, int]],
    area_interest_coordinates: list[list[int, int]],
    persons_global: dict[Person]
) -> Table:

    # Статус по умолчанию
    status = TableStatus.Free()

    # Время для зачтения стола занятым
    time_lock = config.Tech.AreaInterest.TIME_LOCK

    # Категория сущности
    essence_type = config.Text.EssenceType.TABLE

    # Поиск в кеше посетителя с количеством кадров "За столиком" с порогом занятия стола
    for _, peron in persons_global.items():     # Для каждого посетителя
        if peron.involved_frames >= time_lock:  # Если порог занятия стола
            status = TableStatus.Busy()         # Новый статус

    # Создание сущности стола
    table = Table(
        coordinates=table_coordinates,
        area_interest_coordinates=area_interest_coordinates,
        status=status
    )

    # Сохранение события
    event_save(                     # Сохранение события
        frame=frames_score,         # Номер кадра
        essence_type=essence_type,  # Тип сущности
        essence_id=1,               # Идентификатор. По скольку стол один, ID всегда равен 1
        status=status.text_event    # Ивент текст статуса
    )

    # Возвращение сущности стола
    return table


# Визуализация данных
def screen_layout(frame: numpy.ndarray, markings: Markings, frames_score: int, display_size: list[int, int]) -> numpy.ndarray:
    table = markings.table      # Сущность стола
    persons = markings.persons  # Список сущностей посетителей

    # Визуализация данных стола
    table_polygon_display(frame=frame, table=table)

    for _, person in persons.items():                           # Для каждого посетителя
        if person.invisibility_frames < 1:                      # Если есть в кадре
            person_polygon_display(frame=frame, person=person)  # Визуализация данных посетителя

    # Визуализация номера кадра
    frame_display(frame=frame, frames_score=frames_score, display_size=display_size)

    # Возвращение кадра
    return frame


# Расчет времени выполнения программы
def get_program_process_duration(start_time: float) -> str:
    # Секунды выполнения
    time_duration = time.time() - start_time

    hours = int(time_duration // 3600)           # Часы
    minutes = int((time_duration % 3600) // 60)  # Минуты
    seconds = int(time_duration % 60)            # Секунды

    # Формат вывода
    time_duration = f'{hours:02}:{minutes:02}:{seconds:02}'

    # Возвращение затраченного времени
    return time_duration
