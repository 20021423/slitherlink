class Converter:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    # 0 = up, 1 = down, 2 = left, 3 = right
    def encode_edge(self, x, y):
        e1 = x * self.col + y + 1
        e2 = (x + 1) * self.col + y + 1
        e3 = (self.row + 1) * self.col + y * self.row + x + 1
        e4 = (self.row + 1) * self.col + (y + 1) * self.row + x + 1
        return e1, e2, e3, e4

    def encode_vertex(self, x, y):
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

    def decode_vertex(self, edge):
        if edge <= (self.row + 1) * self.col:
            t = edge - 1
            x = t // self.col
            y = t % self.col
            return x, y, x, y + 1
        else:
            t = edge - (self.row + 1) * self.col - 1
            y = t // self.row
            x = t % self.row
            return x, y, x + 1, y
