import numpy as np

from .ant import Ant
from .edge import Edge


class ACO:
    def __init__(self, vrp, packer, n_ants=5, max_iter=1,
                 alpha=1.0, beta=3.0, rho=0.1,
                 pheromone=1.0, phe_deposit_weight=1.0,
                 elitist_weight=1.0, minFactor=0.001):
        self.vrp = vrp
        self.packer = packer
        self.n_ants = n_ants
        self.max_iter = max_iter
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.pheromone = pheromone
        self.phe_deposit_weight = phe_deposit_weight
        self.elitist_weight = elitist_weight
        self.minFactor = minFactor

        self.edges = np.empty((self.vrp.n_customers, self.vrp.n_customers), dtype=object)

        if self.vrp.distance is None:
            heuristic = np.linalg.norm(
                self.vrp.coordinates[:, None] - self.vrp.coordinates, axis=-1
            )

            # Populate self.edges based on the heuristic
            for x, y in np.ndindex(heuristic.shape):
                self.edges[x, y] = self.edges[y, x] = Edge(x, y, heuristic[x, y], self.pheromone)
        else:
            # Populate self.edges based on the provided distance matrix
            for x, y in np.ndindex(self.edges.shape):
                self.edges[x, y] = self.edges[y, x] = Edge(x, y, self.vrp.distance[x][y], self.pheromone)

        self.ants = np.array([Ant(self.alpha, self.beta, self.vrp.n_customers, self.edges, self.packer)
                              for _ in range(self.n_ants)])

        self.best_tour = None
        self.best_distance = np.inf

    def ACS(self):
        print("ACS")
        for iter in range(self.max_iter):
            self._find_tours()
            self._evaporate_pheromone()
            self._apply_local_search()
            print(f"Iteration {iter + 1}: Best distance = {self.best_distance}")
        return self.best_tour, self.best_distance
    
    def ELITIST(self):
        for iter in range(self.max_iter):
            self._find_tours()
            self._add_pheromone(self.best_tour, self.best_distance, heuristic=self.elitist_weight)
            self._evaporate_pheromone()
            self._apply_local_search()
            print(f"Iteration {iter + 1}: Best distance = {self.best_distance}")
        return self.best_tour, self.best_distance

    def MAX_MIN(self):
        for iter in range(self.max_iter):
            self._find_tours()
            self._evaporate_pheromone(max_min=True)
            self._apply_local_search()
            print(f"Iteration {iter + 1}: Best distance = {self.best_distance}")
        return self.best_tour, self.best_distance

    def _find_tours(self):
        print("Finding tours")
        for ant in self.ants:
            self._add_pheromone(ant._update_tour(), ant._calculate_distance())
            if ant.distance < self.best_distance:
                self.best_tour = ant.tour
                self.best_distance = ant.distance
    
    def _add_pheromone(self, tour, distance, heuristic=None):
        print("Adding pheromone")
        pheromone_to_add = self.phe_deposit_weight / distance
        for i in range(len(tour)):
            if heuristic is not None:
                self.edges[tour[i]][tour[(i+1)%len(tour)]].pheromone += heuristic
            else:
                self.edges[tour[i]][tour[(i+1)%len(tour)]].pheromone += pheromone_to_add
    
    def _evaporate_pheromone(self, max_min=False):
        print("Evaporating pheromone")
        for x in range(self.vrp.n_customers):
            for y in range(self.vrp.n_customers):
                self.edges[x][y].pheromone *= (1 - self.rho)
                if max_min:
                    max_pheromone = self.phe_deposit_weight / self.best_distance
                    min_pheromone = max_pheromone * self.minFactor
                    if self.edges[x][y].pheromone > max_pheromone:
                        self.edges[x][y].pheromone = max_pheromone
                    elif self.edges[x][y].pheromone < min_pheromone:
                        self.edges[x][y].pheromone = min_pheromone

    def _apply_local_search(self):
        print("Applying local search")
        for ant in self.ants:
            ant.tour = self._two_opt(ant.tour)
            ant.distance = ant._calculate_distance()
            if ant.distance < self.best_distance:
                self.best_tour = ant.tour
                self.best_distance = ant.distance

    def _two_opt(self, tour):
        print("Two opt")
        best = []
        tour_starts = [i for i, node in enumerate(tour) if node == 0]
        routes = [tour[tour_starts[i]:tour_starts[i+1]
                 if i+1 < len(tour_starts) else None]
                 for i in range(len(tour_starts))]

        for route in routes:
            improved = True
            while improved:
                improved = False
                for i in range(len(route)):
                    for j in range(i+1, len(route)):
                        edge1 = self.edges[route[i]][route[i+1]]
                        edge2 = self.edges[route[j]][route[(j+1)%len(route)]]

                        new_edge1 = self.edges[route[i]][route[j]]
                        new_edge2 = self.edges[route[i+1]][route[(j+1)%len(route)]]

                        cur_distance = edge1.heuristic + edge2.heuristic
                        new_distance = new_edge1.heuristic + new_edge2.heuristic

                        if new_distance < cur_distance:
                            route = route[:i+1] + route[j:i:-1] + route[j+1:]
                            improved = True

            best += route

        return best
