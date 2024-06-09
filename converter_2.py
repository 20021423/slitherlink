class Converter:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def get_next_vertice(self, old_x, old_y, edge):
        if edge <= (self.row + 1) * self.col:
            # Canh ngang
            t = edge - 1
            x1 = t // self.col
            y1 = t % self.col
            x2 = x1
            y2 = y1 + 1
        else:  # Canh doc
            t = edge - (self.row + 1) * self.col - 1
            y1 = t // self.row
            x1 = t % self.row
            x2 = x1 + 1
            y2 = y1

        if x1 == old_x and y1 == old_y:
            return x2, y2
        else:
            return x1, y1

    def get_vertice(self, edge):
        if edge <= (self.row + 1) * self.col:
            # Canh ngang
            t = edge - 1
            x = t // self.col
            y = t % self.col
            return x, y
        else:  # Canh doc
            t = edge - (self.row + 1) * self.col - 1
            y = t // self.row
            x = t % self.row
            return x, y

    def get_two_vertices(self, edge):
        if edge <= (self.row + 1) * self.col:
            # Canh ngang
            t = edge - 1
            x = t // self.col
            y = t % self.col
            return x, y, x, y + 1
        else:  # Canh doc
            t = edge - (self.row + 1) * self.col - 1
            y = t // self.row
            x = t % self.row
            return x, y, x + 1, y

    def get_neighbor_edges(self, x, y):
        edges = []
        if y > 0:
            edges.append(x * self.col + y)
        if y < self.col:
            edges.append(x * self.col + y + 1)
        if x > 0:
            edges.append((self.row + 1) * self.col + y * self.row + x)
        if x < self.row:
            edges.append((self.row + 1) * self.col + y * self.row + x + 1)
        return edges

    def get_side_edges(self, x, y):
        e1 = x * self.col + y + 1
        e2 = (x + 1) * self.col + y + 1
        e3 = (self.row + 1) * self.col + y * self.row + x + 1
        e4 = (self.row + 1) * self.col + (y + 1) * self.row + x + 1
        return e1, e2, e3, e4

    def get_neighbor_cells(self, edge):
        if edge <= (self.row + 1) * self.col:
            # Canh ngang
            t = edge - 1
            x = t // self.col
            y = t % self.col
            if x == 0:
                return [(x, y)]
            elif x == self.row:
                return [(x - 1, y)]
            else:
                return [(x, y), (x - 1, y)]
        else:  # Canh doc
            t = edge - (self.row + 1) * self.col - 1
            y = t // self.row
            x = t % self.row
            if y == 0:
                return [(x, y)]
            elif y == self.col:
                return [(x, y - 1)]
            else:
                return [(x, y), (x, y - 1)]
