###############################################################################
#                                                                             
#                                twang42.py                                   
#                                                                             
###############################################################################
# Author:  Joao Nuno Carvalho                                                 
# Data:    2020.01.03                                                         
# License: MIT Open Source License                                            
#                                                                             
# Description: A funny, simple and very additive game for the PC, based on
#              Twang32 for the ESP32 that uses a LED strip.
#              This is the Twang 42 game. A very simple and partial re-implementation
# for the PC, of the game Twang32 for the ESP32 microcontroller that uses a LED strip
# and a joystick made with a door Twang spring. See the video of the original
# [TWANG32 LED Strip Game Demo](https://www.youtube.com/watch?v=RXpfa-ZvUMA) I wanted
# to make this game for my daughter and I didn't had a LED strip nor an accelerometer.
# So I made a simple PC version hack during two days of work.
# I wanted to make it in 3D, so that it retained the cool aspect of the perspective
# of the LED strip that you can see in the video. But I wanted to make something fast
# so my daughter could play soon. With that in mind I choose the Python programming
# Language for this project. For the 3D API I taught of PyOpenGL, PyGame and Pandas3D,
# but I have little, rusty, or no experience with those API's, so I asked around and a
# friend suggested that I used the TK API (Tkinter in Python). That is a GUI API that
# has a Canvas 2D Widget with functions to draw polygons and that I could implemented
# the mathematics of the projection of a 3D world in a 2D world using the draw polygons
# functions. I searched around on the internet and found a small example in Stack
# Overflow of a small example code that did that. But that had an error, and that was
# why the person has posted the code. [How to display tkinter polygons on canvas under
# 3D conditions?](https://stackoverflow.com/questions/54043171/how-to-display-tkinter-polygons-on-canvas-under-3d-conditions)
# I have corrected the error and I give the corrected file hear [cube.py](./cube.py).
# This program draws a 3D cube inside TK API and makes it spin in different directions
# depending on the mouse position. It didn't draw the faces of the cube correctly, the
# version I give hear is the some code but with the correction of the Z ordered drawing
# of the polygons and some very small addictions.
# Then I started with this and changed almost everything in the code except the math
# of the projections, I hacked away all the 3D graphic part until it was finished. 
# Then I started on the game partial re-implementation ... I studied all the code, but
# the rendering engine was really different and I wanted to implement a much simpler
# version (partial implementation), so I used an adaptation of the Enemy class from the
# original code and made my own custom version of all the rest. Following the game play
# that I had seen on the original Twang32 video.
#                                                                             
# Dependencies:                                                               
#             Python, Tkinter and Numpy                                       
#                                                                             
# To Run this code do:                                                        
#                      1. python twang42.py                                   
#                                                                             
# For references see the project page at:                                     
#     https://github.com/joaocarvalhoopen?tab=repositories                    
###############################################################################  


from numpy import *
from tkinter import *

# Eulers angles matrixes
def Rx(theta):
    return mat(mat([[1,     0     ,     0      ],
                    [0, cos(theta), -sin(theta)],
                    [0, sin(theta), cos(theta) ]]).round(15))

def Ry(theta):
    return mat(mat([[cos(theta), 0, -sin(theta)],
                    [    0     , 1,     0      ],
                    [sin(theta), 0, cos(theta) ]]).round(15))

def Rz(theta):
    return mat(mat([[cos(theta), -sin(theta), 0],
                    [sin(theta), cos(theta) , 0],
                    [    0     ,     0      , 1]]).round(15))

# Returns a 2d projection matrix, 
def proj2d(p):
    return mat(eye(2,3)*p)

# Tuple into vector
def vector(tuple):
    return transpose(mat(list(tuple)))

# Updates position of the  3D point in function of the x,y,z angles
def position(pts3d, anglex, angley, anglez):
    for i in range(len(pts3d)):
        pts3d[i] = (float((Rx(anglex) * vector(pts3d[i]))[0]),
                    float((Rx(anglex) * vector(pts3d[i]))[1]),
                    float((Rx(anglex) * vector(pts3d[i]))[2]))
        pts3d[i] = (float((Ry(angley) * vector(pts3d[i]))[0]),
                    float((Ry(angley) * vector(pts3d[i]))[1]),
                    float((Ry(angley) * vector(pts3d[i]))[2]))
        pts3d[i] = (float((Rz(anglez) * vector(pts3d[i]))[0]),
                    float((Rz(anglez) * vector(pts3d[i]))[1]),
                    float((Rz(anglez) * vector(pts3d[i]))[2]))

