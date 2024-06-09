import numpy as np
import math

import converter_2


class SlitherlinkSolver:
    def __init__(self, solver, version):
        self.solver = solver()
        self.result = None
        self.model = None
        self.curr_solver = None
        self.base_cond = []
        self.cond = None
        self.result_array = None
        self.board = None
        self.num_loops = 1
        self.list_loops = None
        self.model_arr = []
        self.version = version

    
    def load_from_file(self, filename):
        self.cond = []
        self.list_nums = []
        with open(filename, 'rt') as file1:
            lines = file1.readlines()
        assert len(lines[0].split()) == 2, "Invalid"
        self.row, self.col = [int(x) for x in lines[0].split()]
        self.board = -np.ones(self.row * self.col, dtype=np.int32).reshape(self.row, self.col)
        for i in range(1, len(lines)):
            if len(lines[i].split()) == 3:
                i, j, k = [int(x) for x in lines[i].split()]
                self.board[i-1, j-1] = int(k) 
                if k > 0:
                    self.list_nums.append((i-1, j-1))
        self.converter = converter_2.Converter(self.row, self.col)
    
    def build_file_cond(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.board[i, j] >= 0:
                    side_edges = self.get_side_edges(i, j)
                    k = self.board[i, j]
                    self.build_cond_with_cell(side_edges, k)
                    
                    
    def build_cond_with_cell(self, edges, k):
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
    
    def build_base_cond(self):
        for i in range(self.row + 1):
            for j in range(self.col + 1):
                neighbor_edges = self.get_neighbor_edges(i, j)
                self.build_cond_with_neighbor(neighbor_edges)
    
    def build_cond_with_neighbor(self, edges):
        if len(edges) == 2:
            self.build_two_neighbor(edges)
        elif len(edges) == 3:
            self.build_three_neighbor(edges)
        elif len(edges) == 4:
            self.build_four_neighbor(edges)
        else:
            raise ValueError
    
    def build_two_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        self.cond.append([-e1, e2])
        self.cond.append([e1, -e2])
        
    def build_three_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        e3 = edges[2]
        self.cond.append([-e1, e2, e3])
        self.cond.append([e1, -e2, e3])
        self.cond.append([e1, e2, -e3])
        self.cond.append([-e1, -e2, -e3])
    
    def build_four_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        e3 = edges[2]
        e4 = edges[3]
        self.cond.append([-e1, -e2, -e3])
        self.cond.append([-e1, -e2, -e4])
        self.cond.append([-e1, -e3, -e4])
        self.cond.append([-e2, -e3, -e4])
        self.cond.append([-e1, e2, e3, e4])
        self.cond.append([e1, -e2, e3, e4])
        self.cond.append([e1, e2, -e3, e4])
        self.cond.append([e1, e2, e3, -e4])
    
    def build_cond(self):
        self.build_base_cond()
        self.build_file_cond()
    
    def solve(self):
        self.build_cond()
        self.num_loops = 1
        for cond in self.cond:
            try:
                self.solver.add_clause(cond)
            except:
                print(f"Condition error: '{cond}'")
                raise
        self.base_cond = [x for x in self.cond]
        self.result = self.solver.solve()
        self.model = self.solver.get_model()
        self.model_arr.append(self.model)
        
        if self.version == '1':
            self.loop_solve_v1()
        elif self.version == '2':
            self.loop_solve_v2()
        else:
            raise ValueError
       
    # Version 1
    def loop_solve_v1(self):
        while self.result and self.has_multi_loops():
            if len(self.list_nums) == 0:
                self.result = True
                self.model = self.list_loops[0]
                return
            
            valid_loops = []
            
            for curr_loop in self.list_loops:
                list_nums = set(self.list_nums)
                for edge in curr_loop:
                    neighbor_cells = self.get_neighbor_cells(edge)
                    for cell in neighbor_cells:
                        if cell in list_nums:
                            is_side_cell = True
                            list_nums.remove(cell)
                if len(list_nums) > 0:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])
                else:
                    valid_loops.append(curr_loop)
                
            if len(valid_loops) > 1:
                for curr_loop in valid_loops:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])

            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)
    
    # Version 2
    def loop_solve_v2(self):
        while self.result and self.has_multi_loops():
            if len(self.list_nums) == 0:
                self.result = True
                self.model = self.list_loops[0]
                return
            
            valid_loops = []
            is_side_cell = False
            count = 0
            
            for curr_loop in self.list_loops:
                list_nums = set(self.list_nums)
                for edge in curr_loop:
                    neighbor_cells = self.get_neighbor_cells(edge)
                    for cell in neighbor_cells:
                        if cell in list_nums:
                            is_side_cell = True
                            list_nums.remove(cell)
                if is_side_cell:
                    count += 1
                if len(list_nums) > 0:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])
                else:
                    valid_loops.append(curr_loop)
                
            if len(valid_loops) > 1 or count >= 2:
                for curr_loop in valid_loops:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])
            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)
    
    def has_multi_loops(self):
        self.list_loops = []
        self.edges = {i for i in self.model if i > 0}
        first_edge = self.edges.pop()
        curr_loop = [first_edge]
        x, y = self.get_vertice(first_edge)
        
        while len(self.edges) > 0:  
            is_continue = True                
            neighbor_edges = self.get_neighbor_edges(x, y)
            for neighbor_edge in neighbor_edges:
                if neighbor_edge in self.edges:
                    self.edges.remove(neighbor_edge)
                    curr_loop.append(neighbor_edge)
                    x, y = self.get_next_vertice(x, y, neighbor_edge)
                    is_continue = False
                    break 
            if is_continue:        
                self.list_loops.append(curr_loop) 
                if len(self.edges) > 0:
                    first_edge = self.edges.pop()
                    curr_loop = [first_edge]
                    x, y = self.get_vertice(first_edge)
            
        self.list_loops.append(curr_loop)
        if len(self.list_loops) == 1:
            return False
        return True
        
    
    def get_next_vertice(self, old_x, old_y, edge):
        if edge <= (self.row + 1) * self.col:
            # Canh ngang
            t = edge - 1
            x1 = t // self.col
            y1 = t % self.col
            x2 = x1
            y2 = y1 + 1
        else: # Canh doc
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
        else: # Canh doc
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
        else: # Canh doc
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
                return [(x-1, y)]
            else:               
                return [(x, y), (x-1, y)]
        else: # Canh doc
            t = edge - (self.row + 1) * self.col - 1
            y = t // self.row
            x = t % self.row 
            if y == 0:
                return [(x, y)]
            elif y == self.col:
                return [(x, y-1)]
            else:               
                return [(x, y), (x, y-1)]
    
    def show_result(self):
        if self.result:
            print("Result: SAT")
            print([i for i in self.model if i > 0])
        else:
            print("Result: UNSAT")


if __name__ == "__main__":
    from pysat.solvers import Minisat22
    import time
    solver = SlitherlinkSolver(Minisat22)
    solver.load_from_file("puzzle/puzzle_30x25_hard_1.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
