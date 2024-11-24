#!/usr/bin/env python
from direct.gui.OnscreenText import OnscreenText
from game_logic import PlayerTurn

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib, CardMaker, TransformState, TextureStage
from panda3d.core import Point3, Vec3

class Scoreboard:
    def __init__(self, game, game_logic):
        self.game = game
        self.game_logic = game_logic

        self.p1_frames = []
        self.p2_frames = []
        self.p1_total = None
        self.p2_total = None

        self.setup_scoreboard()

        self.game.taskMgr.add(self.update_scoreboard, "scoreboard_update")

    def setup_scoreboard(self):

        # setup the png of the scoreboard, this code is a bit messy but worked for our purposes
        print("setting up scoreboard")
        cm = CardMaker('scoreboardCard')
        cm.setFrame(5.5, 0, 15, -15)
        scorecard = self.game.render.attachNewNode(cm.generate())
        scorecard.setTexTransform(TextureStage.getDefault(), TransformState.makeHpr((90, 180, 0)))
        scoreboard_tex = self.game.loader.loadTexture("../images/scoreboard.png")
        scorecard.setTexture(scoreboard_tex)
        scorecard.setPos(19, -9.5, 0)
        scorecard.setHpr(90, 0, 0)
        scorecard.setTwoSided(True)

        # creating frame nodes for each player
        self.frame_nodes = {
            PlayerTurn.PLAYER_ONE: {},
            PlayerTurn.PLAYER_TWO: {}
        }

        # Define relative positions for each frame node
        # Adjust these coordinates to match your scoreboard layout
        p1_y_pos = -10  # Player 1 row y-position
        p2_y_pos = -8  # Player 2 row y-position
        frame_z_positions = {
            'R1': -2,  # Frame 1 x-position
            'R2': -1,  # Frame 2 x-position
            'R3': 1,  # Frame 3 x-position
            'Total': 2  # Total score x-position
        }

        # Create nodes for Player 1
        for frame_name, x_pos in frame_z_positions.items():
            node = scorecard.attachNewNode(f'p1_{frame_name}_node')
            node.setPos(x_pos, p1_y_pos, 0)
            self.frame_nodes[PlayerTurn.PLAYER_ONE][frame_name] = node

        # Create nodes for Player 2
        for frame_name, x_pos in frame_z_positions.items():
            node = scorecard.attachNewNode(f'p2_{frame_name}_node')
            node.setPos(x_pos, p2_y_pos, 0)
            self.frame_nodes[PlayerTurn.PLAYER_TWO][frame_name] = node

        # Create frame score displays with relative positioning
        self.p1_frames = []
        self.p2_frames = []

        # Set up score text relative to frame nodes
        kameron_font = self.game.loader.loadFont('../models/Kameron.ttf')
        text_offset_x = 5.0
        text_offset_y = 0.0

        # Player 1 frame scores
        for i in range(3):
            frame_node = self.frame_nodes[PlayerTurn.PLAYER_ONE][f'R{i + 1}']
            frame_text = OnscreenText(
                text="",
                scale=0.2,
                fg=(0, 0, 0, 0),
                align=0,
                mayChange=True,
                font = kameron_font,
            )
            frame_text.reparentTo(frame_node)
            frame_text.setPos(text_offset_x, text_offset_y)
            self.p1_frames.append(frame_text)

        # Player 2 frame scores
        for i in range(3):
            frame_node = self.frame_nodes[PlayerTurn.PLAYER_TWO][f'R{i + 1}']
            frame_text = OnscreenText(
                text="",
                scale=0.2,
                fg=(0, 0, 0, 0),
                align=0,
                mayChange=True,
                font = kameron_font,
            )
            frame_text.reparentTo(frame_node)
            frame_text.setPos(text_offset_x, text_offset_y)
            self.p2_frames.append(frame_text)

        # Total score displays
        self.p1_total = OnscreenText(
            text="",
            scale=0.2,
            fg=(0, 0, 0, 0),
            align=0,
            mayChange=True,
            font = kameron_font,
        )
        self.p1_total.reparentTo(self.frame_nodes[PlayerTurn.PLAYER_ONE]['Total'])
        self.p1_total.setPos(text_offset_x, text_offset_y)

        self.p2_total = OnscreenText(
            text="",
            scale=0.2,
            fg=(1, 1, 1, 1),
            align=0,
            mayChange=True,
            font = kameron_font,
        )
        self.p2_total.reparentTo(self.frame_nodes[PlayerTurn.PLAYER_TWO]['Total'])
        self.p2_total.setPos(text_offset_x, text_offset_y)

    def format_frame_score(self, player, frame_idx):
        frame = self.game_logic.scores[player][frame_idx]
        if not frame.is_complete:
            if frame.first_roll == 0:
                return ""
            elif self.game_logic.current_roll == 2:
                return str(frame.first_roll)
            return ""

        frame_score = self.game_logic.get_frame_score(player, frame_idx)

        if frame.first_roll == 10:
            return "X"
        elif frame_score == 10:
            return f"{frame.first_roll}/"
        else:
            return f"{frame.first_roll}{frame.second_roll}"

    def update_scoreboard(self, task):
        # player 1
        for i in range(3):
            score_text = self.format_frame_score(PlayerTurn.PLAYER_ONE, i)
            self.p1_frames[i].setText(score_text)

        # player 2
        for i in range(3):
            score_text = self.format_frame_score(PlayerTurn.PLAYER_TWO, i)
            self.p2_frames[i].setText(score_text)

        p1_total = self.game_logic.get_current_score(PlayerTurn.PLAYER_ONE)
        p2_total = self.game_logic.get_current_score(PlayerTurn.PLAYER_TWO)

        self.p1_total.setText(str(p1_total))
        self.p2_total.setText(str(p2_total))

        return task.cont