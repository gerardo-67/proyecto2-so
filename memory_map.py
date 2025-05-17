class Clock():
    def __init__(self):
        self.total_time = 0
        self.thrashing = 0
    def register_hit(self):
        self.total_time += 1
    def register_fault(self):
        self.total_time += 5
        self.thrashing =+ 5
    
class Page:
    __page_count = 0
    def __init__(self, pid: int):
        self.pid = pid
        self.page_id = self.__page_count
        self.logical_address = self.__page_count
        self.__page_count += 1
        self.loaded = True # Por defecto cuando se crea una pagina, está en memoria.
        self.memory_address = None # Cuando se carga la pagina en memoria se asigna el marco respectivo.
        self.disk_address = None 
        self.load_time = 0 # No se aun.
        self.mark = 0 # Aun no se ha implementado.

class Pointer:
    def __init__(self, pid: int, size: int, pages: list[Page]):
        self.pid: int = pid
        self.size: int = size

        self.pages: list[Page] = pages



class MemoryMap:
    def __init__(self):
        __pointer_count = 0
        self.pointers: dict[int, Pointer] = {}
    def add_pointer(self, pointer: Pointer):
        self.pointers[self.__pointer_count] = pointer
        self.pointer_count =+ 1
        return 0
    def delete_pointer(self, pointer_id: int):
        del self.pointers[pointer_id]
        return 0

class Memory:
    def __init__(self):
        self.clock: Clock = Clock()
        self.frames: list[Page] = [None] * 100
        self.frames_used: int = 0

    def get_available_frame(self):
        for i, frame in enumerate(self.frames):
            if frame is None:
                return i
        return -1
    def load_page(self, page: Page):
        if (not page.loaded):
            return 
        # Valida que hayan paginas disponibles
        if (self.frames_used < 100):
            available_frame = self.get_available_frame()
            if (available_frame == -1):
                print(f"Error finding available page. Could not load page {page.page_id} into RAM")
                return -1
            # Carga la pagina en el frame disponible
            self.frames[available_frame] = page
            
            # Actualiza datos de la pagina
            page.loaded = True
            page.memory_address = available_frame
            
            self.frames_used =+ 1
            self.clock.register_hit()
        else:
            # FALTA
            print("Falta de implementar, aqui sucede el page swap con el algoritmo seleccionado.")
    
    def unload_page(self, page: Page):
        return None

class MMU:
    def __init__(self):
        self.ram = Memory()
        self.memory_map = MemoryMap()

    # Retorna puntero logico (Pointer) con las paginas necesarias para almacenar la cantidad de bytes (size)
    # que se requieren. Todas las paginas pertenecientes al puntero, se cargan en memoria por defecto.
    def new(self, pid: int, size: int):
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
        for page in pointers[ptr]:
            self.ram.load_page(page)
        return 0
    def delete(self, ptr: int):
        pointers = self.memory_map.pointers
        if ptr not in pointers:
            return -1
        
        # Descarga todas las paginas de memoria
        for page in self.memory_map.pointers[ptr]:
            self.ram.unload(page)
        # Borra el puntero del memory map 
        self.memory_map.delete_pointer(ptr)
        return 0
        

        



    