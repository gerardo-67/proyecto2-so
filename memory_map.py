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
        self.thrashing += 5
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
    def get_internal_fragmentation(self):
        # Calcular la fragmentación interna
        total_page_size = (len(self.pages) * 4) * 1024  
        internal_fragmentation = total_page_size - self.size
        return internal_fragmentation
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

oldest_page_index = 0
class PageReplacementStrategy(ABC):
    @abstractmethod
    def replace(self, frames:list[Page], page: Page):
        pass
    @abstractmethod
    def mark_page(self, page: Page):
        pass
class OptimalPageReplacementStrategy(PageReplacementStrategy):
    def replace(self, frames: list[Page]):
        page_accesses: dict[int, list[int]] = parser.page_accesses
        farthest = -1
        index_to_replace = -1
        for i, frame_page in enumerate(frames):
            if frame_page is None:
                return i
            accesses = page_accesses.get(frame_page.page_id, [])
            if not accesses:
                return i
            next_access = accesses[0]
            if next_access > farthest:
                farthest = next_access
                index_to_replace = i
        return index_to_replace
    def mark_page(self, page: Page):
        page_id = page.page_id
        if page_id in parser.page_accesses and parser.page_accesses[page_id]:
            parser.page_accesses[page_id].pop(0)

class RandomPageReplacementStrategy(PageReplacementStrategy):
    def replace(self, frames: list[Page]):
        return random.randint(0, len(frames) - 1)
    def mark_page(self, page: Page):
        pass

class FIFOPageReplacementStrategy(PageReplacementStrategy):
    def __init__(self):
        self.pointer = 0
    def replace(self, frames: list[Page]):
        idx = self.pointer
        self.pointer = (self.pointer + 1) % len(frames)
        return idx
    def mark_page(self, page: Page):
        pass

class MRUPageReplacementStrategy(PageReplacementStrategy):
    def replace(self, frames: list[Page]):
        global last_used_index
        # Si el frame más recientemente usado está vacío, busca el último frame ocupado
        if frames[last_used_index] is None:
            for i in range(len(frames) - 1, -1, -1):
                if frames[i] is not None:
                    last_used_index = i
                    break
        return last_used_index
    def mark_page(self, page: Page):
        pass

class SecondChancePageReplacementStrategy(PageReplacementStrategy):
    def __init__(self, frame_amount=30):
        self.pointer = 0
        self.reference_bits = [0] * frame_amount
    def replace(self, frames: list[Page]):
        n = len(frames)
        while True:
            if frames[self.pointer] is None:
                idx = self.pointer
                break
            if self.reference_bits[self.pointer] == 0:
                idx = self.pointer
                break
            self.reference_bits[self.pointer] = 0
            self.pointer = (self.pointer + 1) % n
        self.pointer = (idx + 1) % n
        return idx
    def mark_page(self, page: Page):
        if page.memory_address is not None:
            self.reference_bits[page.memory_address] = 1


class FIFOPageReplacementStrategy(PageReplacementStrategy):
    def __init__(self):
        self.queue = []  # Cola de índices de frames ocupados en orden de llegada

    def replace(self, frames: list[Page]):
        global oldest_page_index
        if oldest_page_index == (frame_amount-1):
            oldest_page_index = 0
        else:
            oldest_page_index += 1
        return oldest_page_index

    def mark_page(self, page: Page):
        # FIFO no necesita marcar páginas
        pass

last_used_index:int = 0
class MRUPageReplacementStrategy(PageReplacementStrategy):
    def replace(self, frames: list[Page]):
        global last_used_index
        # Si el frame más recientemente usado está vacío, busca el último frame ocupado
        if frames[last_used_index] is None:
            # Busca el frame ocupado más cercano hacia atrás
            for i in range(len(frames) - 1, -1, -1):
                if frames[i] is not None:
                    last_used_index = i
                    break
        index_to_replace = last_used_index
        return index_to_replace

    def mark_page(self, page: Page):
        pass

class SecondChancePageReplacementStrategy(PageReplacementStrategy):
    def __init__(self, frame_amount=100):
        self.pointer = 0  # Apunta al siguiente frame candidato a reemplazo
        self.reference_bits = [0] * frame_amount  # Bit de referencia para cada frame

    def replace(self, frames: list[Page]):
        global disk
        global disk_used_spaces
        n = len(frames)
        while True:
            # Si el frame está vacío, úsalo directamente
            if frames[self.pointer] is None:
                index_to_replace = self.pointer
                break
            # Si el bit de referencia es 0, reemplaza esta página
            if self.reference_bits[self.pointer] == 0:
                index_to_replace = self.pointer
                break
            # Si el bit de referencia es 1, dale una segunda oportunidad
            self.reference_bits[self.pointer] = 0
            self.pointer = (self.pointer + 1) % n
        self.reference_bits[index_to_replace] = 1  # Nuevo o recargado, bit en 1
        self.pointer = (index_to_replace + 1) % n

        return index_to_replace

    def mark_page(self, page: Page):
        # Cuando una página es accedida (hit), pon su bit de referencia en 1
        if page.memory_address is not None:
            self.reference_bits[page.memory_address] = 1
