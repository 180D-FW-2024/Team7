#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import loadPrcFile, TransparencyAttrib
import simplepbr
from bowling_mechanics import BowlingMechanics

loadPrcFile("../config/conf.prc")


class BowlingGame(ShowBase):
    def __init__(self):
        super().__init__()
        simplepbr.init()

        # setup camera
        self.disable_mouse()
        self.camera.setPos(-30, -10, 0)
        self.camera.setHpr(-75, 0, 90)

        # Set up crosshairs
        crosshairs = OnscreenImage(
            image="../images/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        self.bowling_mechanics = BowlingMechanics(self)
        self.accept("mouse1", self.bowling_mechanics.onMouseClick)
        self.taskMgr.add(self.bowling_mechanics.update, "updateTask")

app = BowlingGame()
app.run()
