from .bin import Bin
from .item import Item
from .axis import Axis
from ..utils.constants import START_POSITION, DEFAULT_DECIMALS


class Packer:
    def __init__(self, bin_capacity, items, n_decimals=DEFAULT_DECIMALS):
        self.bin = Bin(*bin_capacity, n_decimals)
        self.items = [Item(*item, n_decimals)
                      for item in [[0, 0, 0, 0]] + items]
        
    def _reset_bin(self):
        self.bin.items = []
        
    def _add_item(self, index):
        fit = False

        if self._pack_to_bin(self.items[index]):
            fit = True

        return fit
    
    def _pack_to_bin(self, item):
        fitted = False

        if not self.bin.items:
            response = self.bin._put_item(item, START_POSITION)

            if response:
                fitted = True

            return fitted
        
        for axis in Axis.ALL:
            items_in_bin = self.bin.items

            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib._get_dimension()

                if axis == Axis.WIDTH:
                    pivot = [
                        ib.position[0] + w,
                        ib.position[1],
                        ib.position[2]
                    ]
                elif axis == Axis.HEIGHT:
                    pivot = [
                        ib.position[0],
                        ib.position[1] + h,
                        ib.position[2]
                    ]
                elif axis == Axis.DEPTH:
                    pivot = [
                        ib.position[0],
                        ib.position[1],
                        ib.position[2] + d
                    ]

                if self.bin._put_item(item, pivot):
                    fitted = True
                    break

            if fitted:
                break

        return fitted
