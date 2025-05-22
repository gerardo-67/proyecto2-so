'''
Parser de archivos
Fecha de inicio: 1:00pm 12/5/25
Última modificación: 7:00 pm 20/5/25
'''
import re
import os


class Line:
    def __init__(self, instruction: str, arguments: list[int]):
        self.instruction: str = instruction
        self.arguments: list[int] = arguments
class Parser:
    def __init__(self):
        # Diccionario de todas las paginas y sus respectivas apariciones. Necesario para el algoritmo optimo,
        self.page_accesses: dict[int, list[int]] = {}
        # Diccionario de todos los punteros y sus respectivas paginas. Necesario para el algoritmo optimo
        self.pointer_to_pages:dict[int, int] = {}
        self.processes_to_pointers:dict[int, list[int]] = {}
        self.instruction_log: list[Line] = []
        self.__next_pointer_id:int = 1 
        self.__next_page_id:int = 1

        self.__instruction_index:int = 1

    def __instructionNew(self, pid, size):
        #print(f"NEW: PID {pid} requests {size} bytes")

        #Si el proceso no está en la tabla se agrega 
        if pid not in self.processes_to_pointers:
            self.processes_to_pointers[pid] = []
        
        # Calcula cuántas páginas necesita el puntero según el tamaño solicitado.
        pages_needed:int
        if (size == 1024):
            pages_needed = 1
        else:
            pages_needed = (size // 1024) + 1
        assigned_pages = []

        # Asigna nuevas páginas al puntero y registra el acceso inicial de cada página.
        for page_id in range(self.__next_page_id, self.__next_page_id + pages_needed):
            if page_id not in self.page_accesses:
                self.page_accesses[page_id] = []  # Inicializa la lista de accesos para la página.
            self.page_accesses[page_id].append(self.__instruction_index)  # Registra el acceso inicial.
            self.__instruction_index += 1
            assigned_pages.append(page_id)  # Guarda el ID de la página asignada al puntero.

        self.__next_page_id += pages_needed
        self.pointer_to_pages[self.__next_pointer_id] = assigned_pages
        
        #Asigna un puntero al proceso y lo guarda
        self.processes_to_pointers[pid].append(self.__next_pointer_id)

        self.__next_pointer_id += 1
        # print(f"Assigned ptr {self.__next_pointer_id} to PID {pid}")
        # print ("Symbol table:", self.processes_to_pointers)
        # print ("self.__next_pointer_id:", self.__next_pointer_id)

        self.instruction_log.append(Line("new", [pid, size]))

    def __instructionUse(self, ptr):
        # print(f"USE: Using ptr {ptr}")

        for page in self.pointer_to_pages[ptr]:
            if page not in self.page_accesses:
                self.page_accesses[page] = []
            self.page_accesses[page].append(self.__instruction_index)
            self.__instruction_index += 1

        self.instruction_log.append(Line("use", [ptr]))

    def __instructionDelete(self, ptr):
        # print(f"DELETE: Removing ptr {ptr}")
        self.instruction_log.append(Line("delete", [ptr]))
        # Recorre la tabla de símbolos y elimina el puntero
        #for pid in self.processes_to_pointers:
        #   if ptr in self.processes_to_pointers[pid]:
        #      del self.processes_to_pointers[pid][ptr]
        #     break

    def __instructionKill(self, pid):
        # print(f"KILL: Terminating process {pid}")
        self.instruction_log.append(Line("kill", [pid]))
        # Elimina el proceso de la tabla de símbolos
        #if pid in self.processes_to_pointers:
        #   del self.processes_to_pointers[pid]


    #Utiliza expresiones regulares para analizar las lineas y extraer su contenido
    def __processLine(self, line):
        #print("\n............\nLine:", line) 

        if match := re.match(r'new\((\d+),(\d+)\)', line):
            pid, size = map(int, match.groups()) 
            self.__instructionNew(pid, size)
            
        elif match := re.match(r'use\((\d+)\)', line):
            ptr = int(match.group(1)) #accede al primer grupo capturado de la ER
            self.__instructionUse(ptr)
            
        elif match := re.match(r'delete\((\d+)\)', line):
            ptr = int(match.group(1))
            self.__instructionDelete(ptr)
            
        elif match := re.match(r'kill\((\d+)\)', line):
            pid = int(match.group(1))
            self.__instructionKill(pid)
            
        else:
            print(f"Invalid instruction: {line}")

    #Lee el archivo de instrucciones y manda cada línea a la función __processLine
    # r"C:\Users\gerar\OneDrive\AAA TEC\Semestre 1 2025\SO\Proyecto 2\instrucciones.txt"
    def readFile(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"The file does not exist: {file_path}")
            return
        with open(file_path, "r") as f:
            for line in f:
                self.__processLine(line)
        #print(self.processes_to_pointers)




parser = Parser()

parser.readFile("generatedInstructions.txt")


#print("Pages:", parser.page_accesses)
#print("Pointers:", parser.pointer_to_pages)