import itertools
from tables import Table


NUM_FIELDS = 16
COLORS = ['blue', 'green', 'orange', 'yellow', 'white']


class GameException(Exception):
    pass


class Field:
    def __init__(self, no):
        self.no = no  # number
        self.camels = []
        self.modifier = 0

    def clone(self):
        mycopy = Field(self.no)
        mycopy.place([camel.clone() for camel in self.camels])
        mycopy.modifier = self.modifier
        return mycopy

    def pickUp(self, camel):
        index = self.camels.index(camel)
        pile = self.camels[index:]
        for camel in pile:
            camel.tile = None
        self.camels = self.camels[:index]
        return pile

    def place(self, camelPile):
        for camel in camelPile:
            camel.tile = self
        self.camels += camelPile

    def getRank(self, camel):
        return self.camels.index(camel)

    def setModifier(self, modifier):
        if self.modifier != 0:
            raise GameException("Modifier Already Set")
        self.modifier = modifier

    def clearModifier(self):
        self.modifier = 0

    def __str__(self):
        modifier = "%+d" % self.modifier if self.modifier != 0 else "  "
        return "%d[%s]" % (self.no, modifier)


class Camel:
    def __init__(self, name):
        self.name = name
        self.tile = None
        self.dice = None

    def clone(self):
        mycopy = Camel(self.name)
        mycopy.tile = None
        mycopy.dice = None if self.dice is None else int(self.dice)
        return mycopy

    def getScore(self):
        if self.tile is None:
            return 0
        return self.tile.no * 10 + self.tile.getRank(self)

    def __repr__(self):
        return "<camel %s>" % self

    def __str__(self):
        dice = str(self.dice) if self.dice is not None else "-"
        return "%s[%s]" % (self.name, dice)

    def __eq__(self, other):
        if isinstance(other, Camel):
            return self.name == other.name
        return other == self.name

fields = [Field(i) for i in range(NUM_FIELDS)]
camels = [Camel(i) for i in COLORS]

statsAreValid = False

stat_stepOnField = []
stat_winDistribution = {}
count_possibilities = 0


def sumMerge(*iterables):
    sumlist = []
    for i in range(len(iterables[0])):
        s = sum(iterable[i] for iterable in iterables)
        sumlist.append(s)
    return sumlist


def recalculateStats():
    global statsAreValid, stat_winDistribution, stat_stepOnField, count_possibilities, fields, camels
    if statsAreValid:
        # nothing to do
        return
    if not isReady():
        raise GameException("Not ready for calculating probabilities")

    # clear stats
    stat_stepOnField = [0 for i in range(NUM_FIELDS)]
    stat_winDistribution = {color: [0 for i in range(5)] for color in COLORS}

    # iterate through all possibilities and count outcomes
    original_state = [field.clone() for field in fields]
    remaining_colors = [c.name for c in camels if c.dice is None]
    color_order = itertools.permutations(remaining_colors)
    dice_values = itertools.product([1, 2, 3], repeat=len(remaining_colors))
    all_possibilities = itertools.product(color_order, dice_values)
    count_possibilities = 0
    for p in all_possibilities:
        count_possibilities += 1
        # simulate
        statPackage = simulate(p)
        # store results
        stat_stepOnField = sumMerge(stat_stepOnField, statPackage["steps"])
        for camel, dist in statPackage["camels"].items():
            stat_winDistribution[camel] = sumMerge(stat_winDistribution[camel], dist)
        # restore backup
        fields = [field.clone() for field in original_state]
        camels = []
        for f in fields: camels += f.camels

    # set flag
    statsAreValid = True


def simulate(possibility):
    global fields, camels
    steps = [0 for i in range(NUM_FIELDS)]
    places = {color: [0 for i in range(5)] for color in COLORS}
    possibility = zip(*possibility)
    for step in possibility:
        registerDiceThrow(*step)
    camels.sort(key=Camel.getScore)
    for i in range(len(camels)):
        places[camels[i].name][i] += 1
    return {"steps": steps, "camels": places}


def showTopBets():
    pass

def showAllBets():
    pass

def showChances():
    recalculateStats()
    table = Table()
    for color in COLORS:
        table.data.append([color] + stat_winDistribution[color])
    table.addColumn("CAMEL", 0)
    table.addColumn("1st", 1, "%d")
    table.addColumn("2nd", 2, "%d")
    table.addColumn("3rd", 3, "%d")
    table.addColumn("4th", 4, "%d")
    table.addColumn("5th", 5, "%d")
    print("WINNING DISTRIBUTION:")
    print(table.render())
    print("Total possibilities: %d" % count_possibilities)

def getCamelByColor(color):
    return camels[camels.index(color)]


def registerDiceThrow(color, number):
    global statsAreValid
    statsAreValid = False
    number = int(number)
    camel = getCamelByColor(color)

    if camel.dice is not None:
        print("Warning: Already rolled in this turn!")
        return

    if camel.tile is None:
        newpos = number - 1
        pile = [camel]
    else:
        newpos = camel.tile.no + number
        newpos += fields[newpos].modifier
        pile = camel.tile.pickUp(camel)
    fields[newpos].place(pile)

    camel.dice = number

