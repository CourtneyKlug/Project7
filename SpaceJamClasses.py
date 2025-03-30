from direct.showbase.ShowBase import ShowBase
from CollideObjectBase import *
from direct.task import Task
from direct.task.Task import TaskManager
import DefensePaths as defensePaths
from panda3d.core import *
    
class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 0.9)
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale (scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)
    
    
class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale (scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)

        self.angle = 0

    def rotate(self, task):
        # Increment the angle
        self.angle += globalClock.getDt() * 20  # 20 degrees per second
        # Apply the rotation
        self.modelNode.setH(self.angle)
        return Task.cont

class Rock(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Rock, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        # Adjust the collider's radius
        new_radius_top = 1
        new_radius_bottom = 11.7
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, new_radius_top, 1, -1, -5, new_radius_bottom)
        
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)

class Drone(SphereCollideObject):
    # How many drones have been spawned.
    droneCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 2.5)
        self.modelNode.setPos(posVec) 
        self.modelNode.setScale (scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)


class CameraDefense:
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        # Load the parent model and texture for the camera defense system
        self.modelNode = parentNode.attachNewNode(nodeName)
        self.model = loader.loadModel(modelPath)
        self.model.reparentTo(self.modelNode)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)

        # Apply texture to the model
        texture = loader.loadTexture(texPath)
        self.model.setTexture(texture, 1)

        # Set up a collision sphere for the object
        colliderScale = 0.1  # Adjust collider scaling as necessary
        collisionNode = CollisionNode(f"{nodeName}_collision")
        collisionNode.addSolid(CollisionSphere(0, 0, 0, 1))  # Base radius of 1
        self.collisionNodePath = self.modelNode.attachNewNode(collisionNode)
        self.collisionNodePath.setScale(colliderScale)

        # Initialize defense paths
        self.setupDefensePaths(loader, parentNode)

    def setupDefensePaths(self, loader, render):
        # Create defense paths around the parent model node
        from DefensePaths import Camera
        Camera(render, self.modelNode, 'x-axis', 150, (255, 0, 0, 1.0), 'xy-circle')
        Camera(render, self.modelNode, 'y-axis', 115, (0, 255, 0, 1.0), 'yz-circle')
        Camera(render, self.modelNode, 'z-axis', 135, (0, 0, 255, 1.0), 'xz-circle')

    def updateCircleScale(self, newScale):
        # Update the visual scale of the model node
        self.modelNode.setScale(newScale)

        # Update the collision node separately to maintain its scale independently
        fixedCollisionScale = 0.1  # Use a fixed size you're comfortable with
        self.collisionNodePath.setScale(fixedCollisionScale)

class Orbiter(SphereCollideObject):
    numOrbits = 0
    velocity = 0.005
    cloudTimer = 240

    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, 
    centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self,).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.2)
        self.taskMgr = taskMgr 
        self.orbitType = orbitType 
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1) 
        self.orbitObject = centralObject 
        self.orbitRadius = orbitRadius
        self.staringAt = staringAt 
        Orbiter.numOrbits += 1

        self.cloudClock = 0
        
        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits) 
        taskMgr.add(self.Orbit, self.taskFlag)


    def Orbit(self, task):
            if self.orbitType == "MLB":
                positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0) 
                self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
            
            elif self.orbitType == "Cloud":
                if self.cloudClock < Orbiter.cloudTimer:
                    self.cloudClock += 1
                else:
                    self.cloudClock = 0
                    positionVec = defensePaths.Cloud()
                    self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
            
            self.modelNode.lookAt(self.staringAt.modelNode)
            return task.cont

class Missile(SphereCollideObject):
    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        # Missile.cNodes[nodeName].show()
        print("Fire torpedo #" + str(Missile.missileCount))
    