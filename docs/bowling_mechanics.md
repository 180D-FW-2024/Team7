# Bowling Mechanics Module Documentation

## Overview

`bowling_mechanics.py` handles the core bowling game mechanics, including ball movement, pin setup, collision detection, and game state management.

## State Management

The module maintains several key states:

- Ball position and movement
- Pin positions and states (knocked/standing)
- Game state (can_bowl, reset_timer)
- Collision detection system
- Score tracking

## Class Structure

### BowlingMechanics Class

```python
class BowlingMechanics:
    def __init__(self, game, options):
```

Main class that manages all bowling-related mechanics.

#### Key Components:

1. **Constants and Configuration**

```python
self.ACCEL_THRESHOLD = 2.0
self.ball_movement_delta = 0.5
self.pin_spacing = 1.9
self.pin_x_offset, self.pin_y_offset, self.pin_z_offset = 7, -0.1, 2.5
```

- Defines game physics parameters
- Sets up pin layout configuration
- Configures movement constraints

2. **Pin Layout**

```python
self.row_positions = [
    [(0, 0)],
    [(self.pin_spacing, 0.5 * self.pin_spacing),
     (self.pin_spacing, -0.5 * self.pin_spacing)],
    # ... more positions
]
```

- Defines the standard bowling pin triangle layout
- Each tuple represents (x, z) coordinates for pin placement

3. **Game Setup**

- `setupLane()`: Creates and positions the bowling lane
- `setupPins()`: Creates and positions all bowling pins
- `setupBowlingBall()`: Creates and positions the bowling ball
- `setupCollisions()`: Configures collision detection system
- `setupControls()`: Sets up input controls

4. **Ball Movement**

```python
def moveBallHorizontal(self, distance):
    if self.can_bowl:
        # Normalize distance to valid range
        old_min, old_max = -100, 100
        new_min, new_max = -3.7, 3.7
        normalized = (distance - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
        z = max(min(normalized, new_max), new_min)
        # Update ball position
        current_pos = self.ball.getPos()
        self.ball.setPos(
            current_pos.getX(),
            current_pos.getY(),
            z
        )
```

- Handles horizontal ball movement
- Normalizes input distance to valid range
- Updates ball position while maintaining constraints

5. **IMU Integration**

```python
def handle_imu_update(self, gyro_x, gyro_y, gyro_z):
```

- Processes IMU gyroscope (y-axis) data
- Uses circular buffer to keep track of "historical" data to detect swing
- Maps IMU data to a "time in motion" value
- Passes "time in motion" value to rollBall(time) which updates ball position on screen

6. **Collision System**

```python
def setupCollisions(self):
    self.cTrav = CollisionTraverser()
    self.handler = CollisionHandlerEvent()
    self.pinHandler = CollisionHandlerEvent()
    # ... collision setup code
```

- Sets up collision detection between ball and pins
- Handles pin-to-pin collisions
- Uses Panda3D's collision system

7. **Pin Management**

```python
def reset_board(self, full_reset=False):
```

- Handles pin reset after each throw
- Supports full and partial resets
- Updates pin visibility and positions

8. **Game Logic Integration**

- Integrates with GameLogic class for score tracking
- Manages turn transitions
- Handles game state updates

## Event System

The module handles several events:

- Mouse clicks for ball rolling
- IMU acceleration updates
- Position tracking updates
- Collision events

## Dependencies

- Panda3D (3D graphics and physics)
- game_logic (Score tracking)
- scoreboard (Score display)

## State Transitions

1. **Ball Movement State**

   - Initial position: (-10, -1.2, 0)
   - Movement constraints: z ∈ [-3.7, 3.7]
   - Movement controlled by IMU or manual input

2. **Pin State**

   - Initial: All pins standing
   - After collision: Pins can be knocked down
   - Reset: Pins return to initial positions

3. **Game State**
   - can_bowl: Controls when ball can be rolled
   - reset_timer: Manages pin reset timing
   - knocked_pins: Tracks which pins are knocked down

## Usage

The BowlingMechanics class is instantiated by the main game:

```python
self.bowling_mechanics = BowlingMechanics(self, options)
```

It handles all bowling-related mechanics while maintaining communication with the main game loop and other components.
