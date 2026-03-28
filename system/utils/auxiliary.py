import numpy
import cv2

from system.rule import Person, PersonStatus
from system import config


# Проверка на пересечение зоны интереса и посетителя
def person_over_table(person_bbox: list[list[int, int]], area_interest_coordinates: list[list[int, int]]) -> bool:
    # Перевод координат в матричный тип
    rect = numpy.array(person_bbox, numpy.int32)
    area_interest_coordinates = numpy.array(area_interest_coordinates, numpy.int32)

    # Нормализация данных для расчета
    rect = rect.reshape((-1, 1, 2))
    poly = area_interest_coordinates.reshape((-1, 1, 2))

    # Получение процента пересечения
    inter = cv2.intersectConvexConvex(poly.astype(numpy.float32), rect.astype(numpy.float32))[0]

    # Возвращение результата (True, если пересечение есть больше 0%)
    return inter > 0


# Обновление отсутствующих посетителей
def person_data_update_invisibility(
    persons_global: dict[int, Person],
    persons_global_new: dict[int, Person],
    persons_visibility_id: dict[int, list[list[int, int]]]
) -> None:

    # Лимит кадров отсутствия, после которого идет очистка из кеша.
    invisibility_limit = config.Tech.Person.INVISIBILITY_FRAMES_LIMIT

    for person_id, person in persons_global.items():  # Для каждого посетителя
        if person_id in persons_visibility_id:        # Если есть в списке найденных в кадре
            continue                                  # Ничего не происходит, переход к следующему посетителю

        if person.invisibility_frames < invisibility_limit:         # Если кадров отсутствия меньше порога
            person_new = Person(                                    # Создание сущности
                person_id=person_id,                                # Идентификатор
                coordinates=person.coordinates,                     # Координаты
                status=person.status,                               # Статус
                involved_frames=person.involved_frames,             # Кол-во кадров "За столиком"
                depart_frames=person.depart_frames,                 # Кол-во кадров "Отошел от столика"
                invisibility_frames=person.invisibility_frames + 1  # Кол-во кадров "Отсутствия" + 1
            )

            # Добавление сущности
            persons_global_new[person_id] = person_new


# Обновление свободных посетителей
def person_data_update_free(
        persons_global: dict[int, Person],
        persons_global_new: dict[int, Person],
        persons_free: dict[int, list[list[int, int]]]
) -> None:

    # Пороги изменения статуса
    time_lock = config.Tech.AreaInterest.TIME_LOCK      # Кадров для занятия столика
    time_unlock = config.Tech.AreaInterest.TIME_UNLOCK  # Кадров для освобождения столика

    for person_id, coordinates in persons_free.items():                  # Для каждого посетителя
        if person_id in persons_global:                                  # Если есть в кеше
            involved_frames = persons_global[person_id].involved_frames  # Кол-во кадров "За столиком"
            depart_frames = persons_global[person_id].depart_frames      # Кол-во кадров "Отошел от столика"

            # Если кол-во кадров "За столиком" больше порога занятости, а кол-во кадров "Отошел от столика" меньше порога освобождения
            if time_lock <= involved_frames and depart_frames <= time_unlock:
                person = Person(                      # Создание сущности
                    person_id=person_id,              # Идентификатор
                    coordinates=coordinates,          # Координаты
                    status=PersonStatus.Depart(),     # Статус. Отошел от столика
                    involved_frames=involved_frames,  # Кол-во кадров "За столиком"
                    depart_frames=depart_frames + 1,  # Кол-во кадров "Отошел от столика" + 1
                )

                persons_global_new[person_id] = person  # Добавление сущности
                continue                                # Следующий посетитель

        # Если прошлые условия не прошли, посетитель свободный
        person = Person(                # Создание сущности
            person_id=person_id,        # Идентификатор
            coordinates=coordinates,    # Координаты
            status=PersonStatus.Free()  # Статус. Отошел от столика
        )

        # Добавление сущности
        persons_global_new[person_id] = person


# Обновление посетителей в зоне интереса
def person_data_update_involved(
        persons_global: dict[int, Person],
        persons_global_new: dict[int, Person],
        persons_involved: dict[int, list[list[int, int]]]
) -> None:

    # Кадров для занятия столика
    time_lock = config.Tech.AreaInterest.TIME_LOCK

    for person_id, coordinates in persons_involved.items():  # Для каждого посетителя
        status = PersonStatus.Interim()                      # Статус по умолчанию "У столика"

        if person_id in persons_global:                                  # Если посетитель в кеше
            involved_frames = persons_global[person_id].involved_frames  # Кол-во кадров "За столиком"

            # Если кол-во кадров "За столиком" больше порога занятости (-1)
            if involved_frames >= time_lock-1:  # -1, так как следом будет 60 frames и он будет помечен как занятый
                status = PersonStatus.Busy()    # Статус "У столика"

            person = Person(                          # Создание сущности
                person_id=person_id,                  # Идентификатор
                coordinates=coordinates,              # Координаты
                status=status,                        # Статус. Отошел от столика
                involved_frames=involved_frames + 1,  # Кол-во кадров "За столиком" + 1
            )

            persons_global_new[person_id] = person  # Добавление сущности
            continue                                # Следующий посетитель

        # Если прошлые условия не прошли, посетитель только занят столик
        person = Person(      # Создание сущности
            person_id=person_id,       # Идентификатор
            coordinates=coordinates,   # Координаты
            status=status,             # Статус. "У столика"
            involved_frames=1          # Кол-во кадров "За столиком". 1, так как только занял столик
        )

        # Добавление сущности
        persons_global_new[person_id] = person
