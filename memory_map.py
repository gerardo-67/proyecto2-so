from Parser import Parser, Line
from abc import ABC, abstractmethod
import random


parser = Parser()
parser.readFile(r"C:\Users\gerar\OneDrive\AAA TEC\Semestre 1 2025\SO\Proyecto 2\instrucciones.txt")

class Clock():
    def __init__(self):
        self.total_time = 0
        self.thrashing = 0
        self.hits = 0
        self.faults = 0
    def register_hit(self):
        self.total_time += 1
        self.hits += 1
    def register_fault(self):
        self.total_time += 5
        self.thrashing =+ 5
        self.faults += 1
    
class Page:
    __page_count = 1
    def __init__(self, pid: int):
        self.pid = pid
        self.page_id = Page.__page_count
        self.logical_address = self.__page_count
        Page.__page_count += 1
        self.loaded = False 
        self.memory_address = None # Cuando se carga la pagina en memoria se asigna el marco respectivo.
        self.disk_address = None 
        self.load_time = 0 # No se aun.
        self.mark = 0 # Aun no se ha implementado.

    def __str__(self):
        status = "Cargada en memoria" if self.loaded else "En disco"
        return (f"Página {self.page_id} (PID: {self.pid}) | "
                f"Dirección lógica: {self.logical_address} | "
                f"Dirección de memoria: {self.memory_address} | "
                f"Dirección de disco: {self.disk_address} | "
                f"Tiempo de carga: {self.load_time} | "
                f"Marca: {self.mark} | Estado: {status}")

class Pointer:
    def __init__(self, pid: int, size: int, pages: list[Page]):
        self.pid: int = pid
        self.size: int = size

        self.pages: list[Page] = pages
    def __str__(self):
        pages_str = "\n    ".join(str(page) for page in self.pages)
        return (f"Pointer (PID: {self.pid}, Size: {self.size} bytes)\n"
                f"  Pages:\n    {pages_str}")



class MemoryMap:
    def __init__(self):
        self.__pointer_count = 1
        self.pointers: dict[int, Pointer] = {}
    def add_pointer(self, pointer: Pointer):
        self.pointers[self.__pointer_count] = pointer
        self.__pointer_count += 1
        return 0
    def delete_pointer(self, pointer_id: int):
        del self.pointers[pointer_id]
        return 0
    def __str__(self):
        result = "Memory Map:\n"
        for pointer_id, pointer in self.pointers.items():
            result += f"  Pointer ID {pointer_id}:\n    {pointer}\n"
        return result
class PageReplacementStrategy(ABC):
    @abstractmethod
    def replace(self, frames:list[Page], page: Page):
        pass
    @abstractmethod
    def mark_page(self, page: Page):
        pass

class OptimalPageReplacementStrategy(PageReplacementStrategy):
    current_pointer_pages = []
    def replace(self, frames:list[Page], page:Page):
        farthest_access:int = -1
        index_of_page_to_replace:int = -1

        # Obtiene todos los accesos a las paginas.
        page_accesses:dict[int, list[int]] = parser.page_accesses

        # Revisa cada pagina en los frames, y chequea quien tiene el siguiente acceso mas lejano para hacer el reemplazo.
        for i,page_ in enumerate(frames):
            if (i in OptimalPageReplacementStrategy.current_pointer_pages):
                continue
            if (len(page_accesses[page_.page_id]) < 1):
                index_of_page_to_replace = i
                break
            next_access_of_page:int = page_accesses[page_.page_id][0]
            if (next_access_of_page > farthest_access):
                farthest_access:int = next_access_of_page
                index_of_page_to_replace = i

        replaced_page = frames[index_of_page_to_replace]
        # Actualiza datos de pagina reemplazada
        replaced_page.loaded = False
        replaced_page.memory_address = 0

        # Se remplaza la pagina anterior por la nueva
        frames[index_of_page_to_replace] = page
        page.memory_address = index_of_page_to_replace

        # Se agrega la pagina a este arreglo para garantizar que todos las paginas de un respectivo puntero se carguen a memoria juntas, y no se remplacen unas por otras.
        OptimalPageReplacementStrategy.current_pointer_pages.append(index_of_page_to_replace)

        next_use = parser.page_accesses[replaced_page.page_id][0] if parser.page_accesses[replaced_page.page_id] else "no hay más usos"
        print(f"Reemplazo de página {replaced_page.page_id} porque su próximo uso es en: {next_use}. Página {page.page_id} cargada en el frame {index_of_page_to_replace}.")
        return index_of_page_to_replace
    def mark_page(self, page: Page):
        # Elimina el acceso recien hecho de la lista de accesos proximos. Osea el primer elemento
        # de la lista page_acceses[id de la pagina]
        page_id = page.page_id
        parser.page_accesses[page_id].pop(0)
        return None
    def __str__(self):
        return "Optimal Page Replacement Strategy"
