import random
from qiskit import QuantumCircuit, execute, Aer
import time
from tkinter import *


probability_array = []
for i in range(100):
    if i < 70:
        probability_array.append(2)
    elif i < 90 and i > 70:
        probability_array.append(1)    # H Gate
    else:
        probability_array.append(3)    # Z gate
random.shuffle(probability_array)


class Temp:
    current_move = "s"


temp = Temp()


def determineCircuit(cell):
    if cell.value > 0:
        initial_state = [1, 0]
        cell.qc.initialize(initial_state, 0)
    else:
        initial_state = [0, 1]
        cell.qc.initialize(initial_state, 0)


def getSign(qc):
    job = execute(qc, Aer.get_backend('qasm_simulator'), shots=1024)
    counts = job.result().get_counts(qc)
    if counts.get('1') > counts.get('0'):
        return "-"
    else:
        return "+"


def passThroughHGate(tile):
    tile.qc.h(0)
    tile.isInSuperposition = not tile.isInSuperposition
    tile.qc.h(0)
    sign = getSign(tile.qc)
    if sign == "+":
        tile.value = abs(tile.value)
    else:
        tile.value = abs(tile.value) * -1


def passThroughZGate(tile):
    tile.qc.z(0)
    sign = getSign(tile.qc)
    if sign == "+":
        tile.value = abs(tile.value)
    else:
        tile.value = abs(tile.value) * -1


class Tile:
    def __init__(self, value):
        self.value = value
        self.qc = QuantumCircuit(1)
        initial_state = [1, 0]   # Define initial_state as |1>
        self.qc.initialize(initial_state, 0)
        self.qc.h(0)
        self.qc.measure_all()
        if self.value != 0:
            sign = getSign(self.qc)
            if sign == "+":
                self.value = 2
            else:
                self.value = -2

    def toString(self):
        if self.value != 0:
            if self.isInSuperposition:
                return "+/-" + str(abs(self.value))
            return str(self.value)
        return ""

    isInSuperposition = False
    isMergable = True
    canMove = True


class HGate:
    def toString(self):
        return self.value
    value = "H"
    isMergable = True


class ZGate:
    def toString(self):
        return self.value
    value = "Z"
    isMergable = True


cells = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

for i in range(4):
    for j in range(4):
        cells[i][j] = Tile(0)


def spawn():
    rand = probability_array[random.randint(0, 99)]
    while True:
        x = random.randint(0, 3)
        y = random.randint(0, 3)
        if cells[x][y].value == 0:
            if rand == 1:
                cells[x][y] = HGate()
            elif rand == 3:
                cells[x][y] = ZGate()
            else:
                cells[x][y] = Tile(-1)
            break


spawn()
spawn()


def canReach(cell, i, j):
    if i < 0 or j < 0 or i > 3 or j > 3:
        return False
    if cells[i][j].value != 0:
        if cells[i][j].value == "H":
            return True
        if cells[i][j].value == "Z":
            return not cell.isInSuperposition
        if cells[i][j].value == cell.value or cells[i][j].value == -cell.value:
            if cells[i][j].isMergable == True and cell.isMergable == True:
                return True
        return False
    return True