disk:list[Page] = []
disk_used_spaces = 0
class Memory:
    def __init__(self, replacement_strategy: PageReplacementStrategy, frame_amount:int):
        self.clock: Clock = Clock()
        self.frames: list[Page] = [None] * frame_amount
        self.frames_used: int = 0
        self.replacement_strategy = replacement_strategy

    def get_available_disk_space(self):            
        return self.disk_used_spaces
    def get_available_frame(self):
        for i, frame in enumerate(self.frames):
            if frame is None:
                return i
        return -1
    def load_page(self, page: Page):
        global disk_used_spaces
        global last_used_index
        # Si la pagina ya esta en memoria, se registra como hit y no se hace nada
        if page.loaded:
            self.clock.register_hit()
            print(f"Página {page.page_id} del proceso {page.pid} ya está cargada en memoria (frame {page.memory_address}). Se registra un hit.")
            self.replacement_strategy.mark_page(page)
            last_used_index = page.memory_address
            page.load_time += 1
            return

        frame_to_use:int = -1
        # Si hay espacio libre, usa el primer frame disponible
        if self.frames_used < len(self.frames):
            frame_to_use = self.get_available_frame()
            if frame_to_use == -1:
                print(f"Error finding available page. Could not load page {page.page_id} into RAM")
                return -1
            self.frames[frame_to_use] = page
            self.frames_used += 1
            print(f"Página {page.page_id} del proceso {page.pid} cargada en el frame {frame_to_use} de la memoria.")
        else:
            # Selecciona el frame a reemplazar usando la estrategia
            frame_to_use:int = self.replacement_strategy.replace(self.frames)
            replaced_page:Page = self.frames[frame_to_use]
            if replaced_page is not None:
                replaced_page.loaded = False
                replaced_page.memory_address = None
                # Simula el almacenamiento en disco si quieres
                replaced_page.disk_address = disk_used_spaces
                disk_used_spaces += 1
            self.frames[frame_to_use] = page
            print(f"Página {page.page_id} del proceso {page.pid} reemplazó a la página {replaced_page.page_id if replaced_page else 'None'} en el frame {frame_to_use}.")

        # Marca la página según la estrategia
        self.replacement_strategy.mark_page(page)
        page.load_time += 5
        self.clock.register_fault()
        last_used_index = frame_to_use
        page.memory_address = frame_to_use
        page.loaded = True
        page.disk_address = None
    
    def unload_page(self, page: Page):
        for i, page_ in enumerate(self.frames):
            if (page_ == page):
                self.frames[i] = None
                self.frames_used -= 1
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
    
    def get_list_of_pages(self):
        pages = []
        for pointer in self.memory_map.pointers.values():
            pages.extend(pointer.pages)
        return pages
    # Retorna la cantidad de paginas cargadas en memoria
    def get_loaded_amount(self):
        return self.ram.frames_used
    
    # Retorna la cantidad de paginas no cargadas en memoria
    def get_unloaded_amount(self):
        return len(self.get_list_of_pages()) - self.ram.frames_used
    # Retorna la cantidad de KB usados en RAM
    def get_kb_used_in_ram(self):
        return (self.ram.frames_used * 4) 
    # Retorna la cantidad de KB usados en disco
    def get_kb_used_in_disk(self):
        return (self.get_unloaded_amount()) * 4
    # Retorna el porcentaje real de RAM usada
    def real_ram_percentage(self):
        return (self.ram.frames_used / len(self.ram.frames)) * 100
    # Retorna el porcentaje real de disco usado, segun el tamaño de la ram
    def real_disk_percentage(self):
        ram_pages = len(self.ram.frames)
        disk_pages = self.get_unloaded_amount()
        if ram_pages == 0:
            return 0
        return (disk_pages / ram_pages) * 100
    
    def get_internal_fragmentation_in_kb(self):
        total_internal_fragmentation = 0
        for pointer in self.memory_map.pointers.values():
            total_internal_fragmentation += pointer.get_internal_fragmentation()
        return total_internal_fragmentation / 1024  # Convertir a KB
    
    def get_percentage_of_thrashing(self):
        if self.ram.clock.total_time == 0:
            return 0
        return (self.ram.clock.thrashing / self.ram.clock.total_time) * 100
    
    def get__active_process_amount(self):
        return len(parser.processes_to_pointers)
    
    def get_total_process_amount(self):
        return len(self.memory_map.pointers)
    
    def __str__(self):
        result = "MMU State:\n"
        result += str(self.ram) + "\n"
        result += str(self.memory_map)
        return result
    

frame_amount = 30
def main():
    ram: Memory = Memory(RandomPageReplacementStrategy(), frame_amount)
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
        #input("")
    # print("RAM:")
    # for i, frame in enumerate(ram.frames):
    #     if frame is not None:
    #         print(f"  Frame {i}: {frame.page_id}")
    #     else:
    #         print(f"  Frame {i}: [Vacío]")
    #input("")
    print("Pointers actuales en el sistema:")
    for pointer_id, pointer in mmu.memory_map.pointers.items():
        print(f"Pointer ID {pointer_id}:")
        print(pointer)
        print("-" * 40)
    print(f"Hits: {ram.clock.hits}")
    print(f"Faults: {ram.clock.faults}")
    print(f"Sim-Time: {ram.clock.total_time}s")
    print(f"Thrashing: {ram.clock.thrashing}s")
    print(f"Porcentaje de thrashing: {mmu.get_percentage_of_thrashing():.2f}%")
    print(f"Cantidad de procesos activos: {mmu.get__active_process_amount()}")
    print(f"Cantidad de procesos totales: {mmu.get_total_process_amount()}")

    print(f"Cantidad de páginas cargadas en RAM: {mmu.get_loaded_amount()}")
    print(f"Cantidad de páginas no cargadas (en disco): {mmu.get_unloaded_amount()}")
    print(f"KB usados en RAM: {mmu.get_kb_used_in_ram():.2f} KB")
    print(f"KB usados en disco: {mmu.get_kb_used_in_disk():.2f} KB")
    print(f"Porcentaje real de RAM usada: {mmu.real_ram_percentage():.2f}%")
    print(f"Porcentaje real de disco usado: {mmu.real_disk_percentage():.2f}%")
    print(f"Fragmentación interna total: {mmu.get_internal_fragmentation_in_kb()} bytes")

main()