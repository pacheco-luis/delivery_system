from ..packing.axis import Axis


def intersect(item1, item2):
    return (
        rect_intersect(item1, item2, Axis.WIDTH, Axis.HEIGHT) and
        rect_intersect(item1, item2, Axis.HEIGHT, Axis.DEPTH) and
        rect_intersect(item1, item2, Axis.WIDTH, Axis.DEPTH)
    )

def rect_intersect(item1, item2, x, y):
    # Get the dimensions of the items
    d1 = item1._get_dimension()
    d2 = item2._get_dimension()

    # Get the center coordinates of the items
    cx1 = item1.position[x] + d1[x]/2
    cy1 = item1.position[y] + d1[y]/2
    cx2 = item2.position[x] + d2[x]/2
    cy2 = item2.position[y] + d2[y]/2

    # Get the intersection of the items
    # By getting the maximum of the center coordinates
    # and subtracting the minimum of the center coordinates
    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    # If the intersection is less than half of the sum of the dimensions
    # of the items, then the items intersect
    return ix < (d1[x]+d2[x])/2 and iy < (d1[y]+d2[y])/2
