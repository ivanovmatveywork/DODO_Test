# Группы констант собраны в классы для удобства и читаемости импорта


# ------------------------------------------
# КООРДИНАТЫ СТОЛИКА #######################

class VideoTableCoordinates:
    # ВИДЕО 1
    VIDEO_ONE = [
        [1721, 841],
        [2134, 1051],
        [1799, 1437],
        [893, 1437]
    ]

    # ВИДЕО 2
    VIDEO_TWO = [
        [518, 523],
        [1118, 695],
        [994, 1079],
        [339, 840]
    ]

    # ВИДЕО 3
    VIDEO_THREE = [
        [263, 126],
        [588, 297],
        [437, 932],
        [41, 818]
    ]


# ------------------------------------------
# ТЕХНИЧЕСКАЯ ЧАСТЬ ########################

class Tech:
    # МОДЕЛЬ
    class Modal:
        VERSION = 'yolov8x.pt'  # Сильная модель, уменьшает кол-во ошибок распознавания
        SENSITIVITY = 0.6       # Порог уверенности модели
        IOU = 0.2               # Порог объединения объектов

    # КАДРЫ
    class Frame:
        SKIP_MULTIPLICITY = 2  # Обрабатывать только каждый n кадр. Нельзя вводить 0
        RESIZE_MODAL = 736     # Изменение размера кадра для модели. Должно быть кратно 32

    # ЗОНА ИНТЕРЕСА
    class AreaInterest:
        SIZE = 60         # Размер области (отступ)
        TIME_LOCK = 60    # Количество кадров нахождения посетителя внутри перед "закрытием" столик
        TIME_UNLOCK = 60  # Количество кадров нахождения посетителя вне перед "открытием" столик

    class Person:
        INVISIBILITY_FRAMES_LIMIT = 120  # Количество кадров, когда не видно посетителя, перед удалением из кеша

    class OutputVido:
        CODEC = 'mp4v'  # Кодек видео. Лучше не трогать
        FORMAT = 'mp4'  # Формат видео. Лучше не трогать


# ------------------------------------------
# ОТОБРАЖЕНИЯ ##############################


class Display:
    class Text:
        class States:
            SCALE = 0.5              # Масштаб
            THICKNESS = 2            # Толщина
            COLOR = (0, 0, 0)        # Черный
            PADDING = 24             # Промежуток между текстами

        class Frames:
            SCALE = 2                # Масштаб
            THICKNESS = 6            # Толщина
            COLOR = (255, 255, 255)  # Белый
            PADDING = 40             # Отступ от краев кадра

    # СТОЛ. ОБВОДКА
    class Table:
        class Stroke:
            THICKNESS = 2            # Толщина
            COLOR = (255, 0, 0)      # Синий, так как нейтральный

        class Filling:
            ALPHA = 0.25              # Процент прозрачности
            COLOR_FREE = (0, 255, 0)  # Зеленый. Столик свободен
            COLOR_BUSY = (0, 0, 255)  # Красный. Столик занят

    # ЗОНА ИНТЕРЕСА. ОБВОДКА
    class AreaInterest:
        STROKE_THICKNESS = 1          # Толщина
        STROKE_COLOR = (255, 0, 255)  # Фиолетовый, для отличия

    # ПОСЕТИТЕЛЬ. ОБВОДКА
    class Person:
        STROKE_THICKNESS = 4                  # Толщина
        STROKE_COLOR_FREE = (0, 255, 0)       # Зеленый. Не (у/за) столик(а/ом)
        STROKE_COLOR_INTERIM = (0, 255, 255)  # Желтый. У столика
        STROKE_COLOR_BUSY = (0, 0, 255)       # Красный. За столиком
        STROKE_COLOR_DEPART = (255, 0, 0)     # Синий. Отошел от "своего" столика


# ------------------------------------------
# СООББЩЕНИЯ ###############################


