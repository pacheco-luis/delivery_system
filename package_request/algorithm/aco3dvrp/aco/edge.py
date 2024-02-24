class Edge:
    def __init__(self, a, b, heuristic, pheromone):
        self.a = a
        self.b = b
        self.heuristic = heuristic
        self.pheromone = pheromone
