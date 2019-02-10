
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task

# Disable module `signal` so that panda3d can run in a thread
Task.signal = None

class Video(ShowBase):

    def __init__(self):
        super().__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.walkPanda, "walkPanda")

        # Load and transform the panda actor.
        self.panda = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.panda.setScale(0.005, 0.005, 0.005)
        self.panda.setPos(0, 0, 0)
        self.panda.reparentTo(render)
        # Loop the panda's animation.
        # self.panda.loop("walk")
        self.acceptOnce("walk", self.panda.loop, ['walk'])
        self.acceptOnce("escape", exit, [0])

    def walkPanda(self, task):
        """walk panda"""
        pos = 10 - 2*task.time
        self.panda.setPos(0, pos, 0)
        return Task.cont

    def spinCameraTask(self, task):
        """move camera"""
        angleDegrees = task.time * 9.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
