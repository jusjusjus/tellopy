
from math import pi, sin, cos

import numpy as np
from threading import Thread

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.task import Task
import panda3d.core as p3d
from panda3d.core import Point3, NodePath, Texture, GraphicsPipeSelection

from typing import List

# Disable module `signal` so that panda3d can run in a thread
Task.signal = None

class Video(ShowBase):

    fps = 30.0 # frames per second
    dt = 1/fps # seconds per frame
    # Speed of rotations
    rotation_speed: float = 3.0
    # Speed of displacements
    displacement_speed: float = 1.0

    def __init__(self):
        super().__init__(self)
        self.init_scene()
        self.init_physics()

    def init_physics(self):
        self._velocity = np.zeros(3, dtype=np.float32)
        self.angular_velocity = 0.0

    def init_scene(self):

        # we now get buffer thats going to hold the texture of our new scene
        buf = self.win.makeTextureBuffer("hello", *self.win.size)
        # now we have to setup a new scene graph to make this scene
        render = NodePath("new render")
        # this takes care of setting up ther camera properly
        self.camera = self.makeCamera(buf)
        self.camera.reparentTo(render)
        self.camera.setPos(1, 0, 1)
        self.texture = buf.getTexture()
        # Panda contains a built-in viewer that lets you view the results of
        # your render-to-texture operations.  This code configures the viewer.
        self.bufferViewer.setPosition("llcorner")
        self.bufferViewer.setCardSize(1.0, 0.0)
        self.make_offscreen(*self.win.size)
        self.accept("v", self.bufferViewer.toggleEnable)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Panda settings
        self.panda = Actor("models/panda-model", {"walk": "models/panda-walk4"})
        self.panda.setScale(0.005, 0.005, 0.005)
        self.panda.setPos(0, 0, 0)
        self.panda.reparentTo(render)
        self.panda.loop("walk")
        # Create the four lerp intervals needed for the panda to walk back and
        # forth.  Also, create and play the sequence that coordinates the intervals.
        move1 = self.panda.posInterval(13, Point3(0, -10, 0), startPos=Point3(0, 10, 0))
        move2 = self.panda.posInterval(13, Point3(0, 10, 0), startPos=Point3(0, -10, 0))
        turn1 = self.panda.hprInterval(3, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        turn2 = self.panda.hprInterval(3, Point3(0, 0, 0), startHpr=Point3(180, 0, 0))
        self.panda_pacing_seq = Sequence(move1, turn1, move2, turn2, name="panda_pace")
        self.panda_pacing_seq.loop()

        # Camera settings
        self.taskMgr.add(self.move_camera, "move_camera")
        # self.taskMgr.add(self.random_velocity_field, "random_velocity_field")
        self.camera_pos = np.array([0, 0, 2], dtype=np.float32)
        self.camera_rot = np.array([0, 0, 0], dtype=np.float32)
        # Tello input settings
        self.accept("back", self.movement_factory(velocity=[0.0, -self.displacement_speed, 0.0]).start)
        self.accept("forward", self.movement_factory(velocity=[0.0, self.displacement_speed, 0.0]).start)
        self.accept("ccw", self.movement_factory(rotation=self.rotation_speed).start)
        self.accept("cw", self.movement_factory(rotation=-self.rotation_speed).start)
        # keyboard control (h,j,k,l,u,i)
        self.accept("l", self.movement_factory(velocity=[self.displacement_speed, 0.0, 0.0]).start)
        self.accept("h", self.movement_factory(velocity=[-self.displacement_speed, 0.0, 0.0]).start)
        self.accept("j", self.movement_factory(velocity=[0.0, -self.displacement_speed, 0.0]).start)
        self.accept("k", self.movement_factory(velocity=[0.0, self.displacement_speed, 0.0]).start)
        self.accept("u", self.movement_factory(rotation=self.rotation_speed).start)
        self.accept("i", self.movement_factory(rotation=-self.rotation_speed).start)
        # exit on escape
        self.acceptOnce("escape", self.stop, [])

        self.taskMgr.add(self.print_cam, "print_cam")

    def make_offscreen(self, sizex, sizey):
        sizex = p3d.Texture.up_to_power_2(sizex)
        sizey = p3d.Texture.up_to_power_2(sizey)

        if self.win and self.win.get_size()[0] == sizex and self.win.get_size()[1] == sizey:
            # The current window is good, don't waste time making a new one
            return

        use_frame_rate_meter = self.frameRateMeter is not None
        self.setFrameRateMeter(False)

        self.graphicsEngine.remove_all_windows()
        self.win = None
        self.view_region = None

        # First try to create a 24bit buffer to minimize copy times
        fbprops = p3d.FrameBufferProperties()
        fbprops.set_rgba_bits(8, 8, 8, 0)
        fbprops.set_depth_bits(24)
        winprops = p3d.WindowProperties.size(sizex, sizey)
        flags = p3d.GraphicsPipe.BF_refuse_window
        #flags = p3d.GraphicsPipe.BF_require_window
        self.win = self.graphicsEngine.make_output(
            self.pipe,
            'window',
            0,
            fbprops,
            winprops,
            flags
        )

        if self.win is None:
            # Try again with an alpha channel this time (32bit buffer)
            fbprops.set_rgba_bits(8, 8, 8, 8)
            self.win = self.graphicsEngine.make_output(
                self.pipe,
                'window',
                0,
                fbprops,
                winprops,
                flags
            )

        if self.win is None:
            print('Unable to open window')
            sys.exit(-1)

        disp_region = self.win.make_mono_display_region()
        disp_region.set_camera(self.cam)
        disp_region.set_active(True)
        disp_region.set_clear_color_active(True)
        disp_region.set_clear_depth(1.0)
        disp_region.set_clear_depth_active(True)
        self.view_region = disp_region
        self.graphicsEngine.open_windows()

        # self.texture = p3d.Texture()
        self.win.addRenderTexture(self.texture, p3d.GraphicsOutput.RTM_copy_ram)

    def print_cam(self, task):
        # data = bytes(memoryview(self.texture.get_ram_image_as('BGR')))
        try:
            print(self.texture.uncompressRamImage())
            if self.texture.has_ram_image():
                nx = self.texture.get_x_size()
                ny = self.texture.get_y_size()
                data = bytes(memoryview(self.texture.get_ram_image_as('BGR')))
                print(nx, ny, data)
        except AssertionError as err:
            print(err)
        return task.cont

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

    def movement_factory(self, velocity: List[float]=None, rotation: float=0.0):
        """sequence factory changing velocity and rotation speed for 1 sec"""
        velocity = velocity or [0, 0, 0]
        return Sequence(
            Func(self.change_velocity, v=np.array(velocity, dtype=np.float32), r=rotation),
            Wait(1),
            Func(self.change_velocity, v=np.array([0, 0, 0], dtype=np.float32), r=0.0)
        )

    def change_velocity(self, v: np.ndarray=None, r: float=None):
        if v is not None:
            self.velocity = v
        if r is not None:
            self.angular_velocity = r

    @property
    def velocity(self) -> np.ndarray:
        return self._velocity

    @velocity.setter
    def velocity(self, v: np.ndarray):
        """rotate `v` into the camera direction and set as velocity"""
        r = self.camera_rot[0]*np.pi/180
        cos_r, sin_r = np.cos(r), np.sin(r)
        rot = np.array([[cos_r, -sin_r, 0], [sin_r, cos_r, 0], [0, 0, 1]], dtype=np.float32)
        self._velocity = np.dot(rot, v)

    def move_camera_by(self, displacement: np.ndarray=None, rotation: np.ndarray=None):
        if displacement is not None:
            self.camera_pos += displacement
            self.camera.setPos(*self.camera_pos)
        if rotation is not None:
            self.camera_rot += rotation
            self.camera.setHpr(*self.camera_rot)

    def move_camera(self, task):
        """move camera task"""
        self.move_camera_by(
            displacement = self.dt*self.velocity,
            rotation = np.array([2*np.pi*self.dt*self.angular_velocity, 0, 0], dtype=np.float32)
        )
        return Task.cont
