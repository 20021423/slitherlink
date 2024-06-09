import converter_2

class SlitherlinkSolver:
    def __init__(self, solver, version):
        self.converter = None
        self.board = []
        self.base_cond = []
        self.cond = []
        self.solver = solver()
        self.row = None
        self.col = None
        self.result = None
        self.model = None
        self.model_arr = []
        self.num_loops = 1

    def load_from_file(self, filename):
        with open(filename) as f:
            self.row, self.col = map(int, f.readline().split())
            self.board = [[-1 for _ in range(self.col)] for _ in range(self.row)]
            while line := f.readline():
                x, y, k = map(int, line.split())
                self.board[x - 1][y - 1] = k
        self.converter = converter_2.Converter(self.row, self.col)

    def add_first_rule(self, edges, k):
        e1, e2, e3, e4 = edges
        if k == 0:
            self.cond.append([-e1])
            self.cond.append([-e2])
            self.cond.append([-e3])
            self.cond.append([-e4])
        elif k == 1:
            self.cond.append([e1, e2, e3, e4])
            self.cond.append([-e1, -e2])
            self.cond.append([-e1, -e3])
            self.cond.append([-e1, -e4])
            self.cond.append([-e2, -e3])
            self.cond.append([-e2, -e4])
            self.cond.append([-e3, -e4])
        elif k == 2:
            self.cond.append([e1, e2, e3])
            self.cond.append([e1, e2, e4])
            self.cond.append([e1, e3, e4])
            self.cond.append([e2, e3, e4])
            self.cond.append([-e1, -e2, -e3])
            self.cond.append([-e1, -e2, -e4])
            self.cond.append([-e1, -e3, -e4])
            self.cond.append([-e2, -e3, -e4])
        elif k == 3:
            self.cond.append([-e1, -e2, -e3, -e4])
            self.cond.append([e1, e2])
            self.cond.append([e1, e3])
            self.cond.append([e1, e4])
            self.cond.append([e2, e3])
            self.cond.append([e2, e4])
            self.cond.append([e3, e4])
        elif k == 4:
            self.cond.append([e1])
            self.cond.append([e2])
            self.cond.append([e3])
            self.cond.append([e4])
        else:
            raise ValueError

    def build_first_rule(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.board[i][j] >= 0:
                    encode_value = self.converter.get_side_edges(i, j)
                    self.add_first_rule(encode_value, self.board[i][j])

    def add_second_rule(self, edges):
        if len(edges) == 2:
            e1, e2 = edges
            self.cond.append([-e1, e2])
            self.cond.append([e1, -e2])
        elif len(edges) == 3:
            e1, e2, e3 = edges
            self.cond.append([-e1, e2, e3])
            self.cond.append([e1, -e2, e3])
            self.cond.append([e1, e2, -e3])
            self.cond.append([-e1, -e2, -e3])
        elif len(edges) == 4:
            e1, e2, e3, e4 = edges
            self.cond.append([-e1, -e2, -e3])
            self.cond.append([-e1, -e2, -e4])
            self.cond.append([-e1, -e3, -e4])
            self.cond.append([-e2, -e3, -e4])
            self.cond.append([-e1, e2, e3, e4])
            self.cond.append([e1, -e2, e3, e4])
            self.cond.append([e1, e2, -e3, e4])
            self.cond.append([e1, e2, e3, -e4])
        else:
            raise ValueError

    def build_second_rule(self):
        for i in range(self.row + 1):
            for j in range(self.col + 1):
                encode_value = self.converter.get_neighbor_edges(i, j)
                self.add_second_rule(encode_value)

    def solve(self):
        self.build_second_rule()
        self.build_first_rule()

        for cond in self.cond:
            self.solver.add_clause(cond)
        self.base_cond = [x for x in self.cond]
        self.result = self.solver.solve()
        self.model = self.solver.get_model()
        self.model_arr.append(self.model)
        self.loop_solve()

    def loop_solve(self):
        while self.result and self.loop_count() != 1:
            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)

    def loop_count(self):
        edges = {i for i in self.model if i > 0}
        visited = {}

        def bfs(x_0, cnt):
            queue = [x_0]
            while len(queue) > 0:
                x = queue.pop()
                visited[x] = cnt
                u = self.converter.get_two_vertices(x)
                neighbor_edges_1 = self.converter.get_neighbor_edges(u[0], u[1])
                neighbor_edges_2 = self.converter.get_neighbor_edges(u[2], u[3])
                for neighbor_edge in neighbor_edges_1 + neighbor_edges_2:
                    if neighbor_edge not in visited and neighbor_edge in edges:
                        queue.append(neighbor_edge)

        count = 0
        for edge in edges:
            if edge not in visited:
                bfs(edge, count)
                count += 1

        if count == 1:
            return 1

        for i in range(count):
            self.solver.add_clause([-x for x in edges if visited[x] == i])
            self.cond.append([-x for x in edges if visited[x] == i])

        return count