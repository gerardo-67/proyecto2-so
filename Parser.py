'''
Parser de archivos
Fecha de inicio: 1:00pm 12/5/25
Última modificación: 7:00 pm 20/5/25
'''

import re
import os

symbolTable = {} #Tabla de símbolos que almacena los punteros por proceso
#Symbol table: {1: [1, 3], 2: [2]} el pid 1 tiene dos punteros: 1 y 3

ptrCounter = 1 

def instructionNew(pid, size):
    global ptrCounter
    print(f"NEW: PID {pid} requests {size} bytes")

    #Si el proceso no está en la tabla se agrega 
    if pid not in symbolTable:
        symbolTable[pid] = []
        
    #Asigna un puntero al proceso y lo guarda
    symbolTable[pid].append(ptrCounter)
    print(f"Assigned ptr {ptrCounter} to PID {pid}")
    ptrCounter += 1
    print ("Symbol table:", symbolTable)
    print ("ptrCounter:", ptrCounter)

def instructionUse(ptr):
    print(f"USE: Using ptr {ptr}")

def instructionDelete(ptr):
    print(f"DELETE: Removing ptr {ptr}")
    # Recorre la tabla de símbolos y elimina el puntero
    #for pid in symbolTable:
    #   if ptr in symbolTable[pid]:
    #      del symbolTable[pid][ptr]
    #     break

def instructionKill(pid):
    print(f"KILL: Terminating process {pid}")
    # Elimina el proceso de la tabla de símbolos
    #if pid in symbolTable:
    #   del symbolTable[pid]


#Utiliza expresiones regulares para analizar las lineas y extraer su contenido
def processLine(line):

    print("\n............\nLine:", line) 

    if match := re.match(r'new\((\d+),(\d+)\)', line):
        pid, size = map(int, match.groups()) 
        instructionNew(pid, size)
        
    elif match := re.match(r'use\((\d+)\)', line):
        ptr = int(match.group(1)) #accede al primer grupo capturado de la ER
        instructionUse(ptr)
        
    elif match := re.match(r'delete\((\d+)\)', line):
        ptr = int(match.group(1))
        instructionDelete(ptr)
        
    elif match := re.match(r'kill\((\d+)\)', line):
        pid = int(match.group(1))
        instructionKill(pid)
        
    else:
        print(f"Invalid instruction: {line}")

#Lee el archivo de instrucciones y manda cada línea a la función processLine
def readFile():
    file = r"C:\proyecto2-so\generatedInstructions.txt"
    if not os.path.exists(file):
        print(f"The file does not exist: {file}")
        return
    with open(file, "r") as f:
        for line in f:
            processLine(line)
    print(symbolTable)

readFile()

