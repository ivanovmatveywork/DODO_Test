import time
import sys

from ultralytics import YOLO
import cv2

from .utils import *
from .rule import Markings, table_from_video_file
from .analytics import start_analytics
from . import config


def main(video_file: str) -> None:
    # Время начала работы
    start_time = time.time()

    # Получение видеофайла
    video = cv2.VideoCapture(video_file)

    # Проверка, открывается ли видео
    if not video.isOpened():
        sys.stdout.write(config.Text.ERROR_OPEN_VIDEO.format(file=video_file))
        return

    # Получение данных видео
    video_fps, video_width, video_height, video_frame_count = get_video_data(video=video)
    display_size = (video_width, video_height)

    # Настройки выходного видео
    video_output_codec = config.Tech.OutputVido.CODEC
    video_output_name = f'{config.Text.VIDEO_OUTPUT_NAME}.{config.Tech.OutputVido.FORMAT}'

    # Инициализация координатов стола и зоны интереса
    table_coordinates = table_from_video_file[video_file]                                           # Координаты зоны стола
    area_interest_coordinates = get_area_interest_coordinates(table_coordinates=table_coordinates)  # Координаты зоны интереса

    # Настройки модели
    frame_skip_multiplicity = config.Tech.Frame.SKIP_MULTIPLICITY  # Кратность, для обработки только кратного кадра
    modal_sensitivity = config.Tech.Modal.SENSITIVITY              # Порог уверенности модели
    modal_iou = config.Tech.Modal.IOU                              # Порог объединения объектов
    modal_frame_resize_modal = config.Tech.Frame.RESIZE_MODAL      # Сжатия изображения, для экономии времени и ресурсов
    model = YOLO(config.Tech.Modal.VERSION)                        # Инициализация модели

    # Кеш
    persons_global = {}  # Посетители
    frames_score = 0     # Счетчик обработанных кадров

    # Получение оборудования для работы (GPU/CPU)
    device_log, device = device_check()

    # Инициализация выходного видео
    fourcc = cv2.VideoWriter_fourcc(*video_output_codec)                                               # Инициализация кодека
    video_output = cv2.VideoWriter(video_output_name, fourcc, video_fps, (video_width, video_height))  # Создание файла

    # Сообщения выводов в консоль
    log_video_start = config.Text.LOG_VIDEO_START
    log_video_process = config.Text.LOG_VIDEO_PROCESS
    log_process_end = config.Text.LOG_END

    title_xslx = config.Text.OutputAnalytics.NAME_XSLX
    title_txt = config.Text.OutputAnalytics.NAME_TXT

    log_video_start = log_video_start.format(
        file=video_file,
        width=video_width,
        height=video_height,
        frames=video_frame_count,
        fps=video_fps
    )

    log_process_end = log_process_end.format(
        file_video=video_output_name,
        file_xlsx=title_xslx,
        file_txt=title_txt
    )

    # Вывод в консоль вводных данных
    sys.stdout.write(device_log)
    sys.stdout.write(f'\n{log_video_start}')

    while True:
        ret, frame = video.read()  # Получение кадра
        frames_score += 1

        if frames_score % frame_skip_multiplicity != 0:  # обработка только каждого n кадра
            continue

        if not ret:  # Проверка, на конец видео
            break

        # Обработка кадра моделью
        results = model.track(
            frame,
            classes=[0],                     # Объекты поиска. 0 - Люди
            conf=modal_sensitivity,          # Порог уверенности модели
            iou=modal_iou,                   # Порог объединения объектов
            imgsz=modal_frame_resize_modal,  # Сжатия изображения, для экономии времени и ресурсов
            device=device,                   # Оборудование
            verbose=False,                   # Использование логов модели
            persist=True                     # Трекинг
        )

        # Получение списка посетителей
        persons = persons_detection(results=results)

        # Сортировка посетителей на тех, кто в зоне интереса и вне ее
        persons_free, persons_involved = persons_sort(
            persons=persons,
            area_interest_coordinates=area_interest_coordinates
        )

        # Обновление данных посетителей
        persons_global = person_data_update(
            frames_score=frames_score,
            persons_global=persons_global,
            persons_free=persons_free,
            persons_involved=persons_involved
        )

        # Обновление данных стола
        table = table_data_update(
            frames_score=frames_score,
            table_coordinates=table_coordinates,
            area_interest_coordinates=area_interest_coordinates,
            persons_global=persons_global
        )

        # Создание сущности Markings
        markings = Markings(table=table, persons=persons_global)

        # Визуализация данных
        frame = screen_layout(
            frame=frame,
            markings=markings,
            frames_score=frames_score,
            display_size=display_size
        )

        # Сохранение кадра
        video_output.write(frame)

        # Подсчет статистики
        progress = (frames_score / video_frame_count * 100)
        time_duration = get_program_process_duration(start_time=start_time)

        # Вывод в консоль прогресса
        sys.stdout.write(f'\r{log_video_process.format(progress=f"{progress:.2f}", time=time_duration)}')
        sys.stdout.flush()

    video.release()          # Закрытие входного видео
    video_output.release()   # Сохранение и закрытие выходного видео

    # Запуск аналитики
    start_analytics(fps=video_fps)

    # Вывод в консоль уведомления, об окончании работы
    sys.stdout.write(f'\n {log_process_end}')