def isRoundEndReached():
    for camel in camels:
        if camel.dice is None:
            return False
    return True

def isReady():
    for camel in camels:
        if camel.tile is None:
            return False
    return True

def reset():
    global statsAreValid
    statsAreValid = False
    fields = [Field(i) for i in range(NUM_FIELDS)]
    camels = [Camel(i) for i in COLORS]

def resetround():
    global statsAreValid
    statsAreValid = False
    print("Round ended. Beginning new round...")
    for camel in camels:
        camel.dice = None
    for field in fields:
        field.clearModifier()

def showBoard():
    for f in fields:
        if f.camels or f.modifier != 0:
            print("%s: %s" % (f, ", ".join(map(str, f.camels))))

def placeBonus(fieldno, sign):
    global statsAreValid
    statsAreValid = False
    no = int(fieldno) - 1
    if no < 0 or no > 15:
        print("Error: invalid field")
        return
    if sign not in '+-':
        print("Error: invalid sign (use + or -)")
        return
    if fields[no].modifier != 0:
        print("Error: this field already has a bonus tile on it")
        return
    fields[no].setModifier(1 if sign == '+' else -1)

def removeBonus(fieldno):
    global statsAreValid
    statsAreValid = False
    no = int(fieldno) - 1
    if no < 0 or no > 15:
        print("Error: invalid field")
        return
    if fields[no].modifier == 0:
        print("Warning: this field has NO bonus tile on it")
        return
    fields[no].clearModifier()



def nl(): print("")

commands = {
    'resetgame': reset,
    'resetround': resetround,
    'roll': registerDiceThrow,
    'state': showBoard,
    'addbonus': placeBonus,
    'rmbonus': removeBonus,
    "bets": showTopBets,
    "allbets": showAllBets,
    "chances": showChances
}

helptext = """
Commands:
    help - show this text

    resetgame - resets the game

    resetround - sets current state as round beginning

    roll COLOR NUMBER - roll the dice

    addbonus FIELD_NO SIGN(+/-) - place a bonus tile

    rmbonus FIELD_NO - remove a bonus tile

    state - show game state

    quit, exit - close this program"""

if __name__ == '__main__':
    # This is the main program (not imported)
    print("Wellcome to CamelUp helper tool")
    nl()
    print("-" * 40)
    nl()
    print(helptext)

    print("Please begin with rolling the dice at least five times")

    while True:
        cmd = input().split(' ')
        if cmd[0] == 'quit' or cmd[0] == 'exit':
            break
        if cmd[0] == 'help':
            print(helptext)
        elif cmd[0] in commands:
            try:
                commands[cmd[0]](*cmd[1:])
            except TypeError as detail:
                print("try again")
                print(detail)
            except GameException as detail:
                print("invalid command at this state")
                print(detail)
        else:
            print("Invalid command")

        if isRoundEndReached():
            resetround()

        showBoard()



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
    camels.sort(key=lambda c: c.pos - len(c.pile) / 10)
    return [camels[-1].name, camels[-2].name, camels[0].name]


def copycamels(source):
    source.sort(key=lambda c: -len(c.pile))
    destination = [Camel(c.name) for c in source]
    for i in range(len(source)):
        base = None
        if not (source[i].baseCamel is None):
            base = \
            [c for c in destination if c.name == source[i].baseCamel.name][0]
        destination[i].setPos(source[i].pos, base)
        destination[i].dice = source[i].dice

    return destination

throws = 0
while 0:
    print("dice result (color number) >>> ", end="")
    color, number = input().split()
    if color == "exit":
        break
    registerDiceThrow(color, int(number))
    throws += 1
    # if throws >= 5:
    #     if throws % 5 == 0:
    #         for c in camels: c.dice = 0
    #     results = {name: [0, 0, 0] for name in COLORS}
    #     camel_backup = copycamels(camels)
    #     remaining_colors = [c.name for c in camels if c.dice == 0]
    #     color_order = itertools.permutations(remaining_colors)
    #     dice_values = itertools.product([1, 2, 3], repeat=len(remaining_colors))
    #     all_possibilities = itertools.product(color_order, dice_values)
    #     total = 0
    #     for p in all_possibilities:
    #         # simulate
    #         win, second, last = simulate(p)
    #         # modify results
    #         results[win][0] += 1
    #         results[second][1] += 1
    #         results[last][2] += 1
    #         total += 1
    #         # restore backup
    #         camels = copycamels(camel_backup)
    #     printState()
    #     print("chances:")
    #     for c in camels:
    #         print(c.name.ljust(8, " "), " ", " ".join(
    #             ("%.2f" % (x * 100 / total)).ljust(8) for x in results[c.name]))

            # kiszámolni a valószínűségeket, és kiírni
            # összes lehetséges dobássorozat elemzése