# Makes a projection of the 3d points on the 2d screen
def projected(pts3d):
    pts2d = []
    for i in pts3d:
        pts2d.append((float((proj2d(30+0.75*i[2]) * vector(i))[0]),
                      float((proj2d(30+0.75*i[2]) * vector(i))[1]),
                      i[2] # Z coordinate for Z buffering of faces.
                      ))
    return pts2d

# The funcion that displays the face of the rectangle
def myFace(canvas, faces, points, myColor):
    coordsface = ()
    for j in faces[0]:
        coordsface += (H/2+points[int(j)][0],H/2+points[int(j)][1])
    canvas.create_polygon(coordsface,fill = myColor)

# Major functions, updates position each time interval(delay)
def updateAllPositions(self, H, canvas, objectList, delay, domegax, domegay, domegaz, colorBuf, colorList, gameState):
    global currentKey
    global accumAngleRot
    global recordOn
    global orderedZObjects

    canvas.delete('all')
    
    midPtH = H - H/4
    midPtV = H/2
    minx = midPtH - 20
    maxx = midPtH + 20
    miny = midPtV - 20
    maxy = midPtV + 20

    canvas.create_arc(midPtH - 60, midPtV - 60, midPtH + 60, midPtV + 60, extent = 359, style = ARC,  outline = 'white', fill = 'black')
    canvas.create_line(minx, midPtV, maxx, midPtV, width = 2, fill = 'white')
    canvas.create_line(midPtH, miny, midPtH, maxy, width = 2, fill = 'white')

    x, y = self.winfo_pointerx() - self.winfo_rootx() - midPtH, self.winfo_pointery() - self.winfo_rooty() - midPtV
    if abs(x) >= 60 or abs(y) >= 60:
        x = 0
        y = 0

    joystickTilt   = y
    joystickWobble = x
    gameState[1] = joystickTilt
    gameState[2] = joystickWobble

    # Generate the next game step! 
    nextGameStep(colorBuf, gameState)

    rotStep = 10.0
    processedKey = False

    if currentKey != 'z':
        processedKey = True
        domegax = 0.0
        domegay = 0.0 
        xRotStep = rotStep
        yRotStep = rotStep
        if currentKey == 'a': 
            # Rotates left in the yy's axes.
            domegay = 0.01*(yRotStep)
        if currentKey == 'd':
            # Rotates right in the yy's axes.
            domegay = 0.01*(-yRotStep)
        if currentKey == 'w':
            # Rotates up in the xx's axes.
            domegax = 0.01*(xRotStep)
        if currentKey == 's':
            # Rotates down in the xx's axes.
            domegax = 0.01*(-xRotStep)
        
        if recordOn == True:
            accumAngleRot.append((domegax, domegay))
        if currentKey == 'r':
            # Records the accumulated angle of rotation.
            if recordOn == False:
                recordOn = True
            else:
                recordOn = False
                print(accumAngleRot)

        # Makes the transformation on the points.
        for points, faces in objectList: 
            position(points, domegax, domegay, domegaz)

        currentKey = 'z'  # Resets current key.

    if processedKey == True or len(orderedZObjects) == 0:
        # Order the drawing of the objects/cubes, back cubes are drawn first.
        orderedZObjects.clear() 
        for i in range(len(objectList)):
            z = 0.0
            points = objectList[i][0]
            for j in points:
                z += j[2] 
            orderedZObjects.append((z, i))

        orderedZObjects.sort()    

    for _, i in orderedZObjects:
        points, faces = objectList[i] 
        myFace(canvas, faces, projected(points), colorList[colorBuf[i]])
    
    self.after(delay, updateAllPositions, self, H, canvas, objectList, delay, domegax, domegay, domegaz, colorBuf, colorList, gameState)

