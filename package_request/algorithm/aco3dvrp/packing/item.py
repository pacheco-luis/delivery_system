from .rotation_type import RotationType
from ..utils.decimal import set_to_decimal
from ..utils.constants import START_POSITION, DEFAULT_DECIMALS


class Item:
    def __init__(self, width, height, depth, weight, n_decimals=DEFAULT_DECIMALS):
        self.width = set_to_decimal(width, n_decimals)
        self.height = set_to_decimal(height, n_decimals)
        self.depth = set_to_decimal(depth, n_decimals)
        self.weight = set_to_decimal(weight, n_decimals)

        self.rotation_type = RotationType.RT_WHD
        self.position = START_POSITION

    def _get_dimension(self):
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension
