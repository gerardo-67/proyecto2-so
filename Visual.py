import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

fontsizeVar = 12

data = {
    "PAGE ID": list(range(1, 20)),
    "PID": [1]*5 + [2]*10 + [3]*4,
    "LOADED": ['X', 'X', '', 'X', '', 'X', 'X', 'X', 'X', 'X', '', 'X', '', '', 'X', 'X', 'X', '', ''],
    "L-ADDR": list(range(1, 20)),
    "M-ADDR": [1,2,3,4,5,8,9,10,11,12,21,22,13,14,15,25,26,18,19],
    "D-ADDR": ['', '', 143, '', 100, '', '', '', '', 231, '', '', 278, 245, '', 152, 153, 97, 12],
    "LOADED-T": ['0s', '1s', '5s', '5s', '', '3s', '4s', '7s', '12s', '13s', '14s', '15s', '', '', '151s', '152s', '153s', '', ''],
    "MARK": ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
}
df_opt = pd.DataFrame(data)
df_alg = pd.DataFrame(data)

stats1 = {
    "Processes": 5,
    "Sim-Time": "250s",
    "RAM KB": 244,
    "RAM %": "61%",
    "V-RAM KB": 40,
    "V-RAM %": "4%",
    "PAGES LOADED": 61,
    "PAGES UNLOADED": 85,
    "Thrashing": "150s",
    "Thrashing %": "60%",
    "Fragmentación": "256KB"
}

class MemoryBar(tk.Canvas):
    def __init__(self, parent, page_states, label, **kwargs):
        super().__init__(parent, **kwargs)
        self.page_states = page_states
        self.label = label
        self.draw_bar()

    def draw_bar(self):
        self.delete("all")
        page_width = 18
        page_height = 30
        gap = 2
        color_map = {
            0: 'lightgreen',
            1: 'khaki',
            2: 'lightpink',
            3: 'lightblue',
            4: 'lightsalmon',
            5: 'plum'
        }
        for i, state in enumerate(self.page_states):
            color = color_map.get(state, 'gray')
            x0 = i * (page_width + gap)
            y0 = 5
            x1 = x0 + page_width
            y1 = y0 + page_height
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')
        self.create_text((len(self.page_states)*(page_width+gap) - gap)/2, 40, text=self.label, font=("Arial", 12, "bold"))

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
        P = self.p_var.get()
        N = self.n_var.get()
        filename = self.file_var.get()


        if not filename and (P <= 0 or N <= 0):
            messagebox.showerror("Error", "Debe seleccionar un archivo o ingresar valores válidos para P y N.")
            return

        self.destroy()
        app = App(seed, algorithm, filename, P, N)
        app.mainloop()


class App(tk.Tk):
    def go_back(self):
        self.destroy()
        StartWindow().mainloop()

    def __init__(self, seed, algorithm, filename, P, N):
        super().__init__()

        self.seed = seed
        self.algorithm = algorithm
        self.filename = filename
        self.P = P
        self.N = N

        self.title("Simulación de Memoria - Layout Completo")
        self.geometry("1600x1000")
        self.resizable(True, True)

        # Estilo para botón grande
        style = ttk.Style()
        style.configure("Big.TButton", font=("Arial", 10, "bold"), padding=10)

        # Layout principal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)  # zona de tablas
        self.rowconfigure(3, weight=0)  # zona de botón

        mem_bar_left = MemoryBar(self, page_states=[1,1,0,2,2,3,3,4,4,5,5,0,1,2,3,4,5,1,2,3,0],
                                 label="RAM - OPT", width=800, height=50, bg='white')
        mem_bar_right = MemoryBar(self, page_states=[1,1,1,2,2,2,3,3,4,4,4,5,5,5,0,1,2,3,4,5,0],
                                  label="RAM - [ALG]", width=800, height=50, bg='white')
        mem_bar_left.grid(row=0, column=0, padx=20, pady=5, sticky='n')
        mem_bar_right.grid(row=0, column=1, padx=20, pady=5, sticky='n')

        frame_left = ttk.Frame(self)
        frame_left.grid(row=1, column=0, sticky='nsew', padx=10, pady=(5, 0))
        frame_left.columnconfigure(0, weight=1)
        frame_left.rowconfigure(1, weight=1)

        frame_right = ttk.Frame(self)
        frame_right.grid(row=1, column=1, sticky='nsew', padx=10, pady=(5, 0))
        frame_right.columnconfigure(0, weight=1)
        frame_right.rowconfigure(1, weight=1)

        ttk.Label(frame_left, text="MMU - OPT", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(frame_right, text="MMU - [ALG]", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=5)

        self.table_container_left, self.tree1 = create_table(frame_left, df_opt)
        self.table_container_left.grid(row=1, column=0, sticky='nsew', pady=5)

        self.table_container_right, self.tree2 = create_table(frame_right, df_alg)
        self.table_container_right.grid(row=1, column=0, sticky='nsew', pady=5)

        self.stats_frame1 = create_stats_table(frame_left, stats1)
        self.stats_frame1.grid(row=2, column=0, sticky='ew', pady=10)

        self.stats_frame2 = create_stats_table(frame_right, stats1)
        self.stats_frame2.grid(row=2, column=0, sticky='ew', pady=10)

        # Botón Volver abajo centrado
        btn_back = ttk.Button(self, text="Regresar", command=self.go_back, style="Big.TButton")
        btn_back.grid(row=3, column=0, sticky='w', padx=30, pady=30)

if __name__ == "__main__":
    start = StartWindow()
    start.mainloop()
