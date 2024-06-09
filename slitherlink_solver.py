import converter
import operator
from pysat.solvers import Minisat22


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
        self.converter = converter.Converter(self.row, self.col)

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
                    encode_value = self.converter.encode_edge(i, j)
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
                encode_value = self.converter.encode_vertex(i, j)
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
        edge = [i for i in self.model if i > 0]
        map = {}
        for x in edge: map[x] = 0

        def get_root(e):
            if map[e] == 0: return e
            map[e] = get_root(map[e])
            return map[e]

        for x in edge:
            u = self.converter.decode_vertex(x)
            neighbor_1 = self.converter.encode_vertex(u[0], u[1])
            neighbor_2 = self.converter.encode_vertex(u[2], u[3])
            neighbor = list(set(neighbor_1 + neighbor_2))
            for y in neighbor:
                if y in map:
                    p = get_root(x)
                    q = get_root(y)
                    if p > q:
                        p, q = q, p
                    if p != q:
                        map[q] = p

        for x in map:
            if map[x]:
                map[x] = get_root(x)

        for x in map:
            if map[x] == 0:
                map[x] = x

        g = [[set() for _ in range(self.col)] for _ in range(self.row)]
        g_cnt = {}
        map_cnt = {}
        for x in map:
            if map[x] not in map_cnt:
                map_cnt[map[x]] = 1
            else:
                map_cnt[map[x]] += 1

        for x in map:
            g_cnt[map[x]] = 0

        save = []

        for i in range(self.row):
            for j in range(self.col):
                if self.board[i][j] > 0:
                    encode_value = self.converter.encode_edge(i, j)
                    encode_value = [x for x in encode_value if x in map]
                    for x in encode_value:
                        g[i][j].add(map[x])
                    if len(g[i][j]) >= 2:
                        for y in g[i][j]:
                            g_cnt[y] += 1
                        save.append((i, j))

            g_cnt = dict(sorted(g_cnt.items(), key=lambda l: (map_cnt[l[0]], -l[1])))

        for x in g_cnt:
            if g_cnt[x] == 0:
                self.solver.add_clause([-i for i in edge if map[i] == x])
                self.cond.append([-i for i in edge if map[i] == x])

        for x in g_cnt:
            if g_cnt[x] == 0:
                continue
            self.solver.add_clause([-i for i in edge if map[i] == x])
            self.cond.append([-i for i in edge if map[i] == x])
            cur = []
            for y in save:
                if x in g[y[0]][y[1]]:
                    for z in g[y[0]][y[1]]:
                        g_cnt[z] -= 1
                    cur.append(y)
            for z in cur:
                save.remove(z)

        return len(g_cnt)