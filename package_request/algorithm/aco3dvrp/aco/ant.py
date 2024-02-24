import numpy as np


class Ant:
    def __init__(self, alpha, beta, n_nodes, edges, packer):
        self.alpha = alpha
        self.beta = beta
        self.n_nodes = n_nodes
        self.edges = edges
        self.packer = packer

        self.tour = None
        self.distance = 0.0
    
    def _update_tour(self):
        print("update tour")
        self.tour = [0]
        visited_nodes = {0}

        while len(visited_nodes) < self.n_nodes:
            next_node = self._select_next_node(visited_nodes)

            if not self.packer._add_item(next_node):
                self.tour.append(0)
                self.packer._reset_bin()
            else:
                self.tour.append(next_node)
                visited_nodes.add(next_node)

        return self.tour
    
    def _select_next_node(self, visited_nodes):
        print("select next node")
        roulette_wheel = 0
        states = [node for node in range(self.n_nodes) if node not in visited_nodes]
        heuristic_value = 0

        for new_state in states:
            heuristic_value += self.edges[self.tour[-1]][new_state].heuristic
        for new_state in states:
            edge = self.edges[self.tour[-1]][new_state]
            A = edge.pheromone ** self.alpha
            B = (heuristic_value / edge.heuristic) ** self.beta if edge.heuristic != 0 else 1e-10
            roulette_wheel += A * B
        random_value = np.random.uniform(0, roulette_wheel)
        wheel_position = 0
        for new_state in states:
            edge = self.edges[self.tour[-1]][new_state]
            A = edge.pheromone ** self.alpha
            B = (heuristic_value / edge.heuristic) ** self.beta if edge.heuristic != 0 else 1e-10
            wheel_position += A * B
            if wheel_position >= random_value:
                return new_state
        return states[-1]
    
    def _calculate_distance(self):
        print("calculate distance")
        self.distance = 0.0
        for i in range(len(self.tour)):
            self.distance += self.edges[self.tour[i]][self.tour[(i+1)%len(self.tour)]].heuristic
        return self.distance
