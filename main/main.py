#!/usr/bin/env python
from panda3d.core import loadPrcFile, TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
import simplepbr

loadPrcFile("../config/conf.prc")


class bowlingGame(ShowBase):
    def __init__(self):
        super().__init__()
        simplepbr.init()

        # set up lanes
        self.lane = self.loader.loadModel("../models/bowling-lane.glb")
        self.lane.reparentTo(self.render)
        self.lane.setPos(2, 0, 0)

        # baseline camera location
        self.disable_mouse()
        self.camera.setPos(-30, -10, 0)
        self.camera.setHpr(-75, 0, 90)

        # set up bowling pins
        self.setupPins()

        # crosshairs if necessary
        # base.setBackgroundColor(.3,.1,0)
        crosshairs = OnscreenImage(
            image="../images/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

    def setupPins(self):
        pin_spacing = 1.9
        pin_x_offset, pin_y_offset, pin_z_offset = 7, -0.1, 2.5
        row_positions = [
            [(0, 0)],
            [(pin_spacing, 0.5 * pin_spacing), (pin_spacing, -0.5 * pin_spacing)],
            [
                (2 * pin_spacing, pin_spacing),
                (2 * pin_spacing, 0),
                (2 * pin_spacing, -pin_spacing),
            ],
            [
                (3 * pin_spacing, 1.5 * pin_spacing),
                (3 * pin_spacing, 0.5 * pin_spacing),
                (3 * pin_spacing, -0.5 * pin_spacing),
                (3 * pin_spacing, -1.5 * pin_spacing),
            ],
        ]

        for i, row in enumerate(row_positions):
            for j, (x, z) in enumerate(row):
                pin = self.loader.loadModel("../models/bowling-pin.glb")
                pin.reparentTo(self.render)
                pin.setPos(x + pin_x_offset, pin_y_offset, z + pin_z_offset)
                pin.setHpr(180, 0, 0)
                pin.setScale(10)


app = bowlingGame()
app.run()
