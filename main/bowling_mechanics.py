import math

from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpQuatInterval
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import (
    Point3,
    Vec3,
    NodePath,
    CollisionHandlerEvent,
    CollisionNode,
    CollisionSphere,
    CollisionCapsule,
    CollisionTraverser,
    CollisionHandlerPusher,
    CollisionCapsule, BitMask32, Quat,
)
from direct.interval.IntervalGlobal import (
    Sequence,
    Parallel,
    LerpPosInterval,
    LerpHprInterval,
    LerpPosHprInterval,
)


class BowlingMechanics:
    def __init__(self, game):
        self.game = game
        self.ball_movement_delta = 0.5
        self.setupLane()
        self.pins = []
        self.setupPins()
        self.setupBowlingBall()
        self.setupCollisions()
        self.setupControls()

    def setupLane(self):
        self.lane = self.game.loader.loadModel("../models/bowling-lane.glb")
        self.lane.reparentTo(self.game.render)
        self.lane.setPos(2, 0, 0)

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
                pin = self.game.loader.loadModel("../models/bowling-pin.glb")
                pin.reparentTo(self.game.render)
                pin.setPos(x + pin_x_offset, pin_y_offset, z + pin_z_offset)
                pin.setHpr(180, 0, 0)
                pin.setScale(10)
                self.pins.append(pin)

    def setupBowlingBall(self):
        self.ball = self.game.loader.loadModel("../models/bowling-ball.glb")
        self.ball.reparentTo(self.game.render)
        self.ball.setPos(-10, -1.2, 0)
        self.ball.setScale(5)
    ###
    def setupControls(self):
        # Add key event handlers
        self.game.accept("arrow_left", self.moveBallLeft)
        self.game.accept("arrow_right", self.moveBallRight)

    def moveBallLeft(self):
        current_pos = self.ball.getPos()
        # Limit movement to reasonable bounds
        if current_pos.getZ() > -3:  # Adjust bound as needed
            self.ball.setPos(current_pos.getX(), current_pos.getY(),
                             current_pos.getZ() - self.ball_movement_delta)

    def moveBallRight(self):
        current_pos = self.ball.getPos()
        # Limit movement to reasonable bounds
        if current_pos.getZ() < 3:  # Adjust bound as needed
            self.ball.setPos(current_pos.getX(), current_pos.getY(),
                             current_pos.getZ() + self.ball_movement_delta)
    #

    def setupCollisions(self):
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerEvent()
        self.pinHandler = CollisionHandlerEvent()

        BALL_MASK = BitMask32.bit(0)
        PIN_MASK = BitMask32.bit(1)

        ballCollider = self.ball.attachNewNode(CollisionNode("ball"))
        ballCollider.node().addSolid(CollisionSphere(0, 0, 0, 0.2))

        ballCollider.node().setFromCollideMask(PIN_MASK)  # Ball can collide with pins
        ballCollider.node().setIntoCollideMask(BitMask32(0))  # Ball cannot be collided with

        self.cTrav.addCollider(ballCollider, self.handler)
        ballCollider.show()

        for i, pin in enumerate(self.pins):
            pinCollider = pin.attachNewNode(CollisionNode(f"pinCollider{i}"))
            pinCollider.node().addSolid(CollisionCapsule(-.1,.1,-.23,-.1,.32,-.23,.04))
            pinCollider.node().setFromCollideMask(PIN_MASK)
            pinCollider.node().setIntoCollideMask(BALL_MASK | PIN_MASK)
            self.cTrav.addCollider(pinCollider, self.pinHandler)

            pinCollider.show()

        self.handler.addInPattern("collision-ball-into-pinCollider*")
        self.pinHandler.addInPattern("collision-pinCollider*-into-pinCollider*")
        self.game.accept("collision-ball-into-pinCollider*", self.handleBallPinCollision)
        self.game.accept("collision-pinCollider*-into-pinCollider*", self.handlePinPinCollision)

    def onMouseClick(self):
        print("Mouse Clicked!")
        self.rollBall()

    def rollBall(self):
        print("Rolling the ball")
        # Get current ball position
        start_pos = self.ball.getPos()
        center_pin_pos = self.pins[0].getPos()
        end_x = 20  # Fixed end X coordinate
        # Calculate the ratio to maintain the same angle
        distance_to_travel = end_x - start_pos.getX()
        y_difference = center_pin_pos.getY() - start_pos.getY() - .7

        # Calculate end position maintaining angle to center pin
        ratio = distance_to_travel / (center_pin_pos.getX() - start_pos.getX())
        end_y = start_pos.getY() + (y_difference * ratio)

        rollSequence = Sequence(
            LerpPosInterval(self.ball, 6, Point3(end_x, end_y, 0)),
            name="rollSequence"
        )
        rollSequence.start()

    def handleBallPinCollision(self, entry):
        print("Ball Pin Collision Detected")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()
        normal = entry.getSurfaceNormal(self.game.render)
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))
        self.knockDownPin(self.pins[pin_index], normal)


    def handlePinPinCollision(self, entry):
        print("Pin-Pin Collision Detected!")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()

        print(f"From Pin: {fromNode.getName()}")
        print(f"Into Pin: {intoNode.getName()}")

        normal = entry.getSurfaceNormal(self.game.render)
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))
        self.knockDownPin(self.pins[pin_index], normal)


    def knockDownPin(self, pin, normal):
        rotationNode = self.game.render.attachNewNode("rotationNode")
        pinPos = pin.getPos(self.game.render)

        pinBounds = pin.getTightBounds(self.game.render)
        pinMin = pinBounds[0]
        pinBaseZ = pinMin.getZ()

        # Set rotationNode's position to the base of the pin
        rotationNode.setPos(pinPos.getX(), pinPos.getY(), pinBaseZ)

        offsetZ = pinPos.getZ() - pinBaseZ
        pin.wrtReparentTo(rotationNode)
        pin.setPos(0, 0, offsetZ)

        projectedNormal = Vec3(normal.getX(), 0, normal.getZ())
        if projectedNormal.length() == 0:
            projectedNormal = Vec3(1, 0, 0)
        else:
            projectedNormal.normalize()

        # Compute rotation axis as perpendicular to projected normal in XZ plane
        rotationAxis = Vec3(-projectedNormal.getZ(), 0, projectedNormal.getX())
        rotationAxis.normalize()

        # Create a quaternion representing rotation of 90 degrees about rotationAxis
        quat = Quat()
        quat.setFromAxisAngle(-90, rotationAxis)

        knockDownSequence = Sequence(
            LerpQuatInterval(rotationNode, 0.7, quat),
        )
        knockDownSequence.start()


    def update(self, task):
        self.cTrav.traverse(self.game.render)
        return task.cont
