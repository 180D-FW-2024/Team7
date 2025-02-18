#!/usr/bin/env python

from direct.task.TaskManagerGlobal import taskMgr

from game_logic import GameLogic, PlayerTurn
from scoreboard import Scoreboard
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
    CollisionCapsule,
    BitMask32,
    Quat,
    PointLight,
    AmbientLight,
    DirectionalLight,
    Spotlight,
    PerspectiveLens,
)
from direct.interval.IntervalGlobal import (
    Sequence,
    Parallel,
    LerpPosInterval,
    LerpHprInterval,
    LerpPosHprInterval,
)
from math import sqrt, exp

MIN_SAMPLES_THRESHOLD = 3
BUFFER_SIZE = 5

class BowlingMechanics:
    def __init__(self, game, options):

        # options
        self.enable_print = options.enable_print
        self.enable_print_power_mag = options.enable_print_power_mag

        self.power_level_buffer = [0] * BUFFER_SIZE

        # constants
        ###### TESTING ACCEL_THRESHOLD
        self.ACCEL_THRESHOLD = 2.0
        ######
        self.ball_movement_delta = 0.5
        self.pin_spacing = 1.9
        self.pin_x_offset, self.pin_y_offset, self.pin_z_offset = 7, -0.1, 2.5
        self.row_positions = [
            [(0, 0)],
            [
                (self.pin_spacing, 0.5 * self.pin_spacing),
                (self.pin_spacing, -0.5 * self.pin_spacing),
            ],
            [
                (2 * self.pin_spacing, self.pin_spacing),
                (2 * self.pin_spacing, 0),
                (2 * self.pin_spacing, -self.pin_spacing),
            ],
            [
                (3 * self.pin_spacing, 1.5 * self.pin_spacing),
                (3 * self.pin_spacing, 0.5 * self.pin_spacing),
                (3 * self.pin_spacing, -0.5 * self.pin_spacing),
                (3 * self.pin_spacing, -1.5 * self.pin_spacing),
            ],
        ]

        # setup
        self.game = game
        
        # Set background color (darker, closer to black)
        self.game.setBackgroundColor(0.02, 0.02, 0.08)
        
        # Create and position overhead lights
        self.setupLighting()
        
        self.setupLane()
        self.pins = []
        self.setupPins()
        self.setupBowlingBall()
        self.setupCollisions()
        self.setupControls()

        # game logic & scorebaord
        self.game_logic = GameLogic(options)
        ### TESTING Scoreboard class
        self.scoreboard = Scoreboard(self.game, self.game_logic, options)
        ###
        self.knocked_pins = {i: False for i in range(10)}
        self.pins_knocked = 0
        self.can_bowl = True
        self.reset_timer = 0

        # update tasks
        self.game.taskMgr.add(self.update, "updateTask")
        self.game.accept("mouse1", self.onMouseClick)
        self.game.accept('accel_data', self.handle_accel_update)
        self.game.accept('position_data', self.moveBallHorizontal)

    def moveBallHorizontal(self, distance):
        if self.can_bowl:
            old_min, old_max = -100, 100
            new_min, new_max = -3.7, 3.7
            normalized = (distance - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
            z = max(min(normalized, new_max), new_min)
            current_pos = self.ball.getPos()
            self.ball.setPos(
                current_pos.getX(),
                current_pos.getY(),
                z
            )

    def handle_accel_update(self, gyro_x, gyro_y, gyro_z):

        def add_to_buffer(val):
            self.power_level_buffer.pop(0)
            self.power_level_buffer.append(val)

        # Increase the range of power levels by reducing the divisor
        power_level = gyro_y
        power_level = int(power_level / 10)  
        
        # Adjust the thresholds and scaling
        if power_level < 4:  # Minimum threshold
            power_level = 0
        elif power_level > 16:  # Maximum threshold
            power_level = 16

        add_to_buffer(power_level)

        # Find consecutive nonzeros
        start = 0
        count = 0
        i = 0
        while i < BUFFER_SIZE:
            i_start = i
            i_count = 0
            for j in range(i_start, BUFFER_SIZE):
                if self.power_level_buffer[j] > 0:
                    i_count += 1
                else:
                    break
            if i_count > count:
                start = i_start
                count = i_count
                i = i_start + i_count
            else:
                i += 1

        stroke = self.power_level_buffer[start:start+count-1]
        
        if count >= MIN_SAMPLES_THRESHOLD:
            # Calculate average power
            avg_power = sum(stroke) / len(stroke)
            
            # Exponential scaling creates bigger difference between soft and hard swings
            scaled_power = (avg_power ** 1.8) / 10  # Adjust exponent for desired curve
            
            # Map to roll time (1 to 8)
            roll_time = max(1, min(8, 8 - scaled_power))
            
            if self.enable_print_power_mag: 
                print(f"raw power: {avg_power}, scaled power: {scaled_power}, roll time: {roll_time}")
            if self.enable_print: 
                print("rolling ball")
                
            self.rollBall(roll_time)

            
    def setupLane(self):
        self.lane = self.game.loader.loadModel("../models/bowling-lane.glb")
        self.lane.reparentTo(self.game.render)
        self.lane.setPos(2, 0, 0)

        # Add background lanes
        self.left_lane = self.game.loader.loadModel("../models/bowling-lane.glb")
        self.left_lane.reparentTo(self.game.render)
        self.left_lane.setPos(2, 0, -12.5)

        self.right_lane = self.game.loader.loadModel("../models/bowling-lane.glb")
        self.right_lane.reparentTo(self.game.render)
        self.right_lane.setPos(2, 0, 12.5)

        self.right_gutter = self.game.loader.loadModel("../models/gutter2.glb")
        self.right_gutter.reparentTo(self.game.render)
        self.right_gutter.setPos(2, 0, 6.25)

        self.left_gutter = self.game.loader.loadModel("../models/gutter2.glb")
        self.left_gutter.reparentTo(self.game.render)
        self.left_gutter.setPos(2, 0, -6.25)

        self.right_gutter2 = self.game.loader.loadModel("../models/gutter2.glb")
        self.right_gutter2.reparentTo(self.game.render)
        self.right_gutter2.setPos(2, 0, 19)

        self.left_gutter2 = self.game.loader.loadModel("../models/gutter2.glb")
        self.left_gutter2.reparentTo(self.game.render)
        self.left_gutter2.setPos(2, 0, -19)


        self.backdrop = self.game.loader.loadModel("../models/backdrop2.glb")
        self.backdrop.reparentTo(self.game.render)
        self.backdrop.setPos(18, -1.5, 0)
        self.backdrop.setScale(1, 2, 1)

        self.backdrop2 = self.game.loader.loadModel("../models/backdrop2.glb")
        self.backdrop2.reparentTo(self.game.render)
        self.backdrop2.setPos(18, -1.5, 12.5)
        self.backdrop2.setScale(1, 2, 1)

        self.backdrop3 = self.game.loader.loadModel("../models/backdrop2.glb")
        self.backdrop3.reparentTo(self.game.render)
        self.backdrop3.setPos(18, -1.5, -12.5)
        self.backdrop3.setScale(1, 2, 1)

    def setupPins(self):
        for i, row in enumerate(self.row_positions):
            for j, (x, z) in enumerate(row):
                pin = self.game.loader.loadModel("../models/bowling-pin.glb")
                pin.reparentTo(self.game.render)
                pin.setPos(
                    x + self.pin_x_offset, self.pin_y_offset, z + self.pin_z_offset
                )
                pin.setHpr(180, 0, 0)
                pin.setScale(10)
                self.pins.append(pin)

    def reset_board(self, full_reset=False):
        if full_reset:
            if self.enable_print: print("performing full reset")
            pin_num = 0
            for i, row in enumerate(self.row_positions):
                for j, (x, z) in enumerate(row):
                    pin = self.pins[pin_num]
                    pin.show()
                    pin.wrtReparentTo(self.game.render)
                    pin.setPos(
                        x + self.pin_x_offset, self.pin_y_offset, z + self.pin_z_offset
                    )
                    pin.setHpr(180, 0, 0)
                    pin_num += 1

        else:
            if self.enable_print: print("performing partial reset")
            for i, is_knocked in self.knocked_pins.items():
                if is_knocked:
                    self.pins[i].hide()

        if full_reset:
            self.knocked_pins = {i: False for i in range(10)}
            self.pins_knocked = 0

        self.ball.setPos(-10, -1.2, 0)
        self.can_bowl = True

    def setupBowlingBall(self):
        self.ball = self.game.loader.loadModel("../models/bowling-ball.glb")
        self.ball.reparentTo(self.game.render)
        self.ball.setPos(-10, -1.2, 0)
        self.ball.setScale(5)

    def setupControls(self):
        self.game.accept("arrow_left", self.moveBallLeft)
        self.game.accept("arrow_right", self.moveBallRight)

    def moveBallLeft(self):
        current_pos = self.ball.getPos()
        if current_pos.getZ() > -3.5:
            self.ball.setPos(
                current_pos.getX(),
                current_pos.getY(),
                current_pos.getZ() - self.ball_movement_delta,
            )

    def moveBallRight(self):
        current_pos = self.ball.getPos()
        if current_pos.getZ() < 3.5:
            self.ball.setPos(
                current_pos.getX(),
                current_pos.getY(),
                current_pos.getZ() + self.ball_movement_delta,
            )

    def setupCollisions(self):
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerEvent()
        self.pinHandler = CollisionHandlerEvent()

        BALL_MASK = BitMask32.bit(0)
        PIN_MASK = BitMask32.bit(1)

        ballCollider = self.ball.attachNewNode(CollisionNode("ball"))
        ballCollider.node().addSolid(CollisionSphere(0, 0, 0, 0.2))

        ballCollider.node().setFromCollideMask(PIN_MASK)  # Ball can collide with pins
        ballCollider.node().setIntoCollideMask(
            BitMask32(0)
        )  # Ball cannot be collided with

        self.cTrav.addCollider(ballCollider, self.handler)
        # ballCollider.show()

        for i, pin in enumerate(self.pins):
            pinCollider = pin.attachNewNode(CollisionNode(f"pinCollider{i}"))
            pinCollider.node().addSolid(
                CollisionCapsule(-0.1, 0.1, -0.23, -0.1, 0.32, -0.23, 0.04)
            )
            pinCollider.node().setFromCollideMask(PIN_MASK)
            pinCollider.node().setIntoCollideMask(BALL_MASK | PIN_MASK)
            self.cTrav.addCollider(pinCollider, self.pinHandler)

            # pinCollider.show()

        self.handler.addInPattern("collision-ball-into-pinCollider*")
        self.pinHandler.addInPattern("collision-pinCollider*-into-pinCollider*")
        self.game.accept(
            "collision-ball-into-pinCollider*", self.handleBallPinCollision
        )
        self.game.accept(
            "collision-pinCollider*-into-pinCollider*", self.handlePinPinCollision
        )

    def onMouseClick(self):
        if self.enable_print: print("Mouse Clicked!")
        self.rollBall()

    def rollBall(self, time_in_motion):
        # NOTE: This roll ball function is temporary: will incorporate imu controls after
        if self.enable_print: print("Rolling the ball")
        if not self.can_bowl:
            if self.enable_print: print("can't bowl")
            return

        # setting self.can_bowl to False is part of core game event handling logic
        self.can_bowl = False
        start_pos = self.ball.getPos()
        end_x = 20
        distance_to_travel = end_x - start_pos.getX()
        y_difference = -0.1 - start_pos.getY() - 0.8
        ratio = distance_to_travel / (7 - start_pos.getX())
        end_y = start_pos.getY() + (y_difference * ratio)

        rollSequence = Sequence(
            LerpPosInterval(self.ball, time_in_motion, Point3(end_x, end_y, 0)), name="rollSequence"
        )
        rollSequence.start()

    def handleBallPinCollision(self, entry):
        if self.enable_print: print("Ball Pin Collision Detected")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()
        normal = entry.getSurfaceNormal(self.game.render)
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))

        if not self.knocked_pins[pin_index]:
            self.knocked_pins[pin_index] = True
            self.pins_knocked += 1

        self.knockDownPin(self.pins[pin_index], normal)

    def handlePinPinCollision(self, entry):
        if self.enable_print: print("Pin-Pin Collision Detected!")
        fromNode = entry.getFromNodePath()
        intoNode = entry.getIntoNodePath()

        if self.enable_print: print(f"From Pin: {fromNode.getName()}")
        if self.enable_print: print(f"Into Pin: {intoNode.getName()}")

        normal = entry.getSurfaceNormal(self.game.render)
        pin_name = intoNode.getName()
        pin_index = int(pin_name.replace("pinCollider", ""))

        if not self.knocked_pins[pin_index]:
            self.knocked_pins[pin_index] = True
            self.pins_knocked += 1

        self.knockDownPin(self.pins[pin_index], normal)

    def knockDownPin(self, pin, normal):
        rotationNode = self.game.render.attachNewNode("rotationNode")
        pinPos = pin.getPos(self.game.render)

        pinBounds = pin.getTightBounds(self.game.render)
        pinMin = pinBounds[0]
        pinBaseZ = pinMin.getZ()

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
        # TODO: Implement linear & rotational collisions more realistically, update board use LerpPosQuat and
        # other parallel combinations of intervals
        knockDownSequence = Sequence(
            LerpQuatInterval(rotationNode, 0.7, quat),
        )
        knockDownSequence.start()

    def update(self, task):
        if not self.can_bowl and self.reset_timer == 0:
            self.reset_timer = globalClock.getFrameTime()
            taskMgr.doMethodLater(6.5, self.perform_reset, "resetTask")

        self.cTrav.traverse(self.game.render)
        return task.cont

    def perform_reset(self, task):
        current_player = self.game_logic.current_player
        self.game_logic.record_roll(self.pins_knocked)
        full_reset = current_player != self.game_logic.current_player
        self.reset_board(full_reset)
        self.reset_timer = 0

        return task.done

    def setupLighting(self):
        # Clear any existing lights
        self.game.render.clearLight()
    
    # Create directional light
        
        
        # Create ambient light
        ambient_light = AmbientLight("ambient")
        ambient_light.setColor((0.3, 0.3, 0.3, 1))  # Slightly brighter ambient
        ambient_light_np = self.game.render.attachNewNode(ambient_light)
        
        # Enable lights
        
        self.game.render.setLight(ambient_light_np)
        
        # Store light nodes for later reference
        
        self.ambient_light = ambient_light_np