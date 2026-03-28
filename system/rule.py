from typing import Union, List

from system import config


# Принадлежность координат столиков к видео
table_from_video_file = {
    'video1.mp4': config.VideoTableCoordinates.VIDEO_ONE,
    'video2.mp4': config.VideoTableCoordinates.VIDEO_TWO,
    'video3.mp4': config.VideoTableCoordinates.VIDEO_THREE
}


class Essence:
    name: str        # Название состояния
    color: int       # Цвет
    text_event: str  # Текст события (для аналитики)


class TableStatus:
    # Свободен
    class Free(Essence):
        name = config.Text.StatusName.TABLE_FREE
        color = config.Display.Table.Filling.COLOR_FREE
        text_event = config.Text.Events.TABLE_FREE

    # У столика
    class Busy(Essence):
        name = config.Text.StatusName.TABLE_BUSY
        color = config.Display.Table.Filling.COLOR_BUSY
        text_event = config.Text.Events.TABLE_BUSY


# Варианты состояний посетителя
class PersonStatus:
    # Свободен
    class Free(Essence):
        name = config.Text.StatusName.PERSON_FREE
        color = config.Display.Person.STROKE_COLOR_FREE
        text_event = config.Text.Events.PERSON_FREE

    # У столика
    class Interim(Essence):
        name = config.Text.StatusName.PERSON_INTERIM
        color = config.Display.Person.STROKE_COLOR_INTERIM
        text_event = config.Text.Events.PERSON_INTERIM

    # За столиком
    class Busy(Essence):
        name = config.Text.StatusName.PERSON_BUSY
        color = config.Display.Person.STROKE_COLOR_BUSY
        text_event = config.Text.Events.PERSON_BUSY

    # Отошел от столика
    class Depart(Essence):
        name = config.Text.StatusName.PERSON_DEPART
        color = config.Display.Person.STROKE_COLOR_DEPART
        text_event = config.Text.Events.PERSON_DEPART


class Table:
    def __init__(
        self,
        coordinates: list[list[int, int]],
        area_interest_coordinates: list[list[int, int]],
        status: Union[TableStatus.Free, TableStatus.Busy]
    ):

        # Проверка, является ли статус одним из TableStatus
        if not isinstance(status, (TableStatus.Free, TableStatus.Busy)):
            raise ValueError(config.Text.ERROR_ESSENCE_STATUS)

        # Проверка, является ли координаты списком их 4 координат
        if not isinstance(coordinates, list) or len(coordinates) != 4:
            raise ValueError(config.Text.ERROR_ESSENCE_COORDINATES)

        # Проверка, является ли координата списком из 2 точек
        for point in coordinates:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError(config.Text.ERROR_ESSENCE_COORDINATE)

        self.coordinates = coordinates                              # Координаты самого стола
        self.area_interest_coordinates = area_interest_coordinates  # Координаты зоны интереса
        self.status = status                                        # Статус


class Person:
    def __init__(
        self,
        person_id: int,
        coordinates: list[list[int, int]],
        status: Union[PersonStatus.Free, PersonStatus.Interim, PersonStatus.Busy, PersonStatus.Depart],
        involved_frames: int = 0,
        depart_frames: int = 0,
        invisibility_frames: int = 0
    ):

        # Проверка, является ли статус одним из PersonStatus
        if not isinstance(status, (PersonStatus.Free, PersonStatus.Interim, PersonStatus.Busy, PersonStatus.Depart)):
            raise ValueError(config.Text.ERROR_ESSENCE_STATUS)

        # Проверка, является ли координаты списком их 4 координат
        if not isinstance(coordinates, list) or len(coordinates) != 4:
            raise ValueError(config.Text.ERROR_ESSENCE_COORDINATES)

        # Проверка, является ли координата списком из 2 точек
        for point in coordinates:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError(config.Text.ERROR_ESSENCE_COORDINATE)

        self.person_id = person_id                      # Идентификатор
        self.coordinates = coordinates                  # Координаты
        self.status = status                            # Статус
        self.involved_frames = involved_frames          # Кол-во кадров "За столиком"
        self.depart_frames = depart_frames              # Кол-во кадров "Отошел от столика"
        self.invisibility_frames = invisibility_frames  # Кол-во кадров "Отсутствия"


class Markings:
    def __init__(self, table: Table, persons: List[Person]):
        self.table = table      # Сущность стола
        self.persons = persons  # Список сущностей посетителей
