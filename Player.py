from CollideObjectBase import SphereCollideObject
from SpaceJamClasses import Missile
from panda3d.core import Loader, NodePath, Vec3
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from panda3d.core import CollisionHandlerEvent
from panda3d.core import CollisionTraverser
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect 
import sys 
# Regex module import for string editing.
import re
from panda3d.core import AudioSound

class PlayerSpaceship(SphereCollideObject):
    def __init__(self, loader: Loader, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, taskMgr, render, numRocks):
        
        collisionpos = Vec3(0.1, 0, 0)
        collisionrad = 1.5
        traverser = CollisionTraverser()
        super(PlayerSpaceship, self).__init__(loader, modelPath, parentNode, nodeName, collisionpos, collisionrad)
        self.missileSound = loader.loadSfx('./Assets/Audio/weaponmortarfire.mp3')
        self.rockSound = loader.loadSfx('./Assets/Audio/objectrespawn2.mp3')  # Load the sound file here
        self.otherObjectSound = loader.loadSfx('./Assets/Audio/weaponbroadsidehitnormal.mp3')  # Load the sound for other objects

        self.modelNode.setScale(scaleVec)
        self.taskMgr = taskMgr
        self.loader = loader
        self.render = render
        self.accept = accept
        self.rockCount = numRocks

        self.reloadTime = .25
        self.missileDistance = 4000
        self.missileBay = 1

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath) 
        self.modelNode.setTexture(tex, 1)
        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.SetKeyBindings()

        self.cntExplode = 0
        self.explodeIntervals = {}
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()

        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
        self.SetParticles()

    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyThrust, 'forward-thrust')
        else:
            self.taskMgr.remove('forward-thrust')

    def ApplyThrust(self, task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont

    def SetKeyBindings(self):
        #All of our key bindings for our spaceship's movement and shooting a missile.
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])
        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])
        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])
        self.accept('arrow_up', self.UpTurn, [1])
        self.accept('arrow_up-up', self.UpTurn, [0])
        self.accept('arrow_down', self.DownTurn, [1])
        self.accept('arrow_down-up', self.DownTurn, [0])
        self.accept('a', self.RollLeft, [1])
        self.accept('a-up', self.RollLeft, [0])
        self.accept('s', self.RollRight, [1])
        self.accept('s-up', self.RollRight, [0])
        self.accept('f', self.Fire)

    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftTurn, 'left-turn')
        else:
            self.taskMgr.remove('left-turn')

    def ApplyLeftTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont

    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightTurn, 'right-turn')
        else:
            self.taskMgr.remove('right-turn')

    def ApplyRightTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont

    def UpTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyUpTurn, 'up-turn')
        else:
            self.taskMgr.remove('up-turn')

    def ApplyUpTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont

    def DownTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyDownTurn, 'down-turn')
        else:
            self.taskMgr.remove('down-turn')

    def ApplyDownTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont

    def RollLeft(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollLeft, 'roll-left')
        else:
            self.taskMgr.remove('roll-left')

    def ApplyRollLeft(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont
    
    def RollRight(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollRight, 'roll-right')
        else:
            self.taskMgr.remove('roll-right')

    def ApplyRollRight(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont

    def Fire(self):
        if self.missileBay > 0:
            travRate = self.missileDistance

            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150

            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront
            
            # Create a missile with a collision node
            currentMissile = Missile(self.loader, './Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)

            # Add the collision node to the traverser
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
            self.taskMgr.add(self.UpdateCollisions, 'update-collisions')

            # Start the missile motion
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos=posVec, fluid=1)
            Missile.Intervals[tag].start()

            if self.missileSound:
                self.missileSound.play()

        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def UpdateCollisions(self, task):
        self.traverser.traverse(self.render)
        return Task.cont
    
    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            if self.missileBay > 1:
                self.missileBay = 1
            print("Reload complete.")
            return Task.done

        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont

    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + ' has reached the end of its fire solution.')
                
                break

        return Task.cont

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName() 
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render))

        tempVar = fromNode.split('_') 
        print("tempVar: " + str(tempVar)) 
        shooter = tempVar[0]
        print("Shooter: " + str(shooter)) 
        tempVar = intoNode.split('-') 
        print("TempVar1: " + str(tempVar)) 
        tempVar = intoNode.split('_') 
        print("TempVar2: " + str(tempVar)) 
        victim = tempVar[0]
        print("Victim: " + str(victim))

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)

        if strippedString in ["BaseballDrone", "CloudDrone", "Planet", "Space Station", "Rock", "x-axis", "y-axis", "z-axis"]: 
            print(victim, ' hit at ', intoPosition)
            self.DestroyObject(victim, intoPosition)

            # Locate and remove the parent node
            victimNode = entry.getIntoNodePath()
            parentNode = victimNode.getParent()
            if not parentNode.isEmpty():  # Ensure the parent exists
                print(f"Removing parent node: {parentNode.getName()}")
                parentNode.removeNode()

        print(shooter + ' is DONE.')
        Missile.Intervals[shooter].finish()
    
    def DestroyObject(self, hitID, hitPosition):
        # Unity also has a find method, yet it is very inefficient if used anywhere but at the beginning of the program. 
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', hitID)

        if strippedString == "Rock":
            if self.rockSound:
                self.rockSound.play()
            self.rockCount -= 1
            print(f"Rock destroyed! Remaining rocks: {self.rockCount}")

            # Check if all rocks are destroyed
            if self.rockCount == 0:
                print("Congratulations! You've destroyed all the rocks! Thanks for playing!")
                sys.exit()

        else:
            if self.otherObjectSound:
                self.otherObjectSound.play()

        # Start the explosion.
        self.explodeNode.setPos(hitPosition)
        self.Explode()

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start() 

    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Part-Efx/default_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
