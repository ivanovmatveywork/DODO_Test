import numpy
import cv2

from system import config, rule


# Визуализация данных стола
def table_polygon_display(frame: numpy.ndarray, table: rule.Table) -> numpy.ndarray:
    # Перевод координат в матричный тип
    table_coordinates = numpy.array(table.coordinates, dtype=numpy.int32)
    area_interest_coordinates = numpy.array(table.area_interest_coordinates, dtype=numpy.int32)

    # Настройки отображения заливки стола
    table_fill_color = table.status.color                  # Цвет
    table_fill_alpha = config.Display.Table.Filling.ALPHA  # Прозрачность

    # Настройки отображения обводки стола
    table_stroke_color = config.Display.Table.Stroke.COLOR          # Цвет
    table_stroke_thickness = config.Display.Table.Stroke.THICKNESS  # Толщина

    # Настройки отображения обводки зоны интереса
    area_interest_color = config.Display.AreaInterest.STROKE_COLOR          # Цвет
    area_interest_thickness = config.Display.AreaInterest.STROKE_THICKNESS  # Толщина

    # Заливка стола
    if table_fill_alpha > 0:  # Если значение прозрачности выше 0
        overlay = frame.copy()  # Копия кадра
        cv2.fillPoly(img=overlay, pts=[table_coordinates], color=table_fill_color)  # Заливка на копии кадра
        cv2.addWeighted(src1=overlay, alpha=table_fill_alpha, src2=frame, beta=1 - table_fill_alpha, gamma=0, dst=frame)  # Объединение исходного и скопированного кадра

    # Обводка стола и зонны интереса
    cv2.polylines(img=frame, pts=[table_coordinates], isClosed=True, color=table_stroke_color, thickness=table_stroke_thickness, lineType=cv2.LINE_AA)
    cv2.polylines(img=frame, pts=[area_interest_coordinates], isClosed=True, color=area_interest_color, thickness=area_interest_thickness, lineType=cv2.LINE_AA)

    # Возвращение кадра
    return frame


# Визуализация данных посетителя
def person_polygon_display(frame: numpy.ndarray, person: rule.Person) -> numpy.ndarray:
    # Перевод координат в матричный тип
    person_coordinates = numpy.array(person.coordinates, dtype=numpy.int32)

    # Настройки обводки
    color = person.status.color                         # Цвет
    thickness = config.Display.Person.STROKE_THICKNESS  # Толщина

    # Настройки текста
    text_thickness = config.Display.Text.States.THICKNESS  # Толщина
    text_color = config.Display.Text.States.COLOR          # Цвет
    scale = config.Display.Text.States.SCALE               # Масштабирование
    font = cv2.FONT_HERSHEY_SIMPLEX                        # Шрифт

    # Обводка посетителя
    cv2.polylines(img=frame, pts=[person_coordinates], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)

    # Присваивание координат
    coordinate_x, coordinate_y = person.coordinates[0][0], person.coordinates[0][1]

    # Список текстовой информации
    texts = [
        config.Text.Display.PERSON_ID.format(value=person.person_id),
        config.Text.Display.STATUS.format(value=person.status.name),
        config.Text.Display.INVOLVED_FRAMES.format(value=person.involved_frames),
        config.Text.Display.DEPART_FRAMES.format(value=person.depart_frames),
    ]

    # Инициализация отступов надписей
    padding = 0
    padding_step = config.Display.Text.States.PADDING

    # Для каждого текста
    for text in texts:
        # Прибавление отступа
        padding += padding_step

        # Получение размера текста
        (text_width, text_height), _ = cv2.getTextSize(text=text, fontFace=font, fontScale=scale, thickness=thickness)

        # Расчет необходимой высоты для заливки фона текста
        text_coordinate_y = coordinate_y - padding

        # Расчет точек координат текста
        text_point_one = (coordinate_x, text_coordinate_y - text_height)
        text_point_two = (coordinate_x + text_width, text_coordinate_y)

        # Группирование координатных точек
        text_coordinates = (coordinate_x, text_coordinate_y)

        # Визуализация
        cv2.rectangle(img=frame, pt1=text_point_one, pt2=text_point_two, color=color, thickness=-1)                                          # Заливка фона
        cv2.putText(img=frame, text=text, org=text_coordinates, fontFace=font, fontScale=scale, color=text_color, thickness=text_thickness)  # Написание текста

    # Возвращение кадра
    return frame


# Визуализация номера кадра
def frame_display(frame: numpy.ndarray, frames_score: int, display_size: tuple) -> numpy.ndarray:
    # Настройки отображения
    text = config.Text.Display.FRAME.format(value=frames_score)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = config.Display.Text.Frames.SCALE
    color = config.Display.Text.Frames.COLOR
    thickness = config.Display.Text.Frames.THICKNESS
    padding = config.Display.Text.Frames.PADDING

    # Получение длины текста
    (text_width, _), _ = cv2.getTextSize(text=text, fontFace=font, fontScale=scale, thickness=thickness)

    # Расчет точек координат текста
    coordinate_x = display_size[0] - (padding + text_width)  # Чем длиннее текст, тем левее его стартовая точка
    coordinate_y = display_size[1] - padding

    # Группирование координатных точек
    text_point = (coordinate_x, coordinate_y)

    # Написание текста
    cv2.putText(img=frame, text=text, org=text_point, fontFace=font, fontScale=scale, color=color, thickness=thickness)

    # Возвращение кадра
    return frame
