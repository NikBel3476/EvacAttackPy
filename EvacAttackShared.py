import math
from operator import itemgetter
from typing import Optional, TypedDict, Literal, TypeAlias, Any


BimElementSign: TypeAlias = Literal[
	'Room', # Указывает, что элемент здания является помещением/комнатой
	'Staircase', # Указывает, что элемент здания является лестницей
	'DoorWay', # Указывает, что элемент здания является проемом (без дверного полотна)
	'DoorWayIn', # Указывает, что элемент здания является дверью, которая соединяет два элемента: ROOM и ROOM или ROOM и STAIR
	'DoorWayOut', # Указывает, что элемент здания является эвакуационным выходом
	'Outside', # Указывает, что элемент является зоной вне здания
    'SZ', # Указывает, что элементы является безопасной зоной
	'Undefined', # Указывает, что тип элемента не определен
]

class Point(TypedDict):
    x: float
    y: float


class Polygon(TypedDict):
    points: list[Point]


class BimJsonElement(TypedDict):
    """ Структура, описывающая элемент """

    Id: str # UUID идентификатор элемента
    Name: str # Название элемента
    XY: list[Polygon] # Полигон элемента
    Output: list[str] # Массив UUID элементов, которые являются соседними к элементу
    # NumberOfPeople: int # Количество людей в элементе
    NumPeople: Optional[float] # Количество людей в элементе
    SizeZ: float # Высота элемента
    ZLevel: Optional[float] # Уровень, на котором находится элемент
    Sign: BimElementSign # Тип элемента


class BimJsonFileData(TypedDict):
    """ Структура, описывающая информацию о файле """

    FormatVersion: int
    CreatingData: str


class BimJsonAddress(TypedDict):
    """ Структура поля, описывающего географическое положение объекта """

    City: str
    StreetAddress: str
    AddInfo: str


class BimJsonLevel(TypedDict):
    """ Структура, описывающая этаж """
    
    NameLevel: str # Название этажа
    BuildElement: list[BimJsonElement] # Массив элементов, которые принадлежат этажу
    ZLevel: float # Высота этажа над нулевой отметкой


class BimJsonObject(TypedDict):
    """ Структура, описывающая здание """

    Address: BimJsonAddress # Информация о местоположении объекта
    NameBuilding: str # Название здания
    Level: list[BimJsonLevel] # Массив уровней здания
    FileData: BimJsonFileData # Информация о файле


def points(el: BimJsonElement):
    if "points" in el["XY"][0]:
        return [(xy["x"], xy["y"]) for xy in el["XY"][0]["points"]]
    else:
        return el["XY"][0][:-1]

def cntr_real(el: BimJsonElement):
    ''' Центр в координатах здания '''
    xy = points(el)
    return sum((x for x, _ in xy)) / len(xy), sum((y for _, y in xy)) / len(xy)

def room_area(el: BimJsonElement):
    # print(xy)
    xy = points(el)
    return math.fabs(0.5*sum((x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(xy, xy[1:]+xy[:1]))))

def is_el_on_lvl(el: BimJsonElement, lvl: BimJsonLevel):
    ''' Принадлежит ли элемент этажу '''
    el_id = el["Id"]
    for e in lvl['BuildElement']:
        if e['Id'] == el_id:
            return True
    return False

def point_in_polygon(point: Point, zone_points: list[Point]):
    """
    Проверка вхождения точки в прямоугольник
    """
    c = False
    for p1, p2 in zip(zone_points, zone_points[1:]+zone_points[:1]):
        if math.dist(p1, point) + math.dist(point, p2) == math.dist(p1, p2):
            return True
        if (((p1[1] > point[1]) != (p2[1] > point[1])) and (point[0] < (p2[0]-p1[0]) * (point[1]-p1[1]) / (p2[1]-p1[1]) + p1[0])):
            c = not c
    return c

def dict_peak(d: list[Any], key: str, reverse: bool):
    ''' Возвращает крайние элементы словаря d по ключу key,
    это минимальные элементы если reverse == False, иначе максимальные '''
    d = sorted(d, key=itemgetter(key), reverse=reverse)
    return [i for i in d if i[key] == d[0][key]]