def nextGameStep(colorBuf, gameState):
    global stepCounter

    stepCounter += 1

    # DEBUG
    # drawWinGameText( )

    # Draw finish Rectangle.
    colorBuf[0] = BLUE

    level, joystickTilt, joystickWobble, currPos, attackOn, winOn, enemyList, looseOn = gameState

    # Write level Text
    levelText = "Level " + str(level)
    x = H/2 + H/4
    y = H/8
    canvas.create_text(x, y, fill="yellow", font="Times 20 italic bold", text=levelText)

    # Clear the color of the last position, of attack and of enemies.
    colorBuf[mapVirtualToLEDs(currPos)] = GREEN
    
    if attackOn > 0:
        if attackOn > ATTACK_DURATION_OFF:
            drawAttack(colorBuf, currPos, GREEN) # Clear attack.
        attackOn -= 1 

    for enemy in enemyList:
        if enemy.alive() == True:
            colorBuf[mapVirtualToLEDs(enemy.pos)] = GREEN   # Clear enemy. 

    if winOn > 0:
        if level == MAX_LEVEL:
            # Draw Win Game!
            drawWinGameText()           
        winOn -= 1
        joystickTilt   = 0
        joystickWobble = 0
        currPos = INITIAL_PLAYER_POSITION
        if winOn == 1:
            drawWin(colorBuf, GREEN)
            if level < MAX_LEVEL:
                level += 1
            else:
                level = 0
            levels_start(level, enemyList)        
            
    if looseOn > 0:
        looseOn -= 1
        joystickTilt   = 0
        joystickWobble = 0
        currPos = INITIAL_PLAYER_POSITION
        if looseOn == 1:
            drawLoose(colorBuf, GREEN)
        if looseOn == 0:
            levels_start(level, enemyList)

    # Move the level one step.
    level_tick(level, colorBuf, enemyList, gameState, stepCounter)

    # Detects if the player was killed.
    flagLooseGame = False
    for enemy in enemyList:
        if enemy.alive() == True:
            if enemy.pos >= currPos:
                flagLooseGame = True
                break

    if flagLooseGame == True:        
        looseOn = 25
        enemyList.clear()
        joystickTilt   = 0
        joystickWobble = 0
        flagLooseGame = False        

    speed = 0
    if abs(joystickTilt) > 2:
        speed = (joystickTilt / 2.0) 
        currPos = currPos + speed
        if currPos > 1000:
            currPos = 1000
        if currPos < 0.001:
            currPos = 0.001

    if attackOn == 0:
        attackOn = 0
        if abs(joystickWobble) > 40:
            attackOn = ATTACK_DURATION  # Duration of the attack. 

    if winOn == 0:
        winOn = 0
        if mapVirtualToLEDs(currPos) == 0:
           winOn = 25   # Win duration 

    # Draw the player position color Yellow.
    colorBuf[mapVirtualToLEDs(currPos)] = YELLOW

    # Draw enemies.
    for enemy in enemyList:
        if enemy.alive() == True:
            colorBuf[mapVirtualToLEDs(enemy.pos)] = WHITE

    if winOn > 1 and winOn < 23:
        drawWin(colorBuf, YELLOW)
        attackOn = 0
        currPos = INITIAL_PLAYER_POSITION

    if looseOn > 1 and looseOn < 23:
        drawLoose(colorBuf, ORANGE)
        attackOn = 0
        winOn    = 0
        currPos = INITIAL_PLAYER_POSITION

    # minPosTotal = maxPosTotal = currPos 
    if attackOn > ATTACK_DURATION_OFF:
        minPosTotal, maxPosTotal = drawAttack(colorBuf, currPos, LIGHT_BLUE) # Draw attack.

        # Detects if the attack killed enemies.
        enemiesToRemove = []
        for enemy in enemyList:
            if enemy.alive() == True:
                if enemy.pos >= minPosTotal and enemy.pos <= maxPosTotal:
                    enemy.kill()
                    enemiesToRemove.append(enemy)
                    break
        for enemy in enemiesToRemove:
            enemyList.remove(enemy)

    gameState[0] = level
    gameState[3] = currPos
    gameState[4] = attackOn
    gameState[5] = winOn
    gameState[6] = enemyList
    gameState[7] = looseOn

