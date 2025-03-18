# Main Game Module Documentation

## Overview

`main.py` is the entry point of the bowling game application. It handles the initialization of the game environment, socket connections for IMU and position tracking, and the main game loop.

## State Management

The game maintains several key states:

- Socket connections for IMU and position tracking
- Game options (presentation mode, speech disable, print enable)
- Camera position and orientation
- Crosshairs display
- Process management for BLE and camera tracking

## Class Structure

### Options Class

```python
class Options:
    def __init__(self):
```

- Handles command-line argument parsing
- Manages three boolean flags:
  - `present`: True if command line arguments are provided
  - `disable_speech`: True if "-ds" flag is present
  - `enable_print`: True if "-p" flag is present

### BowlingGame Class

```python
class BowlingGame(ShowBase):
    def __init__(self, options):
```

Main game class that inherits from Panda3D's ShowBase. Manages:

- Game initialization
- Camera setup
- Socket connections
- Process management
- Event handling

#### Key Components:

1. **Camera Setup**

```python
self.disable_mouse()
self.camera.setPos(-30, -10, 0)
self.camera.setHpr(-75, 0, 90)
```

- Disables mouse control
- Positions camera for optimal bowling lane view
- Sets camera orientation

2. **Crosshairs Setup**

```python
crosshairs = OnscreenImage(
    image="../images/crosshairs.png",
    pos=(0, 0, 0),
    scale=0.05,
)
crosshairs.setTransparency(TransparencyAttrib.MAlpha)
```

- Creates transparent crosshairs for aiming

3. **Socket Connections**

- IMU Socket (Port 8080):

  - Receives acceleration data from BLE device
  - Runs in separate thread
  - Handles connection/disconnection gracefully

- Position Socket (Port 8081):
  - Receives ball position data from camera
  - Runs in separate thread
  - Handles connection/disconnection gracefully

4. **Process Management**

- BLE Process:

  - Runs central.py for IMU data collection
  - Managed through subprocess.Popen

- Camera Process:
  - Runs position_tracker.py for ball tracking
  - Uses OpenCV for ball detection
  - Managed through subprocess.Popen

5. **Cleanup Handling**

```python
def cleanup(self):
```

- Properly terminates all processes
- Closes all socket connections
- Handles graceful shutdown

6. **Connection Handlers**

- `accept_connections()`: Handles IMU data connection
- `accept_position_connections()`: Handles camera position connection
- Both run in separate threads
- Handle reconnection attempts
- Process incoming data through messenger system

## Event System

The game uses Panda3D's messenger system for event handling:

- `accel_data`: Handles IMU acceleration data
- `position_data`: Handles ball position updates
- `exit`: Handles game cleanup

## Dependencies

- Panda3D (3D graphics engine)
- simplepbr (Physically based rendering)
- socket (Network communication)
- threading (Concurrent operations)
- subprocess (External process management)

## Usage

```python
options = Options()
app = BowlingGame(options)
app.run()
```

The game is started by creating Options and BowlingGame instances, then running the main loop.
