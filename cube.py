# Corrected version of the post:
#     [How to display tkinter polygons on canvas under
#      3D conditions?](https://stackoverflow.com/questions/54043171/how-to-display-tkinter-polygons-on-canvas-under-3d-conditions)
#

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

# Displays dots
def dots(canvas, points):
    for i in points:
        canvas.create_oval(H/2+5+i[0],H/2+5+i[1],H/2-5+i[0],H/2-5+i[1],fill = 'white')

# Displays vertices
def connect(canvas, vertices, points):
    for i in vertices:
        canvas.create_line(H/2+points[int(i[0])][0],H/2+points[int(i[0])][1],H/2+points[int(i[1])][0],H/2+points[int(i[1])][1],width = 2,fill = 'white')

# What I should modify, I guess: it's the funcion that displays the faces of the object
def face(canvas, faces, points, colors):
    orderedZFaces = [] 
    for i in range(len(faces)):
        z = 0.0
        for j in faces[i]:
            z += points[int(j)][2] 
        orderedZFaces.append((z, i))

    orderedZFaces.sort()    

    for _, i in orderedZFaces:
        coordsface = ()
        for j in faces[i]:
            coordsface += (H/2+points[int(j)][0],H/2+points[int(j)][1])
        canvas.create_polygon(coordsface,fill = colors[i])

    #for i in range(len(faces)):
    #    coordsface = ()
    #    for j in faces[i]:
    #        coordsface += (H/2+points[int(j)][0],H/2+points[int(j)][1])
    #    canvas.create_polygon(coordsface,fill = colors[i])

# Major functions, updates position each time interval(delay)
def updateposition(self, H, canvas, points, vertices, faces, colourFaces, delay, domegax, domegay, domegaz):
    canvas.delete('all')
    y,x = self.winfo_pointerx() - self.winfo_rootx() - H/2, self.winfo_pointery() - self.winfo_rooty() - H/2
    if abs(x) >= H/2 or abs(y) >= H/2: x,y = 0,0
    domegax -= 0.00001*(x)
    domegay -= 0.00001*(y)
    position(points, domegax, domegay, domegaz)
    if affpts == 'y':
        dots(canvas, projected(points))
    if affart == 'y':
        connect(canvas, vertices, projected(points))
    if afffac == 'y':
        face(canvas, faces, projected(points), colourFaces)
    self.after(delay, updateposition, self, H, canvas, points, vertices, faces, colourFaces, delay, domegax, domegay, domegaz)

## Cube

def pts3Dcube():
    # Points
    a = ( L/2, L/2, L/2)
    b = ( L/2, L/2,-L/2)
    c = ( L/2,-L/2, L/2)
    d = ( L/2,-L/2,-L/2)
    e = (-L/2, L/2, L/2)
    f = (-L/2, L/2,-L/2)
    g = (-L/2,-L/2, L/2)
    h = (-L/2,-L/2,-L/2)
    pts3d = [a,b,c,d,e,f,g,h]
    # Vertices
    aretes = []
    for i in [0,2,4,6]:
        aretes.append(str(i)+str(i+1))
    for i in [0,1,4,5]:
        aretes.append(str(i)+str(i+2))
    for i in [0,1,2,3]:
        aretes.append(str(i)+str(i+4))
    # Faces
    faces = ['0132','4576','0154','2376','1375','0264']
    colourFaces = ['green','red','yellow','blue','orange','white']
    return pts3d, aretes, faces, colourFaces

## Initial conditions
L = 5
H = 600
delay = 5

delay = 40

self = Tk()
canvas = Canvas(self,height = H,width = H,bg = 'gray13')
canvas.pack()

objet = pts3Dcube() # Object choice

domegax = 0.0
domegay = 0.0
domegaz = 0.0

# Initial rotation angles
iomegax = 0
iomegay = 0
iomegaz = 0

# Displaying points, vertices, faces or not
affpts = 'y'
affart = 'y'
afffac = 'y'

position(objet[0], iomegax, iomegay, iomegaz) # Initial rotation
updateposition(self, H, canvas, objet[0], objet[1], objet[2], objet[3], delay, domegax, domegay, domegaz) # Dynamic rotation

mainloop()

