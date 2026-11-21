"""Clip a sampled terrain at exact model coordinates, preserving its triangles."""

from bisect import bisect_left, bisect_right
from decimal import Decimal
from sys import float_info


def division_positions(length, parts):
    """Calculate cuts from the requested dimensions, independently of the grid."""
    size = Decimal(str(length))
    return [float(size * i / parts) for i in range(parts + 1)]


class ClippedTerrain:
    """Clipped surface triangles and their counterclockwise boundary polylines."""

    def __init__(self, bounds):
        self.bounds = bounds
        self.triangles = []
        self.boundaries = [{}, {}, {}, {}]  # Bottom, right, top, left.

    def add_boundary_point(self, point):
        x_min, y_min, x_max, y_max = self.bounds
        if point.y == y_min:
            self.boundaries[0][point.x] = point
        if point.x == x_max:
            self.boundaries[1][point.y] = point
        if point.y == y_max:
            self.boundaries[2][point.x] = point
        if point.x == x_min:
            self.boundaries[3][point.y] = point

    def edges(self):
        return [
            [points[key] for key in sorted(points, reverse=i >= 2)]
            for i, points in enumerate(self.boundaries)
        ]


def clip_grid(matrix, x_min, y_min, x_max, y_max):
    """Crop the intersecting cells, then clip at the exact rectangle if needed."""
    xs = [point.x for point in matrix[0]]
    ys = [-row[0].y for row in matrix]
    col0 = max(0, bisect_right(xs, x_min) - 1)
    col1 = min(len(xs) - 1, bisect_left(xs, x_max))
    row0 = max(0, bisect_right(ys, -y_max) - 1)
    row1 = min(len(ys) - 1, bisect_left(ys, -y_min))
    cropped = [row[col0:col1 + 1] for row in matrix[row0:row1 + 1]]
    if (cropped[0][0].x == x_min and cropped[-1][-1].x == x_max
            and cropped[0][0].y == y_max and cropped[-1][-1].y == y_min):
        return cropped

    tile = ClippedTerrain((x_min, y_min, x_max, y_max))
    for j in range(len(cropped) - 1):
        for k in range(len(cropped[0]) - 1):
            p1, p2 = cropped[j + 1][k], cropped[j][k + 1]
            p3, p4 = cropped[j][k], cropped[j + 1][k + 1]
            if (x_min <= p1.x and p2.x <= x_max
                    and y_min <= p1.y and p2.y <= y_max):
                faces = ((p1, p2, p3), (p1, p4, p2))
            else:
                faces = clip_cell(p1, p2, p3, p4, tile.bounds)
            boundary_cell = (p1.x <= x_min or p2.x >= x_max
                             or p1.y <= y_min or p2.y >= y_max)
            for face in faces:
                tile.triangles.append(face)
                if boundary_cell:
                    for point in face:
                        tile.add_boundary_point(point)
    return tile


def clip_cell(p1, p2, p3, p4, bounds):
    """Intersect a cell's two original triangles with the clipping rectangle."""
    x0, y0, z0 = p1
    x1, y1, z1 = p2
    dx, dy = x1 - x0, y1 - y0
    x_min, y_min, x_max, y_max = bounds
    left, right = max(x0, x_min), min(x1, x_max)
    bottom, top = max(y0, y_min), min(y1, y_max)
    if left >= right or bottom >= top:
        return
    rectangle = [(left, bottom), (right, bottom), (right, top), (left, top)]
    make_point = type(p1)

    def diagonal_distance(point):
        distance = (point[0] - x0) * dy - (point[1] - y0) * dx
        tolerance = 8 * float_info.epsilon * dx * dy
        return 0 if abs(distance) <= tolerance else distance

    for upper in (True, False):
        polygon = []
        previous = rectangle[-1]
        distance = diagonal_distance(previous)
        previous_inside = distance <= 0 if upper else distance >= 0
        for current in rectangle:
            distance = diagonal_distance(current)
            inside = distance <= 0 if upper else distance >= 0
            if inside != previous_inside:
                # Derive intersections from the original diagonal in every tile.
                if previous[0] == current[0]:
                    x = current[0]
                    y = min(top, max(bottom, y0 + (x - x0) * dy / dx))
                else:
                    y = current[1]
                    x = min(right, max(left, x0 + (y - y0) * dx / dy))
                polygon.append((x, y, True))
            if inside:
                polygon.append((*current, distance == 0))
            previous, previous_inside = current, inside

        points = []
        for x, y, diagonal in polygon:
            if points and points[-1].x == x and points[-1].y == y:
                continue
            u, v = (x - x0) / dx, (y - y0) / dy
            # Preserve corner heights and evaluate shared edges consistently.
            if x == x0 and y == y0:
                z = z0
            elif x == x1 and y == y1:
                z = z1
            elif x == x0 and y == y1:
                z = p3.z
            elif x == x1 and y == y0:
                z = p4.z
            elif x == x0:
                z = z0 + v * (p3.z - z0)
            elif x == x1:
                z = p4.z + v * (z1 - p4.z)
            elif y == y0:
                z = z0 + u * (p4.z - z0)
            elif y == y1:
                z = p3.z + u * (z1 - p3.z)
            elif diagonal:
                z = z0 + u * (z1 - z0)
            elif upper:
                z = z0 + u * (z1 - p3.z) + v * (p3.z - z0)
            else:
                z = z0 + u * (p4.z - z0) + v * (z1 - p4.z)
            points.append(make_point(x, y, z))
        if len(points) > 1 and points[0][:2] == points[-1][:2]:
            points.pop()
        for k in range(1, len(points) - 1):
            a, b, c = points[0], points[k], points[k + 1]
            area2 = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
            if area2 > 0:
                yield a, b, c
