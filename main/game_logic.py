#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum


class PlayerTurn(Enum):
    PLAYER_ONE = 1
    PLAYER_TWO = 2

@dataclass
class Frame:
    first_roll: int = 0
    second_roll: int = 0
    is_complete: bool = False


class GameLogic:
    def __init__(self):
        # Initialize player scores and game state
        self.current_player = PlayerTurn.PLAYER_ONE
        self.current_round = 1
        self.max_rounds = 3

        # Score tracking for both players
        self.scores = {
            PlayerTurn.PLAYER_ONE: [Frame() for _ in range(self.max_rounds)],
            PlayerTurn.PLAYER_TWO: [Frame() for _ in range(self.max_rounds)],
        }

        self.current_roll = 1  # 1 for first roll, 2 for second roll
        self.game_complete = False

    def record_roll(self, pins_knocked: int) -> None:
        """Records the number of pins knocked down for current player's roll"""
        print(f"Recording Roll with {pins_knocked} pins knocked")

        print(self.current_round)
        current_frame = self.scores[self.current_player][self.current_round - 1]

        if self.current_roll == 1:
            current_frame.first_roll = pins_knocked
            if pins_knocked == 10:
                current_frame.is_complete = True
                self.advance_turn()
            else:
                self.current_roll = 2
        else:
            current_frame.second_roll = pins_knocked
            current_frame.is_complete = True
            self.advance_turn()

    def advance_turn(self) -> None:
        """Advances the game to the next player or round"""
        self.current_roll = 1

        if self.current_player == PlayerTurn.PLAYER_ONE:
            self.current_player = PlayerTurn.PLAYER_TWO
        else:
            self.current_player = PlayerTurn.PLAYER_ONE
            self.current_round += 1

        if self.current_round > self.max_rounds:
            self.game_complete = True

    def get_frame_score(self, player: PlayerTurn, frame_idx: int) -> int:
        """Calculates score for a specific frame"""
        frame = self.scores[player][frame_idx]
        return frame.first_roll + frame.second_roll

    def get_current_score(self, player: PlayerTurn) -> int:
        """Calculates total score for a player"""
        total = 0
        for frame in self.scores[player]:
            if frame.is_complete:
                total += frame.first_roll + frame.second_roll
        return total

    def is_game_complete(self) -> bool:
        return self.game_complete
