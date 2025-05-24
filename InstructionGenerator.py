'''
Generador de Instrucciones
Fecha de inicio: 7:00 pm 20/5/25
Última modificación: 10:00 pm 20/5/25

Dado un número de procesos, operaciones y una semilla, genera 
una secuencia de instrucciones new(pid,size), use(ptr), delete(ptr) y kill(pid). 
Almacena todo en generatedInstructions.txt
'''

import random

def initSeed(seed: int):
    # Inicializa el generador de números aleatorios con la semilla dada
    random.seed(seed)

def generateInstructions(numProcesses: int,
                         numOperations: int,
                         seed: int,
                         maxSize: int = 100) -> tuple[list[str], dict[int, list[int]]]:
    initSeed(seed)
    #Tabla de símbolos: mapea PID a lista de punteros asignados
    symbolTable = {pid: [] for pid in range(1, numProcesses + 1)}
    #Procesos vivos
    alivePids = list(symbolTable.keys())
    #Punteros que aún no han sido eliminados
    activePtrs = []
    #Contador para asignar identificadores de puntero
    ptrCounter = 1
    #Lista donde se acumulan todas las instrucciones
    instructions = []
    P, N = numProcesses, numOperations

    #Tamaños válidos para los news (>=50 y terminan en 0 o 5)
    validSizes = [i for i in range(50, maxSize + 1) if i % 5 == 0]

    #Un 'new' por cada proceso con tamaño aleatorio válido
    for pid in alivePids.copy():
        size = random.choice(validSizes)
        instructions.append(f"new({pid},{size})")
        symbolTable[pid].append(ptrCounter)
        activePtrs.append(ptrCounter)
        ptrCounter += 1

    #Determina posiciones para 'kill': P-1 aleatorias y la última forzada
    killSlots = random.sample(range(P, N - 1), P - 1)
    killSlots.append(N - 1)
    killSlots.sort()
    #Asigna cada 'kill' a un PID distinto en orden aleatorio
    pidsShuffled = alivePids.copy()
    random.shuffle(pidsShuffled)
    killAt = dict(zip(killSlots, pidsShuffled))

    #Genera las instrucciones restantes
    for i in range(P, N):
        if i in killAt:
            #Operación 'kill' para un proceso que aún vive
            pid = killAt[i]
            instructions.append(f"kill({pid})")
            alivePids.remove(pid)
            #Elimina punteros asociados a ese PID de la lista activa
            activePtrs = [p for p in activePtrs if p not in symbolTable[pid]]
        else:
            #Selecciona operaciones válidas según estado actual
            ops = []
            if alivePids:
                ops.append("new")
            if activePtrs:
                ops += ["use", "delete"]
            op = random.choice(ops)

            if op == "new":
                #Crea nuevo puntero para un proceso vivo
                pid = random.choice(alivePids)
                size = random.choice(validSizes)
                instructions.append(f"new({pid},{size})")
                symbolTable[pid].append(ptrCounter)
                activePtrs.append(ptrCounter)
                ptrCounter += 1

            elif op == "use":
                #Usa un puntero existente
                ptr = random.choice(activePtrs)
                instructions.append(f"use({ptr})")

            else:  #delete
                #Elimina un puntero de la tabla
                ptr = random.choice(activePtrs)
                instructions.append(f"delete({ptr})")
                activePtrs.remove(ptr)

    #Guarda todas las instrucciones en un archivo texto
    with open("generatedInstructions.txt", "w") as f:
        for instr in instructions:
            f.write(instr + "\n")

    return instructions, symbolTable

if __name__ == "__main__":
    numProcesses = 100
    numOperations = 2000
    seed = 123
    max_size = 32768

    instructions, symbolTable = generateInstructions(
        numProcesses, numOperations, seed, max_size
    )

    for line in instructions:
        print(line)
    print("symbolTable =", symbolTable)
