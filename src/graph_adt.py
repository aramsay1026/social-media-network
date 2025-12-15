# Worked on by: Amy Ramsay

from linked_adts import LinkedQueue

class Vertex:
    # Runtime:
    # add_neighbor: O(1) average
    # get_connections: O(1)
    # get_weight: O(1) average

    def __init__(self, key):
        self.id = key
        self.connected_to = {}  # neighbor Vertex -> weight

    def add_neighbor(self, nbr, weight=0):
        self.connected_to[nbr] = weight

    def get_connections(self):
        return self.connected_to.keys()

    def get_id(self):
        return self.id

    def get_weight(self, nbr):
        return self.connected_to.get(nbr, None)


class UndirectedGraph:
    # Runtime notes:
    # add_vertex: O(1) average
    # add_edge: O(1) average
    # bfs: O(V + E)
    # dfs: O(V + E)

    def __init__(self):
        self.vert_list = {}   # key -> Vertex
        self.num_vertices = 0

    def add_vertex(self, key):
        if key not in self.vert_list:
            self.num_vertices += 1
            self.vert_list[key] = Vertex(key)
        return self.vert_list[key]

    def get_vertex(self, key):
        return self.vert_list.get(key, None)

    def add_edge(self, from_key, to_key, weight=0):
        # undirected: add both directions
        if from_key not in self.vert_list:
            self.add_vertex(from_key)
        if to_key not in self.vert_list:
            self.add_vertex(to_key)

        v1 = self.vert_list[from_key]
        v2 = self.vert_list[to_key]
        v1.add_neighbor(v2, weight)
        v2.add_neighbor(v1, weight)

    def get_vertices(self):
        return list(self.vert_list.keys())

    def contains(self, key):
        return key in self.vert_list

    def clear(self):
        self.vert_list = {}
        self.num_vertices = 0

    def is_empty(self):
        return self.num_vertices == 0

    def size(self):
        return self.num_vertices

    def get_edges(self):
        # returns a list of tuples (from, to, weight) without duplicates
        edges = []
        seen = set()
        for from_key, vertex in self.vert_list.items():
            for nbr in vertex.get_connections():
                to_key = nbr.get_id()
                pair = tuple(sorted([from_key, to_key]))
                if pair not in seen:
                    seen.add(pair)
                    edges.append((from_key, to_key, vertex.get_weight(nbr)))
        return edges

    def bfs(self, start):
        # Uses LinkedQueue (required)
        if start not in self.vert_list:
            return []

        visited = set()
        order = []

        q = LinkedQueue()
        q.enqueue(start)
        visited.add(start)

        while not q.is_empty():
            current_key = q.dequeue()
            order.append(current_key)

            current_vertex = self.vert_list[current_key]
            for nbr in current_vertex.get_connections():
                nbr_key = nbr.get_id()
                if nbr_key not in visited:
                    visited.add(nbr_key)
                    q.enqueue(nbr_key)

        return order

    def dfs(self, start):
        # iterative DFS to keep it simple
        if start not in self.vert_list:
            return []

        visited = set()
        order = []
        stack = [start]

        while stack:
            current_key = stack.pop()
            if current_key in visited:
                continue
            visited.add(current_key)
            order.append(current_key)

            current_vertex = self.vert_list[current_key]
            # push neighbors (reversed for more stable output ordering)
            neighbors = [nbr.get_id() for nbr in current_vertex.get_connections()]
            neighbors.sort(reverse=True)
            for nbr_key in neighbors:
                if nbr_key not in visited:
                    stack.append(nbr_key)

        return order