class FIFOPageReplacementStrategy(PageReplacementStrategy):
    def __init__(self):
        self.queue = []

    def replace(self, frames: list[Page], page: Page):
        # Encuentra el primer frame ocupado (FIFO)
        for i, frame in enumerate(frames):
            if frame is not None:
                index_to_replace = i
                break
        else:
            index_to_replace = 0  # fallback

        # Actualiza la cola FIFO
        if len(self.queue) >= len(frames):
            self.queue.pop(0)
        self.queue.append(page)

        replaced_page = frames[index_to_replace]
        replaced_page.loaded = False
        frames[index_to_replace] = page
        return index_to_replace

    def mark_page(self, page: Page):
        pass

class MRUPageReplacementStrategy(PageReplacementStrategy):
    def __init__(self):
        self.last_used_index = None

    def replace(self, frames: list[Page], page: Page):
        # Reemplaza la página más recientemente usada
        if self.last_used_index is not None:
            index_to_replace = self.last_used_index
        else:
            index_to_replace = 0  # fallback

        replaced_page = frames[index_to_replace]
        replaced_page.loaded = False

        # Guarda el indice de la ultima pagina usada.
        self.last_used_index = index_to_replace

        frames[index_to_replace] = page
        return index_to_replace

    def mark_page(self, page: Page):
        pass

class RandomPageReplacementStrategy(PageReplacementStrategy):
    def replace(self, frames: list[Page], page: Page):
        indices = [i for i, frame in enumerate(frames) if frame is not None]
        index_to_replace = random.choice(indices)
        replaced_page = frames[index_to_replace]
        replaced_page.loaded = False
        frames[index_to_replace] = page
        return index_to_replace

    def mark_page(self, page: Page):
        pass
class Memory:
    def __init__(self, replacement_strategy: PageReplacementStrategy, frame_amount:int):
        self.clock: Clock = Clock()
        self.frames: list[Page] = [None] * frame_amount
        self.frames_used: int = 0
        self.replacement_strategy = replacement_strategy

    def get_available_frame(self):
        for i, frame in enumerate(self.frames):
            if frame is None:
                return i
        return -1
    frame_to_use:int = 0
    def load_page(self, page: Page):
        # Si la pagina ya esta en memoria, se registra como hit y no se hace nada
        if (page.loaded):
            self.clock.register_hit()
            print(f"Página {page.page_id} del proceso {page.pid} ya está cargada en memoria (frame {page.memory_address}). Se registra un hit.")
            self.replacement_strategy.mark_page(page)
            return 
        # Valida que hayan paginas disponibles
        if (self.frames_used < len(self.frames)):
            frame_to_use = self.get_available_frame()
            if (frame_to_use == -1):
                print(f"Error finding available page. Could not load page {page.page_id} into RAM")
                return -1
            # Carga la pagina en el frame disponible
            self.frames[frame_to_use] = page
            
            # Actualiza datos de la pagina
            page.load_time += 1

            # Marca la pagina dependiendo del algoritmo de reemplazo usado.
            self.replacement_strategy.mark_page(page)
            
            self.frames_used += 1
            self.clock.register_hit()
            print(f"Página {page.page_id} del proceso {page.pid} cargada en el frame {frame_to_use} de la memoria.")
        else:
            # Hace el reemplazo y devuelve el indice de memoria que se utilizó
            frame_to_use = self.replacement_strategy.replace(self.frames, page)
            
            # Como fue fallo, se suman 5 segundos al contador de tiempo utilizado por la pagina.
            page.load_time += 5
            self.clock.register_fault()
        page.memory_address = frame_to_use
        page.loaded = True
    
    def unload_page(self, page: Page):
        for i, page_ in enumerate(self.frames):
            if (page_ == page):
                del self.frames[i]
                self.frames_used
                page.loaded = False
                page.memory_address = 0
                print(f"Descargando página {page.page_id} del índice {i} de la memoria.")
                return 0
        print(f"La página {page.page_id} no estaba cargada en memoria.")
        return 0
    def __str__(self):
        result = "Estado de la Memoria RAM:\n"
        for i, frame in enumerate(self.frames):
            if frame is not None:
                result += f"  Frame {i}: Página {frame.page_id} (PID: {frame.pid}) | Dirección lógica: {frame.logical_address} | Tiempo de carga: {frame.load_time}\n"
            else:
                result += f"  Frame {i}: [Vacío]\n"
        result += f"Frames usados: {self.frames_used}/{len(self.frames)}\n"
        result += f"Hits: {self.clock.hits} | Fallos: {self.clock.faults} | Tiempo total: {self.clock.total_time}\n"
        return result
