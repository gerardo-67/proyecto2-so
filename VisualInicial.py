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
        color_map = {0: 'lightgreen', 1: 'khaki', 2: 'lightpink', 3: 'lightblue', 4: 'lightsalmon', 5: 'plum'}
        for i, state in enumerate(self.page_states):
            color = color_map.get(state, 'gray')
            x0 = i * (page_width + gap)
            y0 = 5
            x1 = x0 + page_width
            y1 = y0 + page_height
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')
        total_width = len(self.page_states)*(page_width+gap)-gap
        self.create_text(total_width/2, 40, text=self.label, font=("Arial",12,"bold"))


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
    col_widths = {"PAGE ID":60, "PID":40, "LOADED":60, "L-ADDR":60, "M-ADDR":60, "D-ADDR":60, "LOADED-T":60, "MARK":40}
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col,60), anchor='center', stretch=False)
    for _, row in df.iterrows():
        tree.insert('', 'end', values=list(row))
    return container, tree


def create_stats_table(frame, stats):
    stats_frame = ttk.Frame(frame, relief='groove', borderwidth=1)
    stats_frame.grid(row=2, column=0, sticky='nsew', pady=10)
    cols = [["Processes","Sim-Time"],["RAM KB","RAM %","V-RAM KB","V-RAM %"],["PAGES LOADED","PAGES UNLOADED","Thrashing","Thrashing %","Fragmentación"]]
    for idx, names in enumerate(cols):
        sub = ttk.Frame(stats_frame)
        sub.grid(row=0, column=idx, padx=10)
        for i, name in enumerate(names):
            ttk.Label(sub, text=name, font=("Arial",9,"bold"), borderwidth=1, relief="solid", anchor="center", width=15).grid(row=i, column=0, sticky='ew')
            ttk.Label(sub, text=stats.get(name,""), font=("Arial",9), borderwidth=1, relief="solid", anchor="center", width=15).grid(row=i, column=1, sticky='ew')
    thr = stats_frame.winfo_children()[2].winfo_children()
    if len(thr)>=10:
        for w in thr[6:10]: w.config(background='pink')
    return stats_frame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulación de Memoria - Layout Completo")
        self.geometry("1600x1000")
        self.resizable(True, True)

        # Botón Regresar a HomePage
        back_btn = ttk.Button(self, text="Regresar", command=self.go_home)
        back_btn.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        frame_left = ttk.Frame(self)
        frame_left.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        frame_left.columnconfigure(0, weight=1)
        frame_left.rowconfigure(1, weight=1)

        frame_right = ttk.Frame(self)
        frame_right.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        frame_right.columnconfigure(0, weight=1)
        frame_right.rowconfigure(1, weight=1)

        mem1 = MemoryBar(self, page_states=[1,1,0,2,2,3,3,4,4,5,5,0,1,2,3,4,5,1,2,3,0], label="RAM - OPT", width=800, height=50, bg='white')
        mem2 = MemoryBar(self, page_states=[1,1,1,2,2,2,3,3,4,4,4,5,5,5,0,1,2,3,4,5,0], label="RAM - [ALG]", width=800, height=50, bg='white')
        mem1.grid(row=0, column=0, padx=20, pady=10); mem2.grid(row=0, column=1, padx=20, pady=10)

        ttk.Label(frame_left, text="MMU - OPT", font=("Arial",14,"bold")).grid(row=0, column=0, pady=5)
        ttk.Label(frame_right, text="MMU - [ALG]", font=("Arial",14,"bold")).grid(row=0, column=0, pady=5)

        tbl1, self.tree1 = create_table(frame_left, df_opt)
        tbl1.grid(row=1, column=0, sticky='nsew', pady=5)
        tbl2, self.tree2 = create_table(frame_right, df_alg)
        tbl2.grid(row=1, column=0, sticky='nsew', pady=5)

        st1 = create_stats_table(frame_left, stats1)
        st2 = create_stats_table(frame_right, stats1)
        st1.grid(row=2, column=0, sticky='ew', pady=10)
        st2.grid(row=2, column=0, sticky='ew', pady=10)

    def go_home(self):
        self.destroy()
        HomePage.HomePage().mainloop()

if __name__ == "__main__":
    app = App()
    app.mainloop()
