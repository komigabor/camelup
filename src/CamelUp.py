import copy

import itertools


class Camel:
    def __init__(self, name):
        self.name = name
        self.pos = 0
        self.dice = 0
        self.pile = []
        self.baseCamel = None
    def setPile(self, pile):
        self.pile = pile
        if not (self.baseCamel is None):
            self.baseCamel.setPile([self] + self.pile)
    def setPos(self, pos, base):
        self.pos = pos
        if not (self.baseCamel is None):
            self.baseCamel.setPile([])
            self.baseCamel = None
        if not (base is None):
            self.baseCamel = base
            self.baseCamel.setPile([self] + self.pile)
        for camel in self.pile:
            camel.pos = pos
    def getTop(self):
        if len(self.pile): return self.pile[-1]
        return self
    def getBottom(self):
        if self.baseCamel is None:
            return self
        return self.baseCamel.getBottom()
    def __str__(self):
        return "%s[%d]" % (self.name, self.dice)

def registerDiceThrow(color, number):
    global camels
    my_camel = [c for c in camels if c.name == color][0]
    newpos = my_camel.pos + number
    already_there = [c for c in camels if c.pos == newpos]
    base = None
    if len(already_there):
        base = already_there[0].getTop()
    my_camel.setPos(newpos, base)
    my_camel.dice = number

colors = ['blue', 'green', 'orange', 'yellow', 'white']
camels = [Camel(i) for i in colors]
camel_backup = None
results = {name:[0,0,0] for name in colors}

throws = 0

def getFieldBottom(pos):
    atpos = [c for c in camels if c.pos == pos]
    if len(atpos):
        return atpos[0].getBottom()
    return None

def printState():
    camelsPrinted = 0
    position = 0
    while camelsPrinted < 5:
        base = getFieldBottom(position)
        if not (base is None):
            print("%d : " % position, *([base] + base.pile))
            camelsPrinted += 1 + len(base.pile)
        # else:
        #     print("%d : -" % position)
        position += 1


def simulate(possibility):
    global camels
    possibility = zip(*possibility)
    for step in possibility: registerDiceThrow(*step)
    camels.sort(key = lambda c : c.pos - len(c.pile) / 10)
    return [camels[-1].name, camels[-2].name, camels[0].name]


def copycamels(source):
    source.sort(key = lambda c : -len(c.pile))
    destination = [Camel(c.name) for c in source]
    for i in range(len(source)):
        base = None
        if not (source[i].baseCamel is None):
            base = [c for c in destination if c.name == source[i].baseCamel.name][0]
        destination[i].setPos(source[i].pos, base)
        destination[i].dice = source[i].dice

    return destination

while 1:
    print("dice result (color number) >>> ", end="")
    color, number = input().split()
    if color == "exit":
        break
    registerDiceThrow(color, int(number))
    throws += 1
    if throws >= 5:
        if throws % 5 == 0:
            for c in camels: c.dice = 0
        results = {name: [0, 0, 0] for name in colors}
        camel_backup = copycamels(camels)
        remaining_colors = [c.name for c in camels if c.dice == 0]
        color_order = itertools.permutations(remaining_colors)
        dice_values = itertools.product([1,2,3], repeat=len(remaining_colors))
        all_possibilities = itertools.product(color_order, dice_values)
        total = 0
        for p in all_possibilities:
            # simulate
            win, second, last = simulate(p)
            # modify results
            results[win][0] += 1
            results[second][1] += 1
            results[last][2] += 1
            total += 1
            # restore backup
            camels = copycamels(camel_backup)
        printState()
        print("chances:")
        for c in camels:
            print(c.name.ljust(8, " "), " ", " ".join(("%.2f" % (x * 100 / total)).ljust(8) for x in results[c.name]))

        # kiszámolni a valószínűségeket, és kiírni
    # összes lehetséges dobássorozat elemzése