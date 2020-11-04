from typing import *

if TYPE_CHECKING:
    from .map import Road, Map

from math import sqrt


class Dijkstra:
    class Edge:
        def __init__(self, distance: float, predecessor: Optional[Road]):
            self.distance: float = distance
            self.predecessor: Optional[Map.Point] = predecessor

        def __repr__(self):
            return f"{self.__class__.__name__}({self.distance}, {self.predecessor})"

    @classmethod
    def find(cls, source: Road, goal: Map.Point):
        visited: Dict[Road: cls.Edge] = {source: cls.Edge(0, None)}
        queue: Dict[Road: cls.Edge] = visited.copy()

        while queue and (source_node := min(queue, key=lambda n: queue[n].distance)):
            # noinspection PyUnboundLocalVariable
            for node in source_node.exits:
                if node is goal and goal in visited:
                    break

                if node not in visited:
                    edge = {node: cls.Edge(
                        sqrt((node.x - source_node.x) ** 2 - (node.y - source_node.y)) +
                        visited[source_node].distance,
                        source_node)}
                    visited.update(edge)  # adds a visited node
                    queue.update(edge)  # adds a node to the queue

                elif visited[node].distance < visited[source_node].distance:
                    edge = {node: cls.Edge(
                        sqrt((node.x - source_node.x) ** 2 - (node.y - source_node.y)) +
                        visited[source_node].distance,
                        source_node)}
                    visited.update(edge)
            queue.pop(source_node)

        current = goal
        path = []
        while visited[current].predecessor is not None:
            path.insert(0, current)
            current = visited[current].predecessor
        return path
