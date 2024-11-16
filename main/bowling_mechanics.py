from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import (
    Point3,
    CollisionHandlerEvent,
    CollisionNode,
    CollisionSphere,
    CollisionTraverser,
    CollisionHandlerPusher,
    BitMask32,
    GeomNode,
)
from direct.interval.IntervalGlobal import (
    Sequence,
    Parallel,
    LerpPosInterval,
    LerpHprInterval,
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
        self.cTrav.showCollisions(self.game.render)
        ballCollider = self.ball.attachNewNode(CollisionNode("ball"))
        ballCollider.node().addSolid(CollisionSphere(0, 0, 0, 0.25))
        ballCollider.node().setFromCollideMask(BitMask32.bit(0))
        ballCollider.node().setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(ballCollider, self.handler)
        ballCollider.show()

        offset_x, offset_y, offset_z = -0.1, 0.15, -0.237
        for i, pin in enumerate(self.pins):
            pinCollider = pin.attachNewNode(CollisionNode(f"pinCollider{i}"))
            pinCollider.node().addSolid(
                CollisionSphere(offset_x, offset_y, offset_z, 0.07)
            )
            pinCollider.node().setFromCollideMask(BitMask32.allOff())
            pinCollider.node().setIntoCollideMask(BitMask32.bit(0))
            pinCollider.show()

        self.handler.addInPattern("collision-ball-into-pinCollider*")
        self.game.accept("collision-ball-into-pinCollider*", self.handleCollision)

    def onMouseClick(self):
        print("Mouse Clicked!")
        self.rollBall()

    def rollBall(self):
        print("Rolling the ball")
        rollSequence = Sequence(
            LerpPosInterval(self.ball, 3, Point3(20, -1.2, 0)), name="rollSequence"
        )
        rollSequence.start()

    def handleCollision(self, entry):
        print("Collision Handler Called")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()
        print(f"From Node: {fromNode.getName()}")
        print(f"Into Node: {intoNode.getName()}")
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))
        self.knockDownPin(self.pins[pin_index])

    def knockDownPin(self, pin):
        knockDownSequence = Sequence(
            LerpHprInterval(pin, 0.5, (90, 0, 0)), name="knockDownSequence"
        )
        knockDownSequence.start()

    def update(self, task):
        dt = globalClock.getDt()
        self.cTrav.traverse(self.game.render)
        return task.cont