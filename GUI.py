import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import time
from slitherlink_solver_2 import SlitherlinkSolver
from pysat.solvers import Minisat22

class SlitherlinkApp(tk.Tk):

    def __init__(self,*args,**kwargs):
        self.problem_Set =0
        tk.Tk.__init__(self,*args,**kwargs)

        tk.Tk.wm_title(self,"Slitherlink Solver")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both",expand=True)

        self.container.grid_rowconfigure(0,weight=1)
        self.container.grid_columnconfigure(0,weight=1)

        self.selected_choice=""
        self.name=""

        self.frames = dict()

        for F in (LoadPage,):

            frame = F(self.container,self)
            self.frames[F] = frame

            frame.grid(row=0,column=0,sticky="nsew")

        self.show_frame(LoadPage)

    def show_frame(self,cont):

        frame = self.frames[cont]
        frame.tkraise()

    def add_frame(self, cont):
        frame = cont(self.container,self)
        self.frames[cont] = frame

        frame.grid(row=0,column=0,sticky="nsew")

class LoadPage(tk.Frame):
    """This class creates a new frame in the app."""
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)

        self.controller = controller

        self.version_text = tk.StringVar()
        label0=tk.Label(self,text = "Version")
        label0.grid(row=0, column=0)
        self.version_choose = ttk.Combobox(self, textvariable = self.version_text)
        self.version_choose['values'] = ('1', '2')
        self.version_choose.current(0)
        self.version_choose["state"] = "readonly"
        self.version_choose.grid(row=0, column=1)

        label1=tk.Label(self,text = "Load file: ")
        label1.grid(row=1, column=0)
        self.filename = tk.StringVar()
        self.file_display = ttk.Label(self, textvariable=self.filename)
        self.file_display.grid(row=1, column=1)
        button1 = ttk.Button(self,text="Open", command=self.select_file)
        button1.grid(row=1, column=2)
        button2 = ttk.Button(self,text="Next", command=self.next)
        button2.grid(row=2, column=2)


    def close(self):
        app.quit()

    def select_file(self):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        self.controller.filename = fd.askopenfilename(
            title='Open a file',
            filetypes=filetypes)

        self.filename.set(self.controller.filename)

    def next(self):
        self.controller.version_text = self.version_text.get()
        self.controller.add_frame(SlitherlinkUIPage)
        self.controller.show_frame(SlitherlinkUIPage)


class SlitherlinkUIPage(tk.Frame):
    """This class creates a new frame in the app. This class is responsible for generating the sudoku grid."""
    time_taken=time.time()
    def __init__(self,parent,controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.solver = SlitherlinkSolver(Minisat22, controller.version_text)
        self.solver.load_from_file(self.controller.filename)

        width_value1 = self.winfo_screenwidth()
        height_value1 = self.winfo_screenheight()

        self.entries = []

        self.createCan()

        label0 = ttk.Label(self, text='Version ' + self.controller.version_text, font=(("Bold",20)))
        label0.place(x=1200, y=250)

        self.button = ttk.Button(self, text="Resolve", command=self.solve)
        self.button.place(x=1200,y=300)
        self.button_1 = ttk.Button(self, text="Previous", command=self.solve_prev)
        self.button_1.place(x=1300, y=300)
        self.button_2 = ttk.Button(self, text="Next", command=self.solve_next)
        self.button_2.place(x=1400, y=300)
        self.button_1['state'] = "disable"
        self.button_2['state'] = "disable"
        self.num_conds = tk.StringVar()
        self.run_time = tk.StringVar()
        self.num_variable = tk.StringVar()
        self.num_loops = tk.StringVar()
        self.count = 0

        label1 = ttk.Label(self, text="Number of loops: ")
        label1.place(x=1200, y=330)
        label2 = ttk.Label(self, textvariable=self.num_loops)
        label2.place(x=1400, y=330)

        label1 = ttk.Label(self, text="Number of conditions: ")
        label1.place(x=1200, y=360)
        label2 = ttk.Label(self, textvariable=self.num_conds)
        label2.place(x=1400, y=360)


        label3 = ttk.Label(self, text="Number of variable: ")
        label3.place(x=1200, y=390)
        label4 = ttk.Label(self, textvariable=self.num_variable)
        label4.place(x=1400, y=390)


        label5 = ttk.Label(self, text="Run time (seconds): ")
        label5.place(x=1200, y=420)
        label6 = ttk.Label(self, textvariable=self.run_time)
        label6.place(x=1400, y=420)



    def solve(self, *args):
        self.button['state'] = "disable"
        self.count = 0
        start_time = time.time()

        self.solver.solve()

        end_time = time.time()

        self.updateCan()

        self.num_loops.set(self.solver.num_loops)

        self.num_conds.set(len(self.solver.cond))

        self.run_time.set(end_time - start_time)

        self.num_variable.set(len(self.solver.model))

        self.count = len(self.solver.model_arr)

        self.button_1['state'] = "enable"


    def solve_prev(self, *args):
        self.count -= 1
        if self.count == 0:
            self.button_1['state'] = "disable"
        self.solver.model = self.solver.model_arr[self.count]

        self.updateCan()
        self.num_loops.set(self.count)

        self.button_2['state'] = "enable"

    def solve_next(self, *args):
        self.count += 1
        if self.count == len(self.solver.model_arr)-1:
            self.button_2['state'] = "disable"
        self.solver.model = self.solver.model_arr[self.count]

        self.updateCan()
        self.num_loops.set(self.count)

        self.button_1['state'] = "enable"


    def updateCan(self):
        self.canvas.delete("all")
        self.createCan()
        if self.solver.result:
            edges = [self.solver.converter.get_two_vertices(i) for i in self.solver.model if i > 0]
            for edge in edges:
                x1, y1, x2, y2 = edge
                x1 = x1 * 28 + 10
                y1 = y1 * 28 + 10
                x2 = x2 * 28 + 10
                y2 = y2 * 28 + 10
                self.canvas.create_line(y1, x1, y2, x2, width=1)


    def createCan(self):

        self.canvas = tk.Canvas(self, height=self.solver.row * 28 + 30, width=self.solver.col * 28 + 30)

        for i in range(self.solver.col + 1):
            for j in range(self.solver.row + 1):
                x = i * 28 + 10
                y = j * 28 + 10
                self.canvas.create_oval(x-1, y-1, x+1, y+1, width=3)
        self.canvas.place(x=0, y=0)
        p, q = 18, 14

        for i in range(self.solver.row):
            for k in range(self.solver.col):
                x = self.solver.board[i][k]
                text_value = tk.StringVar()
                if(x >= 0):
                    text_value.set(x)

                entry = tk.Label(self, textvariable=text_value, fg='black', font=("Normal",10))
                entry.grid_slaves(row=i, column=k)
                entry.place(x=p, y=q)
                self.entries.append(text_value)
                p += 28.0
            q += 28
            p = 18


app = SlitherlinkApp()
width_value = app.winfo_screenwidth()
height_value = app.winfo_screenheight()
app.geometry("%dx%d+0+0" %(width_value,height_value))
app.mainloop()

