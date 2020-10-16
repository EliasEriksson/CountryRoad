from Map.map import Map, Tile
from .Map.dijkstra import Dijkstra

from pathlib import Path


class Road(Tile):
    def __init__(self, pos, *exits):
        super(Road, self).__init__(pos)
        self._exits = [*exits]

    def find(self, destination: Tile):
        return Dijkstra.find(self, destination)

    @classmethod
    def load(cls, x, y, exits, **_):
        cls((x, y), *((ex["x"], ex["y"]) for ex in exits))

    @property
    def exits(self):
        return [self.map.tiles[coordinate] for coordinate in self._exits]

    def save(self):
        return {
            "class": self.__class__.__name__,
            "x": self.x,
            "y": self.y,
            "exits": [(x, y) for x, y in self._exits]
        }


if __name__ == '__main__':
    m = Map()
    p = Path("testing.json")
    m.load(p)
    m.save(Path("temp.json"))
