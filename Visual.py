import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import memory_map as mm

import InstructionGenerator
import Parser

fontsizeVar = 12

class MemoryBar(tk.Frame):
    def __init__(self, parent, page_states, label, width=800, height=50, **kwargs):
        super().__init__(parent, **kwargs)
        self.page_states = page_states
        self.label = label
        self.width = width
        self.height = height

        # Canvas dentro de un Frame para scrollbar
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg='white')
        self.hscroll = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hscroll.set)

        self.hscroll.pack(side='bottom', fill='x')
        self.canvas.pack(side='top', fill='both', expand=True)

        # Frame interno para dibujar
        self.inner_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0,0), window=self.inner_frame, anchor='nw')

        self.inner_frame.bind("<Configure>", self._on_frame_configure)

        self.draw_bar()

    def _on_frame_configure(self, event):
        # Ajustar scrollregion del canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def draw_bar(self):
        # Limpiamos el frame interno
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        page_width = 18
        page_height = 12  # Barra más delgada
        gap = 2
        color_map = {
            0: 'lightgreen',
            1: 'khaki',
            2: 'lightpink',
            3: 'lightblue',
            4: 'lightsalmon',
            5: 'plum'
        }

        total_width = max(1, len(self.page_states)) * (page_width + gap) - gap
        self.inner_frame.config(width=total_width, height=self.height)

        # Crear canvas para barras
        bar_canvas = tk.Canvas(self.inner_frame, width=total_width, height=self.height, bg='white', highlightthickness=0)
        bar_canvas.pack()

        y1 = 0  # Valor por defecto en caso de no haber barras

        for i, state in enumerate(self.page_states):
            color = color_map.get(state, 'gray')
            x0 = i * (page_width + gap)
            y0 = 10
            x1 = x0 + page_width
            y1 = y0 + page_height
            bar_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')

        # Texto centrado debajo de las barras, con posición segura
        text_y = y1 + 15 if y1 else page_height + 25
        bar_canvas.create_text(total_width / 2, text_y, text=self.label, font=("Arial", 10, "bold"))


def create_table(parent, df):
    container = ttk.Frame(parent)
    container.grid(row=0, column=0, sticky='nsew')

    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    tree = ttk.Treeview(container, columns=list(df.columns), show='headings', height=15)
    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    col_widths = {
        "PAGE ID": 60,
        "PID": 40,
        "LOADED": 60,
        "L-ADDR": 60,
        "M-ADDR": 60,
        "D-ADDR": 60,
        "LOADED-T": 60,
        "MARK": 40
    }

    for col in df.columns:
        width = col_widths.get(col, 60)
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor='center', stretch=False)

    for _, row in df.iterrows():
        tree.insert('', 'end', values=list(row))

    return container, tree

def create_stats_table(frame, stats):
    for child in frame.winfo_children():
        child.destroy()

    stats_frame = ttk.Frame(frame, relief='groove', borderwidth=1)
    stats_frame.grid(row=2, column=0, sticky='nsew', pady=10)

    cols = [
        ["Processes", "Sim-Time"],
        ["RAM KB", "RAM %", "V-RAM KB", "V-RAM %"],
        ["PAGES LOADED", "PAGES UNLOADED", "Thrashing", "Thrashing %", "Fragmentación"]
    ]

    for col_idx, col_names in enumerate(cols):
        sub_frame = ttk.Frame(stats_frame)
        sub_frame.grid(row=0, column=col_idx, padx=10)

        for i, name in enumerate(col_names):
            ttk.Label(sub_frame, text=name, font=("Arial", 9, "bold"),
                      borderwidth=1, relief="solid", anchor="center", width=15).grid(row=i, column=0, sticky='ew')
            value = stats.get(name, "")
            ttk.Label(sub_frame, text=value, font=("Arial", 9),
                      borderwidth=1, relief="solid", anchor="center", width=15).grid(row=i, column=1, sticky='ew')

    # Colorear Thrashing
    sub_frame_thrashing = stats_frame.winfo_children()[2]
    thrashing_widgets = sub_frame_thrashing.winfo_children()
    if len(thrashing_widgets) >= 10:
        for widget in thrashing_widgets[6:10]:
            widget.config(background='pink')

    return stats_frame

class StartWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configuración de Simulación")
        self.geometry("500x400")

        # Algoritmo
        ttk.Label(self, text="Algoritmo:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.alg_var = tk.StringVar(value="FIFO")
        ttk.Combobox(self, textvariable=self.alg_var, values=["FIFO", "SC", "MRU", "RND"], state='readonly').grid(row=0, column=1, pady=5, padx=5)

        # Semilla
        ttk.Label(self, text="Semilla:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.seed_var = tk.IntVar(value=0)
        ttk.Entry(self, textvariable=self.seed_var).grid(row=1, column=1, pady=5, padx=5)

        # Número de operaciones (N)
        ttk.Label(self, text="Número de operaciones (N):").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.n_var = tk.StringVar(value="500")
        ttk.Combobox(self, textvariable=self.n_var, values=["500", "1000", "5000"], state='readonly').grid(row=2, column=1, pady=5, padx=5)

        # Número de procesos (P)
        ttk.Label(self, text="Número de procesos (P):").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.p_var = tk.StringVar(value="10")
        ttk.Combobox(self, textvariable=self.p_var, values=["10", "50", "100"], state='readonly').grid(row=3, column=1, pady=5, padx=5)

        # Archivo
        ttk.Label(self, text="Archivo (.txt/.csv):").grid(row=4, column=0, sticky='w', pady=5, padx=5)
        self.file_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.file_var).grid(row=4, column=1, pady=5, padx=5)
        ttk.Button(self, text="Examinar", command=self.browse_file).grid(row=4, column=2, pady=5, padx=5)

        # Botón iniciar
        ttk.Button(self, text="Iniciar Simulación", command=self.start_simulation).grid(row=5, column=0, columnspan=3, pady=20)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt;*.csv"), ("Todos los archivos", "*.*")])
        if file:
            self.file_var.set(file)

    def start_simulation(self):
        algorithm = self.alg_var.get()
        seed = self.seed_var.get()
        P = int(self.p_var.get())
        N = int(self.n_var.get())
        filename = self.file_var.get()

        if not filename:
            InstructionGenerator.generateInstructions(P, N, seed)
            filename = "generatedInstructions.txt"

        parser = Parser.Parser()
        parser.readFile(filename)

        self.destroy()
        app = App(seed, algorithm, filename, P, N)
        app.mainloop()

class App(tk.Tk):
    def go_back(self):
        self.destroy()
        StartWindow().mainloop()

    def __init__(self, seed=0, algorithm="FIFO", filename="", P="10", N="500"):
        super().__init__()

        self.seed = seed
        self.algorithm = algorithm
        self.filename = filename
        self.P = P
        self.N = N

        self.title("Simulación de Memoria - Layout Completo")
        self.geometry("1600x1000")
        self.resizable(True, True)

        style = ttk.Style()
        style.configure("Big.TButton", font=("Arial", 10, "bold"), padding=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=0)

        # Memoria visual (barras)
        self.mem_bar_left = MemoryBar(self, page_states=[], label="RAM - OPT", width=800, height=50, bg='white')
        self.mem_bar_right = MemoryBar(self, page_states=[], label=f"RAM - {self.algorithm}", width=800, height=50, bg='white')

        self.mem_bar_left.grid(row=0, column=0, padx=20, pady=5, sticky='n')
        self.mem_bar_right.grid(row=0, column=1, padx=20, pady=5, sticky='n')

        # Frames para tablas y stats
        frame_left = ttk.Frame(self)
        frame_left.grid(row=1, column=0, sticky='nsew', padx=10, pady=(5, 0))
        frame_left.columnconfigure(0, weight=1)
        frame_left.rowconfigure(1, weight=1)

        frame_right = ttk.Frame(self)
        frame_right.grid(row=1, column=1, sticky='nsew', padx=10, pady=(5, 0))
        frame_right.columnconfigure(0, weight=1)
        frame_right.rowconfigure(1, weight=1)

        ttk.Label(frame_left, text="MMU - OPT", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(frame_right, text=f"MMU - {self.algorithm}", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=5)

        self.df_opt = pd.DataFrame(columns=["PAGE ID","PID","LOADED","L-ADDR","M-ADDR","D-ADDR","LOADED-T","MARK"])
        self.df_alg = pd.DataFrame(columns=["PAGE ID","PID","LOADED","L-ADDR","M-ADDR","D-ADDR","LOADED-T","MARK"])

        self.table_container_left, self.tree1 = create_table(frame_left, self.df_opt)
        self.table_container_left.grid(row=1, column=0, sticky='nsew', pady=5)

        self.table_container_right, self.tree2 = create_table(frame_right, self.df_alg)
        self.table_container_right.grid(row=1, column=0, sticky='nsew', pady=5)

        self.stats_frame1 = ttk.Frame(frame_left, relief='groove', borderwidth=1)
        self.stats_frame1.grid(row=2, column=0, sticky='ew', pady=10)

        self.stats_frame2 = ttk.Frame(frame_right, relief='groove', borderwidth=1)
        self.stats_frame2.grid(row=2, column=0, sticky='ew', pady=10)

        self.btn_run = ttk.Button(self, text="Ejecutar Simulación", command=self.run_simulation, style="Big.TButton")
        self.btn_run.grid(row=3, column=1, sticky='e', padx=30, pady=30)

        btn_back = ttk.Button(self, text="Regresar", command=self.go_back, style="Big.TButton")
        btn_back.grid(row=3, column=0, sticky='w', padx=30, pady=30)

    def run_simulation(self):
        strategy_map = {
            "FIFO": mm.FIFOPageReplacementStrategy,
            "SC": mm.SecondChancePageReplacementStrategy,
            "MRU": mm.MRUPageReplacementStrategy,
            "RND": mm.RandomPageReplacementStrategy
        }

        replacement_class = strategy_map.get(self.algorithm, mm.RandomPageReplacementStrategy)

        pages_info_alg, stats_alg = mm.main(replacement_class, self.filename)
        self.df_alg = pd.DataFrame(pages_info_alg)
        self.update_table(self.tree2, self.df_alg)
        self.update_stats(stats_alg, self.stats_frame2)

        pages_info_opt, stats_opt = mm.main(mm.OptimalPageReplacementStrategy, self.filename)
        self.df_opt = pd.DataFrame(pages_info_opt)
        self.update_table(self.tree1, self.df_opt)
        self.update_stats(stats_opt, self.stats_frame1)

        self.update_memory_bars(pages_info_opt, pages_info_alg)

    def update_table(self, tree, df):
        tree.delete(*tree.get_children())
        for _, row in df.iterrows():
            tree.insert('', 'end', values=list(row))

    def update_stats(self, stats, frame):
        for child in frame.winfo_children():
            child.destroy()
        create_stats_table(frame, stats).grid()

    def update_memory_bars(self, pages_info_opt, pages_info_alg):
        frame_count = 100
        states_opt = [0]*frame_count
        states_alg = [0]*frame_count

        for page in pages_info_opt:
            if page['LOADED'] == 'X' and page['M-ADDR'] != '':
                idx = int(page['M-ADDR'])
                if 0 <= idx < frame_count:
                    states_opt[idx] = 1

        for page in pages_info_alg:
            if page['LOADED'] == 'X' and page['M-ADDR'] != '':
                idx = int(page['M-ADDR'])
                if 0 <= idx < frame_count:
                    states_alg[idx] = 1

        self.mem_bar_left.page_states = states_opt
        self.mem_bar_left.draw_bar()

        self.mem_bar_right.page_states = states_alg
        self.mem_bar_right.draw_bar()


if __name__ == "__main__":
    StartWindow().mainloop()
