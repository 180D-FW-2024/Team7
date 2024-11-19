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
    CollisionCapsule, BitMask32,
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
        self.setupLane()
        self.pins = []
        self.setupPins()
        self.setupBowlingBall()
        self.setupCollisions()

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

    def setupCollisions(self):
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerEvent()
        self.pinHandler = CollisionHandlerEvent()

        BALL_MASK = BitMask32.bit(0)
        PIN_MASK = BitMask32.bit(1)

        ballCollider = self.ball.attachNewNode(CollisionNode("ball"))
        ballCollider.node().addSolid(CollisionSphere(0, 0, 0, 0.25))

        ballCollider.node().setFromCollideMask(PIN_MASK)  # Ball can collide with pins
        ballCollider.node().setIntoCollideMask(BitMask32(0))  # Ball cannot be collided with

        self.cTrav.addCollider(ballCollider, self.handler)
        ballCollider.show()

        for i, pin in enumerate(self.pins):
            pinCollider = pin.attachNewNode(CollisionNode(f"pinCollider{i}"))
            pinCollider.node().addSolid(CollisionCapsule(-.1,.1,-.23,-.1,.32,-.23,.05))
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
        rollSequence = Sequence(
            LerpPosInterval(self.ball, 3, Point3(20, -1.2, 0)), name="rollSequence"
        )
        rollSequence.start()

    def handleBallPinCollision(self, entry):
        print("Ball Pin Collision Detected")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()
        print(f"From Node: {fromNode.getName()}")
        print(f"Into Node: {intoNode.getName()}")
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))
        self.knockDownPin(self.pins[pin_index])

    def handlePinPinCollision(self, entry):
        print("Pin-Pin Collision Detected!")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()
        print(f"From Pin: {fromNode.getName()}")
        print(f"Into Pin: {intoNode.getName()}")

        # Get collision point and normal
        contactPoint = entry.getSurfacePoint(self.game.render)
        contactNormal = entry.getSurfaceNormal(self.game.render)
        print(f"Contact Point: {contactPoint}")
        print(f"Contact Normal: {contactNormal}")

        # Get pin indices
        from_pin_index = int(fromNode.getName().replace("pinCollider", ""))
        into_pin_index = int(intoNode.getName().replace("pinCollider", ""))
        # Knock down both pins with dynamic motion
        # self.knockDownPinDynamic(self.pins[from_pin_index], contactNormal)
        # self.knockDownPinDynamic(self.pins[into_pin_index], contactNormal)[2]

    def knockDownPin(self, pin):
        knockDownSequence = Sequence(
            LerpHprInterval(pin, 0.7, (270, 0, 0))
        )
        knockDownSequence.start()

    def update(self, task):
        self.cTrav.traverse(self.game.render)
        return task.cont
