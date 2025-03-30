import math, random
from panda3d.core import *

collision_count = 0  # Global or external counter to track unique names

def Camera(render, parent, name, radius, color, axis):
    global collision_count  # Access the global counter
    x = 0
    for i in range(100):
        theta = x
        placeholder = render.attachNewNode(name)
        if axis == 'xy-circle':
            placeholder.setPos(radius * math.cos(theta), radius * math.sin(theta), 0.0)
        elif axis == 'yz-circle':
            placeholder.setPos(0.0, radius * math.sin(theta), radius * math.cos(theta))
        elif axis == 'xz-circle':
            placeholder.setPos(radius * math.cos(theta), 0.0, radius * math.sin(theta))
        placeholder.setColor(*color)
        parent.instanceTo(placeholder)
        
        # Generate a unique nickname for the collision node
        collision_nickname = name + '_collision_' + str(collision_count)
        collisioncamera = CollisionNode(collision_nickname)
        collision_count += 1  # Increment the counter for the next collision node

        collisioncamera.addSolid(CollisionSphere(0, 0, 0, 3))
        collisionattach = placeholder.attachNewNode(collisioncamera)
        #collisionattach.show()

        collisioncamera.setFromCollideMask(BitMask32.bit(0))
        collisioncamera.setIntoCollideMask(BitMask32.allOn())
        x = x + 2 * math.pi / 100
        

def Cloud(radius = 1):
    x = 2 * random.random() - 1
    y = 2 * random.random() - 1
    z = 2 * random.random() - 1
    unitVec = Vec3(x, y, z)
    unitVec.normalize()

    return unitVec * radius


def BaseballSeams (step, numSeams, B, F = 1): 
    time = step / float(numSeams) * 2 * math.pi

    F4 = 0
    R = 1

    xxx = math.cos(time) - B * math.cos(3 * time)
    yyy = math.sin(time) + B * math.sin(3 * time)
    zzz = F * math.cos(2 * time) + F4 * math.cos(4 * time)

    rrr = math.sqrt(xxx ** 2 + yyy ** 2 + zzz ** 2)

    x = R * xxx / rrr 
    y = R * yyy / rrr
    z = R * zzz / rrr
    
    return Vec3(x, y, z)