def mapVirtualToLEDs(currPos):
    return int(round((MAX_RECT - 1) * (currPos / 1000)))

def drawAttack(colorBuf, currPos, color):
    pos = mapVirtualToLEDs(currPos)
    minCurrPosAttack = currPos - DEFAULT_ATTACK_WIDTH
    minPos = mapVirtualToLEDs(minCurrPosAttack)
    while(minPos < pos):
        if minPos >= 0:
            colorBuf[minPos] = color
        minPos += 1
    
    maxCurrPosAttack = currPos + DEFAULT_ATTACK_WIDTH
    maxPos = mapVirtualToLEDs(maxCurrPosAttack)
    while(maxPos > pos):
        if maxPos <= MAX_POS:
            colorBuf[maxPos] = color
        maxPos -= 1

    return minCurrPosAttack, maxCurrPosAttack

def drawWin(colorBuf, color):
    for pos in range(0, MAX_POS + 1):
        colorBuf[pos] = color

def drawWinGameText( ):
    # Write level Text
    winText = "Game finished!"
    x = H/2 - H/4
    y = H/8
    canvas.create_text(x, y, fill="BLUE", font="Times 30 italic bold", text=winText)

def drawLoose(colorBuf, color):
    for pos in range(0, MAX_POS + 1, 3):
        colorBuf[pos] = color

def levels_start(level, enemyList):
    if level == 1 or level == 2 or level == 3:
        speed = 0
        if level == 1:
            speed = 5
        if level == 2:
            speed = 20
        if level == 3:
            speed = 40
        enemy = Enemy()
        pos          = 25
        direction    = UP
        wobble       = 0
        enemy.spawn(pos, direction, speed, wobble)
        enemyList.append(enemy)
    
    if level == 4:
        for pos in range(25, 500, 75):
            enemy = Enemy()
            # pos          = 25
            speed        = 5
            direction    = UP
            wobble       = 0
            enemy.spawn(pos, direction, speed, wobble)
            enemyList.append(enemy)

    if level == 5:
        for pos in range(25, 500, 125):
            enemy = Enemy()
            # pos          = 25
            speed        = 10
            direction    = UP
            wobble       = 0
            enemy.spawn(pos, direction, speed, wobble)
            enemyList.append(enemy)

    if level == 6:
        for pos in range(100, 500, 150):
            enemy = Enemy()
            # pos        = 25
            speed        = 10
            direction    = UP
            wobble       = 50   # Has Wobble!
            enemy.spawn(pos, direction, speed, wobble)
            enemyList.append(enemy)

    if level == 7:
        for pos in range(125, 700, 125):
            enemy = Enemy()
            # pos        = 25
            speed        = 10
            direction    = UP
            wobble       = 70   # Has Wobble!
            enemy.spawn(pos, direction, speed, wobble)
            enemyList.append(enemy)


def level_tick(level, colorBuf, enemyList, gameState, stepCounter):
    # level, joystickTilt, joystickWobble, currPos, attackOn, winOn, enemyList, looseOn, winGameOn = gameState

    if level == 0:
        pass
    elif level in [1, 2, 3, 4, 5, 6, 7]:
        for enemy in enemyList:
            enemy.tick( stepCounter )
    
## Rectangle

def pts3DRectangle(xTrans, yTrans, zTrans):
    # Points
    a = ( L/2, L/2, L/2)
    b = ( L/2, L/2,-L/2)
    e = (-L/2, L/2, L/2)
    f = (-L/2, L/2,-L/2)    
    pts3d_v0 = [a,b,e,f]          # Rectangle
    pts3d = []
    for x, y, z in pts3d_v0:
        pts3d.append((x + xTrans, y + yTrans, z + zTrans))
    
    # Faces
    faces = ['0132']
    return pts3d, faces

def keydown(e):
    global currentKey
    if e.char in ('a', 'd', 'w', 's', 'r'):
        currentKey = e.char
        # print(currentKey)

