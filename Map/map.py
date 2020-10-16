from typing import *
from pathlib import Path
import json

from .dijkstra import Dijkstra


class Map:
    _instance = None

    class Map:
        class Tiles(type):
            """
            metaclass for a tile.
            This metaclass keeps track on all child class names and couples them with their class

            this is done to easily instantiate a class from a json object
            """
            classes: Dict[str, Type["Tile"]] = {}

            def __new__(mcs, name, base, *args):
                cls = super(mcs, mcs).__new__(mcs, name, base, *args)
                if base:
                    mcs.classes.update({name: cls})
                return cls

        class Objects(type):
            """
            metaclass for an object.
            This metaclass keeps track on all child class names and couples them with their class

            this is done to easily instantiate a class from a json object
            """
            classes: Dict[str, Type["Object"]] = {}

            def __new__(mcs, name, base, *args):
                cls = super(mcs, mcs).__new__(mcs, name, base, *args)
                if base:
                    mcs.classes.update({name: cls})
                return cls

        def __init__(self):
            self.tiles: Dict[Tuple[int, int], Tile] = {}
            self.objects: Dict[Tuple[int, int], Object] = {}

        def load(self, path: Path):
            with path.open("r") as f:
                save = json.load(f)

            for tile in save["tiles"]:
                if tile["class"] in self.Tiles.classes:
                    self.Tiles.classes[tile["class"]].load(**tile)

        def save(self, path: Path):
            tiles = []
            objects = []
            save = {"tiles": tiles, "objects": objects}
            for tile in self.tiles.values():
                tiles.append(tile.save())
            with path.open("w") as f:
                json.dump(save, f, indent=True)

    Tiles = Map.Tiles
    Objects = Map.Objects

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls.Map)
            cls._instance.__init__()
        return cls._instance


class Tile(metaclass=Map.Tiles):
    map = Map()

    def __init__(self, pos: Tuple[int, int]):
        self.pos = pos
        self.map.tiles[pos] = self

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def __hash__(self):
        return hash(self.pos)

    def load(self, *_, **kwargs):
        raise NotImplementedError()

    def save(self, *_, **__):
        raise NotImplementedError()


class Object(metaclass=Map.Objects):
    map = Map()

