import numpy as np


class VRP:
    def __init__(self, coordinates, distance=None):
        self.coordinates = np.array(coordinates)
        self.n_customers = len(self.coordinates)
        self.distance = distance
