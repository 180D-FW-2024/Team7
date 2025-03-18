# Game Logic Module Documentation

## Overview

`game_logic.py` manages the core game rules, scoring system, and turn management for the bowling game. It implements the standard bowling scoring rules and handles game progression.

## State Management

The module maintains several key states:

- Current player
- Current round
- Frame scores for each player
- Game completion status
- Current roll within frame

## Class Structure

### PlayerTurn Enum

```python
class PlayerTurn(Enum):
    PLAYER_ONE = 1
    PLAYER_TWO = 2
```

- Defines the two possible players in the game
- Used for tracking whose turn it is

### Frame Dataclass

```python
@dataclass
class Frame:
    first_roll: int = 0
    second_roll: int = 0
    is_complete: bool = False
```

- Represents a single frame in bowling
- Tracks:
  - First roll score
  - Second roll score
  - Frame completion status

### GameLogic Class

```python
class GameLogic:
    def __init__(self, options):
```

Main class that manages game rules and scoring.

#### Key Components:

1. **Game State Initialization**

```python
self.current_player = PlayerTurn.PLAYER_ONE
self.current_round = 1
self.max_rounds = 3
self.current_roll = 1
self.game_complete = False
```

- Sets up initial game state
- Configures number of rounds
- Initializes player tracking

2. **Score Tracking**

```python
self.scores = {
    PlayerTurn.PLAYER_ONE: [Frame() for _ in range(self.max_rounds)],
    PlayerTurn.PLAYER_TWO: [Frame() for _ in range(self.max_rounds)],
}
```

- Maintains separate score arrays for each player
- Each player has an array of frames
- Each frame tracks individual rolls

3. **Roll Recording**

```python
def record_roll(self, pins_knocked: int) -> None:
```

- Records the number of pins knocked down
- Handles special cases:
  - Strike (10 pins on first roll)
  - Spare (10 pins total in two rolls)
- Updates frame completion status
- Triggers turn advancement when needed

4. **Turn Management**

```python
def advance_turn(self) -> None:
```

- Handles turn transitions between players
- Manages round progression
- Updates game completion status
- Resets roll counter

5. **Score Calculation**

```python
def get_frame_score(self, player: PlayerTurn, frame_idx: int) -> int:
def get_current_score(self, player: PlayerTurn) -> int:
```

- Calculates individual frame scores
- Computes running total for each player
- Handles special scoring rules for strikes and spares

## State Transitions

1. **Frame State**

   - Initial: Empty frame (0, 0, False)
   - After first roll: (pins_knocked, 0, False)
   - After second roll: (first_roll, second_roll, True)
   - Special case: Strike (10, 0, True)

2. **Turn State**

   - Player 1 → Player 2 → Player 1
   - Round increments after both players complete their frames
   - Game completes after max_rounds

3. **Roll State**
   - Alternates between 1 and 2 within each frame
   - Resets to 1 after frame completion
   - Special handling for strikes

## Dependencies

- dataclasses (Frame data structure)
- enum (Player turn enumeration)

## Usage

The GameLogic class is instantiated by the main game:

```python
self.game_logic = GameLogic(options)
```

It manages all game rules and scoring while communicating with the bowling mechanics and scoreboard components.

## Scoring Rules

1. **Standard Frame**

   - Two rolls per frame
   - Score is sum of pins knocked down
   - Frame completes after second roll

2. **Strike**

   - 10 pins on first roll
   - Frame completes immediately
   - Special bonus scoring (not implemented in current version)

3. **Spare**
   - 10 pins total in two rolls
   - Special bonus scoring (not implemented in current version)

## Game Flow

1. Player 1 rolls
2. If not a strike, Player 1 rolls again
3. Player 2 rolls
4. If not a strike, Player 2 rolls again
5. Round increments
6. Repeat until max_rounds reached
