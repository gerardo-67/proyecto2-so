class Page:
    __page_count = 0
    def __init__(self, pid: int, loaded: bool, logical_add: int, memory_add: int, disk_add: int, load_time: int, mark: int):
        __page_count += 1
        self.page_id = __page_count
        self.pid = pid
        self.loaded = loaded
        self.logical_add = logical_add
        self.memory_add = memory_add
        self.disk_add = disk_add
        self.load_time = load_time
        self.mark = mark