class Enemy:

    def __init__(self):
        self.pos        = 0
        self.wobble     = 0
        self.playerSide = 0
        
        self.direction = 0
        self.speed     = 0
        self._alive    = True
        self.origin    = 0

    def spawn(self, pos, direction, speed, wobble):
        self.pos       = pos
        self.direction = direction        # 0 = UP, 1 = DOWN
        self.wobble    = wobble           # 0 = no, >0 = yes, value is width of wobble
        self.origin    = pos
        self.speed     = speed
        self._alive    = True

    def tick(self, stepCounter):
        if self._alive == True:
            if self.wobble > 0:                
                self.pos = self.origin + (math.sin((stepCounter/10.0)*self.speed)*self.wobble)
            else:
                if self.direction == DOWN:
                    self.pos -= self.speed
                else:
                    self.pos += self.speed
                if self.pos > 1000:
                    self.kill()
                if self.pos <= 0:
                    self.kill()

    def alive(self):
        return self._alive

    def kill(self):
        self._alive = False



GREEN      = 0
YELLOW     = 1
BLUE       = 2
LIGHT_BLUE = 3
RED        = 4
ORANGE     = 5
WHITE      = 6

MAX_RECT = 42  # Max number of Rectangles
MAX_POS = MAX_RECT - 1


# WOBBLE ATTACK
DEFAULT_ATTACK_WIDTH = 100  # Width of the wobble attack, world is 1000 wide
attack_width         = DEFAULT_ATTACK_WIDTH     
ATTACK_DURATION      = 35   # Duration of a wobble attack (steps)
ATTACK_DURATION_OFF  = 20   # Duration of OFF attack (steps), the duration after an attack that you can't attack.

INITIAL_PLAYER_POSITION = 900

# Enemy
UP   = 0
DOWN = 1

# Levels
MAX_LEVEL = 7

# Step counter
stepCounter = 0

## Initial conditions
L = 0.5              # Rectangle side Length
I = 0.5              # Distance between rectangles.
H = 1000
delay = 40

currentKey = 'z'

self = Tk()
canvas = Canvas(self,height = H,width = H,bg = 'gray13')
canvas.pack()

objectList = []
numRect = MAX_RECT
for i in range(0, numRect):
    dif = -(numRect*(L+I))/2.0 + i*(L + I) 
    xTrans = dif
    yTrans = 0.0
    zTrans = 0.0
    objectList.append( pts3DRectangle(xTrans, yTrans, zTrans) ) # Object choice

domegax = 0.0
domegay = 0.0
domegaz = 0.0

# Initial rotation angles
iomegax = 0
iomegay = 0
iomegaz = 0

# Globals
accumAngleRot = []
recordOn = False
orderedZObjects = []

colorList = ['green', 'yellow','blue', '#0099FF', 'red', 'orange','white']
colorBuf = zeros(42, dtype ='int')

# GameState
level          = 0
joystickTilt   = 0  # Stores the angle of the joystick
joystickWobble = 0  # Stores the max amount of acceleration (wobble)
currPos        = INITIAL_PLAYER_POSITION
attackOn       = 0
winOn          = 0
enemyList      = []
looseOn        = 0

# Fill to Jump To directly to level.
jumpToLevel = 7   # 7

if jumpToLevel > 0:
    level = jumpToLevel - 1  # DEBUG
    winOn = 25               # DEBUG

gameState = [ level, joystickTilt, joystickWobble, currPos, attackOn, winOn, enemyList, looseOn ]

intialRotations = [(0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (0.0, 0.1),
                   (0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (0.0, 0.1), (-0.1, 0.0),
                   (-0.1, 0.0), (-0.1, 0.0), (-0.1, 0.0), (-0.1, 0.0), (-0.1, 0.0),
                   (-0.1, 0.0), (0.0, 0.0)]

# Initial rotation on all objects(cubes)
for iomegax, iomegay in intialRotations:
    for obj in objectList:
        points, faces = obj
        position(points, iomegax, iomegay, iomegaz) 

updateAllPositions(self, H, canvas, objectList, delay, domegax, domegay, domegaz, colorBuf, colorList, gameState) # Dynamic rotation


self.bind("<KeyPress>", keydown)

mainloop()