class MMU:
    def __init__(self, ram: Memory, memory_map: MemoryMap):
        self.ram: Memory = ram
        self.memory_map: MemoryMap = memory_map

    # Retorna puntero logico (Pointer) con las paginas necesarias para almacenar la cantidad de bytes (size)
    # que se requieren. Todas las paginas pertenecientes al puntero, se cargan en memoria por defecto.
    def new(self, pid: int, size: int):
        pages_needed:int
        if (size == 1024):
            pages_needed = 1
        else:
            pages_needed = (size // 1024) + 1
        pages_created = []
        for i in range(pages_needed):
            page = Page(pid)
            pages_created.append(page)
            self.ram.load_page(page)
        
        # SOLUCION FEA
        # Lista utilizada para garatizar que el puntero completo se cargue a memoria y no se reemplacen paginas del mismo puntero entre si.
        OptimalPageReplacementStrategy.current_pointer_pages = []

        # Se agrega el puntero junto a sus paginas al memory_map
        pointer = Pointer(pid, size, pages_created)
        self.memory_map.add_pointer(pointer)
        return 0
    
    def use(self, ptr: int):
        pointers = self.memory_map.pointers
        if ptr not in pointers:
            return -1
        # Todas las paginas del puntero las carga a memoria

        for page in pointers[ptr].pages:
            self.ram.load_page(page)
        
        # SOLUCION FEA
        # Lista utilizada para garatizar que el puntero completo se cargue a memoria y no se reemplacen paginas del mismo puntero entre si.
        OptimalPageReplacementStrategy.current_pointer_pages = []
        
        return 0
    def delete(self, ptr: int):
        pointers = self.memory_map.pointers
        if ptr not in pointers:
            print(f"Pointer {ptr} doesn't exist.")
            return -1
        
        # Descarga todas las paginas de memoria
        for page in self.memory_map.pointers[ptr].pages:
            self.ram.unload_page(page)
        # Obtiene el PID del proceso dueño del puntero
        process = self.memory_map.pointers[ptr].pid 

        # Borra el puntero del memory map 
        self.memory_map.delete_pointer(ptr)

        # Borra el puntero del diccionario de punteros
        parser.pointer_to_pages.pop(ptr, None)

        # Borra el puntero del diccionario de procesos
        parser.processes_to_pointers[process].remove(ptr)

        # Borra el puntero del diccionario de procesos
        for pid, pointers in parser.processes_to_pointers.items():
            if ptr in pointers:
                pointers.remove(ptr)
                break
        print(f"Pointer {ptr} deleted.")
        return 0
    def kill(self, pid: int):
        # PID no existe, puede que ya haya sido eliminado (kill)
        if pid not in parser.processes_to_pointers:
            print(f"Pid {pid} doesn't exist.")
            return -1
        
        # Elimina cada puntero de memoria
        for ptr in parser.processes_to_pointers[pid]:
            self.delete(ptr)

        # Elimina el proceso del diccionario con todos los procesos activos.
        del parser.processes_to_pointers[pid]

        return 0
    def __str__(self):
        result = "MMU State:\n"
        result += str(self.ram) + "\n"
        result += str(self.memory_map)
        return result
    
def main():
    ram: Memory = Memory(OptimalPageReplacementStrategy(), 100)
    mmu: MMU = MMU(ram, MemoryMap())
    instruction_log: list[Line] = parser.instruction_log

    for instruction in instruction_log:
        match instruction.instruction:
            case "new":
                mmu.new(instruction.arguments[0], instruction.arguments[1])
            case "use":
                mmu.use(instruction.arguments[0])
            case "delete":
                mmu.delete(instruction.arguments[0])
            case "kill":
                mmu.kill(instruction.arguments[0])
            case _:
                print(f"Error: Instruction {instruction.instruction} with arguments: {instruction.arguments} is not valid.")
        print(f"{instruction.instruction} con argumentos: {instruction.arguments}")
        # print("RAM:")
        # for i, frame in enumerate(ram.frames):
        #     if frame is not None:
        #         print(f"  Frame {i}: {frame.page_id}")
        #     else:
        #         print(f"  Frame {i}: [Vacío]")
        input("")
    print(f"Hits: {ram.clock.hits}")
    print(f"Faults: {ram.clock.faults}")
    print(f"Sim-Time: {ram.clock.total_time}s")
    print(f"Thrashing: {ram.clock.thrashing}s")

main()