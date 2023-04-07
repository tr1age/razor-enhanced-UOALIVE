## Use this on the lockbox at the Public Rune Library
## box = Items.FindBySerial(0x40017CE0) update the serial to the box you choose to use
## Make sure you are in warmode, this allows you to easily stop the macro by leaving warmode
## At skill level 80 grid size changes from 3 to 4,
##  at 100 it changes to 5,
##    if you are using a new box, it will always start with 3 regardless of skill, until you complete it for the first time, at which point it figures out your skill, and adjusts the grid size
## Not sure how this reacts if someone else is using the same box you are, havent tested whether the instances of the puzzle are shared or unique, so best to find your own box if possible

gridSize = 3

class actionReturn:
    x = 0
    y = 0
    step = 0

    def __init__ (self, x, y, step):
        self.x = x
        self.y = y
        self.step = step

def down(x, y, stepToIncrease):
    Gumps.SendAction(653724266, 3)
    Gumps.WaitForGump(653724266, 2000)
    return actionReturn(x, y + 1, stepToIncrease + 1)

def right(x, y, stepToIncrease):
    Gumps.SendAction(653724266, 2)
    Gumps.WaitForGump(653724266, 2000)
    return actionReturn(x + 1, y, stepToIncrease + 1)

def left(x, y, stepToIncrease):
    Gumps.SendAction(653724266, 4)
    Gumps.WaitForGump(653724266, 2000)
    return actionReturn(x - 1, y, stepToIncrease + 1)

def up(x, y, stepToIncrease):
    Gumps.SendAction(653724266, 1)
    Gumps.WaitForGump(653724266, 2000)
    return actionReturn(x, y - 1, stepToIncrease + 1)

class action:
    name = ''
    fn = down

    def __init__ ( self, name, fn):
        self.name = name
        self.fn = fn

class location:
    x = 1
    y = 1

    def __init__ ( self, x, y):
        self.x = x
        self.y = y

leftAction = action('left', left)
rightAction = action('right', right)
downAction = action('down', down)
upAction = action('up', up)

class specificAction:
    step = 0
    action = leftAction

    def __init__ ( self, step, action):
        self.step = step
        self.action = action

box = Items.FindBySerial(0x40017C5B)



def getActions(currentLocation, pastLocations, previouslyFailedActions):
    actions = []
    if (currentLocation.x < gridSize):
        newLocation = location(currentLocation.x + 1, currentLocation.y)
        ignore = False
        for prevLocation in pastLocations:
            if prevLocation.x == newLocation.x and prevLocation.y == newLocation.y:
                ignore = True
        for previouslyFailedAction in previouslyFailedActions:
            if previouslyFailedAction.action.name == rightAction.name:
                ignore = True
        if ignore == False:
            actions.append(rightAction)
    if (currentLocation.y < gridSize):
        newLocation = location(currentLocation.x, currentLocation.y + 1)
        ignore = False
        for prevLocation in pastLocations:
            if prevLocation.x == newLocation.x and prevLocation.y == newLocation.y:
                ignore = True
        for previouslyFailedAction in previouslyFailedActions:
            if previouslyFailedAction.action.name == downAction.name:
                ignore = True
        if ignore == False:
            actions.append(downAction)
    if (currentLocation.x > 1):
        newLocation = location(currentLocation.x - 1, currentLocation.y)
        ignore = False
        for prevLocation in pastLocations:
            if prevLocation.x == newLocation.x and prevLocation.y == newLocation.y:
                ignore = True
        for previouslyFailedAction in previouslyFailedActions:
            if previouslyFailedAction.action.name == leftAction.name:
                ignore = True
        if ignore == False:
            actions.append(leftAction)
    if (currentLocation.y > 1):
        newLocation = location(currentLocation.x, currentLocation.y - 1)
        ignore = False
        for prevLocation in pastLocations:
            if prevLocation.x == newLocation.x and prevLocation.y == newLocation.y:
                ignore = True
        for previouslyFailedAction in previouslyFailedActions:
            if previouslyFailedAction.action.name == upAction.name:
                ignore = True
        if ignore == False:
            actions.append(upAction)
    return actions

failedActions = []
passActions = []

while Player.WarMode:
    if Timer.Check('remove'):
        Misc.Pause(Timer.Remaining('remove'))

    Player.UseSkill("Remove Trap")
    Timer.Create('remove', 10100)
    Target.WaitForTarget(2000, True)
    Target.TargetExecute(box)
    Gumps.WaitForGump(653724266, 2000)

    currentX = 1
    currentY = 1
    currentStep = 0
    currentLocation = location(currentX,currentY)
    previousLocations = [currentLocation]
    lastAction = specificAction(currentStep, upAction)

    Journal.Clear()
    while not Journal.Search('You fail to disarm the trap and reset it.') and not Journal.Search('You successfully disarm the trap!') and Player.WarMode and Gumps.HasGump():
        highestPassStep = -1
        for passAction in passActions:
            highestPassStep = passAction.step

        while highestPassStep >= currentStep:
            actionToTake = passActions[currentStep]
            Misc.SendMessage("Repeating Pass action going: " + actionToTake.action.name)
            response = actionToTake.action.fn(currentX, currentY, currentStep)
            currentStep = response.step
            currentX = response.x
            currentY = response.y
            lastAction = specificAction(currentStep, actionToTake)
            previousLocations.append(location(currentX, currentY))
            
        failedActionsOnThisStep = []
        for previouslyFailedAction in failedActions:
            if previouslyFailedAction.step == currentStep:
                failedActionsOnThisStep.append(previouslyFailedAction)

        actions = getActions(location(currentX,currentY), previousLocations, failedActionsOnThisStep)
        actionToTake = actions[0]
        response = actionToTake.fn(currentX, currentY, currentStep)
        currentStep = response.step
        currentX = response.x
        currentY = response.y
        lastAction = specificAction(currentStep, actionToTake)

        if not Journal.Search('You fail to disarm the trap and reset it.'):
            Misc.SendMessage("Pass when going: " + lastAction.action.name, False)
            lastAction.step = lastAction.step - 1
            passActions.append(lastAction)
            currentLocation.x = currentX
            currentLocation.y = currentY
            previousLocations.append(location(currentX, currentY))
    
    if Journal.Search('You fail to disarm the trap and reset it.'):
        Misc.SendMessage("Failed to go: " + lastAction.action.name, False)
        lastAction.step = lastAction.step - 1
        failedActions.append(lastAction)
    if Journal.Search('You successfully disarm the trap!'):
        Misc.SendMessage("DONE!!!!!!")
        failedActions = []
        passActions = []
