from typing import *
from pathlib import Path
import json


class Map:
    class _Points(type):
        classes: Dict[str, Type["Map.Point"]] = {}

        def __new__(mcs, name, base, *args):
            cls = super(mcs, mcs).__new__(mcs, name, base, *args)
            if base:
                mcs.classes.update({name: cls})
            return cls

    class _Objects(type):
        classes: Dict[str, Type["Map.Object"]] = {}

        def __new__(mcs, name, base, *args):
            cls = super(mcs, mcs).__new__(mcs, name, base, *args)
            if base:
                mcs.classes.update({name: cls})
            return cls

    class Point(metaclass=_Points):
        map: Optional["Map"] = None

        def __init__(self, pos: Tuple[float, float], *_, **__):
            self.pos = pos

        @property
        def x(self) -> float:
            return self.pos[0]

        @property
        def y(self) -> float:
            return self.pos[1]

        def add_map_instance(self, map_instance: "Map") -> "Map.Point":
            self.map = map_instance
            return self

        @property
        def json(self):
            json_representation = {
                attr.strip("_"): getattr(self, attr)
                for attr in set(dir(self)).difference(dir(self.__class__))
            }
            json_representation.update({
                "class": self.__class__.__name__
            })
            return json_representation

        @classmethod
        def load(cls, tile: Dict[str, Any]):
            raise NotImplementedError()

        def __hash__(self):
            return hash(self.pos)

        def __repr__(self):
            return f"{self.__class__.__name__}(pos={self.pos})"

    class Object(metaclass=_Objects):
        map: Optional["Map"] = None

        def __init__(self, pos: Tuple[float, float]):
            self.pos = pos

        @property
        def x(self) -> float:
            return self.pos[0]

        @property
        def y(self) -> float:
            return self.pos[1]

        def add_map_instance(self, map_instance: "Map") -> "Map.Object":
            self.map = map_instance
            return self

        @property
        def json(self):
            json_representation = {
                (attr.strip("_")): (
                    getattr(self, attr).pos
                    if hasattr(getattr(self, attr), "json") else
                    getattr(self, attr)
                )
                for attr in set(dir(self)).difference((dir(self.__class__)))
            }
            json_representation.update({
                "class": self.__class__.__name__
            })
            return json_representation

        @classmethod
        def load(cls, map_instance: "Map", obj: Dict[str, Any]):
            raise NotImplementedError()

        def __hash__(self):
            return hash(self.pos)

        def __repr__(self):
            return f"{self.__class__.__name__}(pos={self.pos})"

    def __init__(self):
        self.tiles: Dict[Tuple[float, float], "Map.Point"] = {}
        self.objects: Dict[Tuple[float, float], "Map.Object"] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def load(cls, path: Path):
        with path.open("r") as f:
            map_data = json.load(f)

        instance = cls()

        for tile in map_data["tiles"]:
            try:
                if (tile_class_name := tile.pop("class")) in cls._Points.classes:
                    instance.add_tile(cls._Points.classes[tile_class_name].load(tile))
            except KeyError:
                pass

        for obj in map_data["objects"]:
            try:
                if (object_class_name := obj.pop("class")) in cls._Objects.classes:
                    instance.add_object(cls._Objects.classes[object_class_name].load(instance, obj))
            except KeyError:
                pass

        return instance

    def save(self, path: Path):
        map_content = {
            "tiles": [tile.json for tile in self.tiles.values()],
            "objects": [obj.json for obj in self.objects.values()]
        }

        with path.open("w") as f:
            json.dump(map_content, f, indent=True)

    def add_tile(self, tile: Point):
        self.tiles.update({
            tile.pos: tile.add_map_instance(self)
        })

    def add_object(self, obj: Object):
        self.objects.update({
            obj.pos: obj.add_map_instance(self)
        })


class Road(Map.Point):
    def __init__(self, pos, *exits: Tuple[float, float]):
        super(Road, self).__init__(pos)
        self._exits = [*exits]

    @property
    def exits(self):
        return [self.map.tiles[exit_] for exit_ in self._exits]

    @classmethod
    def load(cls, tile: dict) -> "Road":
        return cls(tuple(tile["pos"]), *(tuple(e) for e in tile["exits"]))


class Car(Map.Object):
    def __init__(self, spawn: Map.Point, width: float):
        super(Car, self).__init__(spawn.pos)
        self.spawn = spawn
        self.width = width

    @classmethod
    def load(cls, map_instance: Map, obj: dict):
        return cls(map_instance.tiles[obj["pos"]], obj["width"])


def generate_3x3(filepath: Path):
    _m = Map()
    roads = [
        Road((0, 0), (0, 1), (1, 0)),
        Road((0, 1), (0, 0), (0, 2), (1, 1)),
        Road((0, 2), (0, 1), (1, 2)),

        Road((1, 0), (0, 0), (1, 1), (2, 0)),
        Road((1, 1), (0, 1), (1, 0), (1, 2), (2, 1)),
        Road((1, 2), (0, 2), (1, 1), (2, 2)),

        Road((2, 0), (1, 0), (2, 1)),
        Road((2, 1), (1, 1), (2, 0), (2, 2)),
        Road((2, 2), (1, 2), (2, 1))
    ]

    for road in roads:
        _m.add_tile(road)
        car = Car(road, 0.05)
        _m.add_object(car)

    _m.save(filepath)


p = Path("testing.json")

generate_3x3(p)

# m = Map.load(p)

# print(m.tiles)
