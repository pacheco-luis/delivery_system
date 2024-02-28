from ..packing.rotation_type import RotationType
from ..utils.decimal import set_to_decimal
from ..utils.intersect import intersect
from ..utils.constants import DEFAULT_DECIMALS


class Bin:
    def __init__(self, width, height, depth, max_weight, n_decimals=DEFAULT_DECIMALS):
        self.width = set_to_decimal(width, n_decimals)
        self.height = set_to_decimal(height, n_decimals)
        self.depth = set_to_decimal(depth, n_decimals)
        self.max_weight = set_to_decimal(max_weight, n_decimals)

        self.items = []
    
    def _put_item(self, item, pivot):
        fit = False
        ip = item.position
        item.position = pivot

        for rt in RotationType.ALL:
            item.rotation_type = rt
            dimension = item._get_dimension()

            if (self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]):
                continue

            fit = True
            
            for item_in_bin in self.items:
                if intersect(item_in_bin, item):
                    fit = False
                    break

            if fit:
                if self._get_total_weight() + item.weight > self.max_weight:
                    fit = False
                    return fit
                
                self.items.append(item)

            if not fit:
                item.position = ip

            return fit

        if not fit:
            item.position = ip

        return fit
    
    def _get_total_weight(self):
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return total_weight
