# Scoreboard Module Documentation

## Overview

`scoreboard.py` handles the visual display of the bowling game scoreboard, including player names, frame scores, and running totals. It provides both visual and audio feedback for the game state.

## State Management

The module maintains several key states:

- Player names
- Frame scores for both players
- Running totals
- Scoreboard visual elements
- Speech recognition state

## Class Structure

### Scoreboard Class

```python
class Scoreboard:
    def __init__(self, game, game_logic, options):
```

Main class that manages the scoreboard display and interaction.

#### Key Components:

1. **Initialization**

```python
self.game = game
self.game_logic = game_logic
self.disable_speech = options.disable_speech
self.enable_print = options.enable_print
```

- Stores game and logic references
- Configures speech and print options
- Initializes score tracking arrays

2. **Player Name Management**

```python
def get_and_display_player_names(self):
```

- Handles speech recognition for player names
- Provides fallback for disabled speech
- Displays names on scoreboard

3. **Scoreboard Setup**

```python
def setup_scoreboard(self):
```

- Creates visual scoreboard elements
- Sets up frame positions
- Initializes score display nodes
- Configures layout and styling

4. **Frame Score Formatting**

```python
def format_frame_score(self, player, frame_idx):
```

- Formats individual frame scores
- Handles special cases:
  - Strikes (X)
  - Spares (/)
  - Empty frames
- Returns [first_roll, second_roll, total]

5. **Scoreboard Update**

```python
def update_scoreboard(self, task):
```

- Updates all score displays
- Refreshes running totals
- Maintains visual consistency
- Runs as a continuous task

## Visual Layout

1. **Scoreboard Background**

- Uses CardMaker for background
- Loads and positions scoreboard texture
- Handles transparency and orientation

2. **Frame Positions**

```python
frame_positions = {
    PlayerTurn.PLAYER_ONE: {
        "R1": (-0.05, 0.75),
        "R2": (0.295, 0.75),
        "R3": (0.64, 0.75),
        "Total": (0.985, 0.75),
    },
    # ... Player 2 positions
}
```

- Defines precise positions for each score element
- Maintains consistent spacing
- Handles both players' displays

3. **Score Offsets**

```python
self.score_offsets = {
    "first_roll": (frame_1_x_offset, frame1_z_offset),
    "second_roll": (frame2_x_offset, frame2_z_offset),
    "total": (round_x_offset, round_z_offset),
}
```

- Manages spacing between score elements
- Ensures proper alignment
- Handles different score types

## Speech Recognition

1. **Name Input**

```python
def listen_for_name(prompt):
    recognizer = sr.Recognizer()
    # ... speech recognition code
```

- Handles voice input for player names
- Provides error handling
- Supports retry on failure

2. **Name Display**

```python
def displayPlayerNames(self):
    positions = {
        "p1": (-.7, 0.77),
        "p2": (-.7, 0.65),
    }
    # ... name display code
```

- Shows player names on scoreboard
- Handles positioning and styling
- Updates when names change

## Dependencies

- Panda3D (3D graphics)
- speech_recognition (Voice input)
- game_logic (Score data)

## Visual Elements

1. **Text Nodes**

- Player names
- Frame scores
- Running totals
- All use TextNode for consistent rendering

2. **Background**

- Scoreboard texture
- CardMaker for 2D display
- Proper transparency handling

3. **Layout**

- Consistent spacing
- Clear visual hierarchy
- Responsive positioning

## State Transitions

1. **Score Updates**

- Frame scores update after each roll
- Running totals update after frame completion
- Visual elements refresh continuously

2. **Name Updates**

- Initial: Empty or default names
- After speech input: Player-provided names
- Display updates immediately

3. **Display Updates**

- Continuous task updates all elements
- Maintains visual consistency
- Handles all score changes

## Usage

The Scoreboard class is instantiated by the main game:

```python
self.scoreboard = Scoreboard(self.game, self.game_logic, options)
```

It provides visual feedback for the game state while maintaining communication with the game logic and main game components.

## Error Handling

- Speech recognition failures
- Display update errors
- Score formatting edge cases
- Visual element positioning issues
