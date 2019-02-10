
from math import pi, sin, cos

import numpy as np
from threading import Thread

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.task import Task

# Disable module `signal` so that panda3d can run in a thread
Task.signal = None

class Video(ShowBase):

    dt = 0.01
    angular_var = 0.01
    velocity_var = 0.02

    def __init__(self):
        super().__init__(self)
        self.init_scene()
        self.init_physics()

    def init_physics(self):
        self.velocity = np.zeros(3, dtype=np.float32)
        self.angular_velocity = 0.0

    def init_scene(self):
        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Add the spinCameraTask procedure to the task manager.
        # self.taskMgr.add(self.spinCameraTask, "spin camera")

        # Panda settings
        self.panda = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.panda.setScale(0.005, 0.005, 0.005)
        self.panda.setPos(0, 0, 0)
        self.panda.reparentTo(render)
        # Loop the panda's animation.
        self.taskMgr.add(self.walkPanda, "walkPanda")

        # Camera settings
        self.taskMgr.add(self.random_camera_movement, "random_camera_movement")
        # self.taskMgr.add(self.random_velocity_field, "random_velocity_field")
        self.camera_pos = np.array([0, 0, 2.0], dtype=np.float32)
        self.camera_rot = np.array([0, 0, 0], dtype=np.float32)

        # control settings
        self.panda.loop("walk")
        self.acceptOnce("escape", self.stop, [])

        self.accept("l", self.movement_factory(velocity=[1, 0, 0]).start)
        self.accept("h", self.movement_factory(velocity=[-1, 0, 0]).start)
        self.accept("back", self.movement_factory(velocity=[0, -1, 0]).start)
        self.accept("forward", self.movement_factory(velocity=[0, 1, 0]).start)
        self.accept("ccw", self.movement_factory(rotation=5.0).start)
        self.accept("cw", self.movement_factory(rotation=-5.0).start)

    def stop(self):
        if hasattr(self, '_thread'):
            # Video was started in a thread
            self._thread.join(timeout=1.0)
            self._thread.close()
        else:
            exit(0)

    @classmethod
    def run_in_thread(cls):
        instance = cls()
        instance._thread = Thread(target=instance.run)
        instance._thread.deamon = True
        instance._thread.start()
        return instance

    def walkPanda(self, task):
        """walk panda"""
        pos = 10 - 2*task.time
        self.panda.setPos(0, pos, 0)
        return Task.cont

    def movement_factory(self, velocity=[0.0, 0.0, 0.0], rotation=0.0):
        return Sequence(
            Func(self.change_velocity, v=np.array(velocity, dtype=np.float32), r=rotation),
            Wait(1),
            Func(self.change_velocity, v=np.array([0, 0, 0], dtype=np.float32), r=0.0)
        )

    def change_velocity(self, v=None, r=None):
        if v is not None: self.velocity = v
        if r is not None: self.angular_velocity = r

    def move_camera_by(self, displacement: np.ndarray=None, rotation: np.ndarray=None):
        if displacement is not None:
            self.camera_pos += displacement
            self.camera.setPos(*self.camera_pos)
        if rotation is not None:
            self.camera_rot += rotation
            self.camera.setHpr(*self.camera_rot)

    def random_velocity_field(self, task):
        """Random walk in displacement and angular velocity"""
        fluct = np.random.randn(4)
        self.velocity = self.velocity + self.velocity_var*fluct[:3]
        self.angular_velocity = self.angular_velocity + \
                self.angular_var*fluct[3]
        return Task.cont

    def random_camera_movement(self, task):
        """move camera randomly"""
        self.move_camera_by(
            self.dt*self.velocity,
            np.array([2*np.pi*self.dt*self.angular_velocity, 0, 0], dtype=np.float32)
        )
        return Task.cont

    def spinCameraTask(self, task):
        """move camera"""
        angleDegrees = task.time * 9.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