def moveUp():
    for i in range(4):
        for j in range(4):
            if cells[i][j].value != 0 and cells[i][j].value != "H" and cells[i][j].value != "Z":
                k = i
                while canReach(cells[k][j], k-1, j) and cells[k][j].canMove:
                    if cells[k-1][j].value == "H":
                        cells[k-1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                        passThroughHGate(cells[k-1][j])
                        cells[k-1][j].isMergable = False
                        cells[k-1][j].canMove = False
                    elif cells[k-1][j].value == "Z":
                        cells[k-1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                        passThroughZGate(cells[k-1][j])
                        cells[k-1][j].isMergable = False
                        cells[k-1][j].canMove = False
                    elif cells[k-1][j].value == cells[k][j].value or cells[k-1][j].value == -cells[k][j].value:
                        value = cells[k-1][j].value
                        cells[k-1][j] = cells[k][j]
                        cells[k-1][j].value = cells[k-1][j].value + value
                        cells[k-1][j].isInSuperposition = False
                        cells[k-1][j].isMergable = False
                        cells[k][j] = Tile(0)
                        determineCircuit(cells[k-1][j])
                    else:
                        cells[k-1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                    k -= 1


def moveDown():
    for i in range(3, -1, -1):
        for j in range(3, -1, -1):
            if cells[i][j].value != 0 and cells[i][j].value != "H" and cells[i][j].value != "Z":
                k = i
                while canReach(cells[k][j], k+1, j) and cells[k][j].canMove:
                    if cells[k+1][j].value == "H":
                        cells[k+1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                        passThroughHGate(cells[k+1][j])
                        cells[k+1][j].isMergable = False
                        cells[k+1][j].canMove = False
                    elif cells[k+1][j].value == "Z":
                        cells[k+1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                        passThroughZGate(cells[k+1][j])
                        cells[k+1][j].isMergable = False
                        cells[k+1][j].canMove = False
                    elif cells[k+1][j].value == cells[k][j].value or cells[k+1][j].value == -cells[k][j].value:
                        value = cells[k+1][j].value
                        cells[k+1][j] = cells[k][j]
                        cells[k+1][j].value = cells[k+1][j].value + value
                        cells[k+1][j].isInSuperposition = False
                        cells[k+1][j].isMergable = False
                        cells[k][j] = Tile(0)
                        determineCircuit(cells[k+1][j])
                    else:
                        cells[k+1][j] = cells[k][j]
                        cells[k][j] = Tile(0)
                    k += 1


def moveLeft():
    for j in range(4):
        for i in range(4):
            if cells[i][j].value != 0 and cells[i][j].value != "H" and cells[i][j].value != "Z":
                k = j
                while canReach(cells[i][k], i, k-1) and cells[i][k].canMove:
                    if cells[i][k-1].value == "H":
                        cells[i][k-1] = cells[i][k]
                        cells[i][k] = Tile(0)
                        passThroughHGate(cells[i][k-1])
                        cells[i][k-1].isMergable = False
                        cells[i][k-1].canMove = False
                    elif cells[i][k-1].value == "Z":
                        cells[i][k-1] = cells[i][k]
                        cells[i][k] = Tile(0)
                        passThroughZGate(cells[i][k-1])
                        cells[i][k-1].isMergable = False
                        cells[i][k-1].canMove = False
                    elif cells[i][k-1].value == cells[i][k].value or cells[i][k-1].value == -cells[i][k].value:
                        value = cells[i][k-1].value
                        cells[i][k-1] = cells[i][k]
                        cells[i][k-1].value = cells[i][k-1].value + value
                        cells[i][k-1].isInSuperposition = False
                        cells[i][k-1].isMergable = False
                        cells[i][k] = Tile(0)
                        determineCircuit(cells[i][k-1])
                    else:
                        cells[i][k-1] = cells[i][k]
                        cells[i][k] = Tile(0)
                    k -= 1


def moveRight():
    for j in range(3, -1, -1):
        for i in range(3, -1, -1):
            if cells[i][j].value != 0 and cells[i][j].value != "H" and cells[i][j].value != "Z":
                k = j
                while canReach(cells[i][k], i, k+1) and cells[i][k].canMove:
                    if cells[i][k+1].value == "H":
                        cells[i][k+1] = cells[i][k]
                        cells[i][k] = Tile(0)
                        passThroughHGate(cells[i][k+1])
                        cells[i][k+1].isMergable = False
                        cells[i][k+1].canMove = False
                    elif cells[i][k+1].value == "Z":
                        cells[i][k+1] = cells[i][k]
                        cells[i][k] = Tile(0)
                        passThroughZGate(cells[i][k+1])
                        cells[i][k+1].isMergable = False
                        cells[i][k+1].canMove = False
                    elif cells[i][k+1].value == cells[i][k].value or cells[i][k+1].value == -cells[i][k].value:
                        value = cells[i][k+1].value
                        cells[i][k+1] = cells[i][k]
                        cells[i][k+1].value = cells[i][k+1].value + value
                        cells[i][k+1].isInSuperposition = False
                        cells[i][k+1].isMergable = False
                        cells[i][k] = Tile(0)
                        determineCircuit(cells[i][k+1])
                    else:
                        cells[i][k+1] = cells[i][k]
                        cells[i][k] = Tile(0)
                    k += 1


def resetMergables():
    for i in range(4):
        for j in range(4):
            cells[i][j].isMergable = True


def resetMoveRestricts():
    for i in range(4):
        for j in range(4):
            cells[i][j].canMove = True


def listener(event):
    temp.current_move = event.keysym
    window.quit()


def checkWin():
    for i in range(4):
        for j in range(4):
            if cells[i][j].value == 256:
                elements = gameArea.winfo_children()
                elements[5].configure(text='You')
                elements[6].configure(text='Win')
                return True
    return False


def checkLose():
    for i in range(4):
        for j in range(4):
            if cells[i][j].value == -256:
                elements = gameArea.winfo_children()
                elements[5].configure(text='You')
                elements[6].configure(text='Lose')
                return True
    return False


def updateWidgets():
    elements = gameArea.winfo_children()
    cell_array = []
    for i in range(4):
        for j in range(4):
            cell_array.append(cells[i][j])
    for i in range(len(elements)):
        if cell_array[i].value != 0:
            elements[i].configure(text=cell_array[i].toString())
            if cell_array[i].value == 2 or cell_array[i].value == -2:
                elements[i].configure(bg='#eee4da')
            elif cell_array[i].value == 4 or cell_array[i].value == -4:
                elements[i].configure(bg='#ede0c8')
            elif cell_array[i].value == 8 or cell_array[i].value == -8:
                elements[i].configure(bg='#f2b179')
            elif cell_array[i].value == 16 or cell_array[i].value == -16:
                elements[i].configure(bg='#f59563')
            elif cell_array[i].value == 32 or cell_array[i].value == -32:
                elements[i].configure(bg='#f67c5f')
            elif cell_array[i].value == 64 or cell_array[i].value == -64:
                elements[i].configure(bg='#edc850')
            elif cell_array[i].value == 128 or cell_array[i].value == -128:
                elements[i].configure(bg='#edc22e')
            elif cell_array[i].value == 256 or cell_array[i].value == -256:
                elements[i].configure(bg='#f65e3b')
            elif cell_array[i].value == "Z":
                elements[i].configure(bg='#8A2BE2')
            elif cell_array[i].value == "H":
                elements[i].configure(bg='#7FFF00')
        else:
            elements[i].configure(text='', bg='#9e948a')


window = Tk()
window.title("2048 Quantum")
window.geometry("512x485+500+50")
window.bind("<KeyPress>", listener)
window.resizable(False, False)
window.focus_force()
gameArea = Frame(window, bg='#92877d')
for i in range(4):
    for j in range(4):
        l = Label(gameArea, text=cells[i][j].toString(), bg='#9e948a',
                  font=('arial', 22, 'bold'), width=6, height=3)
        l.grid(row=i, column=j, padx=7, pady=7)
gameArea.grid()
updateWidgets()
window.mainloop()


def useless(event):
    a = 4


while True:
    current_move = temp.current_move

    if current_move == "Up":
        moveUp()
        spawn()
        time.sleep(0.1)
        current_move = ""
    elif current_move == "Down":
        moveDown()
        spawn()
        time.sleep(0.1)
        current_move = ""
    elif current_move == "Left":
        moveLeft()
        spawn()
        time.sleep(0.1)
        current_move = ""
    elif current_move == "Right":
        moveRight()
        spawn()
        time.sleep(0.1)
        current_move = ""
    resetMergables()
    resetMoveRestricts()
    updateWidgets()
    if checkWin() or checkLose():
        window.bind("<KeyPress>", useless)
    window.mainloop()