class Text:  # Для читаемости импорта
    class Display:  # ВАЖНО! Только английский, ибо OpenCV не поддерживает русский язык
        PERSON_ID = 'ID: {value}'                             # Идентификатор
        STATUS = 'Status: {value}'                            # Статус
        INVOLVED_FRAMES = 'Involved frames: {value}'          # Кол-во кадров "За столиком"
        DEPART_FRAMES = 'Depart frames: {value}'              # Кол-во кадров "Отошел от столика"
        FRAME = 'Frame: {value}'                              # Номер кадра

    class StatusName:  # ВАЖНО! Только английский, ибо OpenCV не поддерживает русский язык
        TABLE_FREE = 'FREE'         # Столик свободен
        TABLE_BUSY = 'BUSY'         # Столик занят
        PERSON_FREE = 'FREE'        # Посетитель не (у/за) столик(а/ом)
        PERSON_INTERIM = 'INTERIM'  # Посетитель у столика
        PERSON_BUSY = 'BUSY'        # Посетитель за столиком
        PERSON_DEPART = 'DEPART'    # Посетитель отошел от "своего" столика

    class Events:
        TABLE_FREE = 'Столик освободили'
        TABLE_BUSY = 'Столик заняли'
        PERSON_FREE = 'Посетитель не за столиком'
        PERSON_INTERIM = 'Посетитель подошел к столику'
        PERSON_DEPART = 'Посетитель отошел от столика'
        PERSON_BUSY = 'Посетитель за столиком'

    class EssenceType:
        TABLE = 'Table'
        PERSON = 'Person'

    class OutputAnalytics:
        NAME_XSLX = 'analytics.xlsx'
        NAME_TXT = 'analytics.txt'

    class AnalyticsXLSXColumn:
        METRIC = 'Метрика'
        VALUE = 'Значение'

    VIDEO_OUTPUT_NAME = 'output'
    ANALYTICS_TITLE = 'Аналитика'
    TABLE_AVERAGE_TIME_FREE = 'Среднее время простоя столика (промежуток между посетителями)'

    LOG_TITLE = 'ИНФО:'
    ERROR_TITLE = 'ОШИБКА:'

    LOG_DEVICE_US_CPU = '{LOG_TITLE} CUDA и Torch не обнаружены. Будет использовано CPU'.format(LOG_TITLE=LOG_TITLE)
    LOG_DEVICE_US_GPU = '{LOG_TITLE} CUDA и Torch обнаружены. Будет использовано GPU'.format(LOG_TITLE=LOG_TITLE)

    LOG_VIDEO_START = '{LOG_TITLE} Видео: \n   Файл: {{file}} \n   Разрешение: {{width}}x{{height}} \n   Кадров: {{frames}} \n   FPS: {{fps}}'.format(LOG_TITLE=LOG_TITLE)
    LOG_VIDEO_PROCESS = 'Прогресс: {progress}%  Длительность: {time}'
    LOG_END = '{LOG_TITLE} Обработка завершена. Созданы файлы {{file_video}}, {{file_xlsx}}, {{file_video}}'.format(LOG_TITLE=LOG_TITLE)

    ERROR_OPEN_VIDEO = '{ERROR_TITLE} Не удалось открыть видео {{file}}'.format(ERROR_TITLE=ERROR_TITLE)

    ERROR_ESSENCE_STATUS = '{ERROR_TITLE} Статус должен быть из [Essence]Status.[Status]'.format(ERROR_TITLE=ERROR_TITLE)
    ERROR_ESSENCE_COORDINATES = '{ERROR_TITLE} Координаты должны быть списком из 4 координат [x, y]'.format(ERROR_TITLE=ERROR_TITLE)
    ERROR_ESSENCE_COORDINATE = '{ERROR_TITLE} Каждая координата должна быть списком из 2 точек [x, y]'.format(ERROR_TITLE=ERROR_TITLE)
