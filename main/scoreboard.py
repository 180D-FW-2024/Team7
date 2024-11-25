#!/usr/bin/env python
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBaseGlobal import aspect2d

from game_logic import PlayerTurn

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import (
    TransparencyAttrib,
    CardMaker,
    TransformState,
    TextureStage,
    TextNode,
)
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
        cm = CardMaker("scoreboardCard")
        cm.setFrame(5.5, 0, 15, -15)
        scorecard = self.game.render.attachNewNode(cm.generate())
        scorecard.setTexTransform(
            TextureStage.getDefault(), TransformState.makeHpr((90, 180, 0))
        )
        scoreboard_tex = self.game.loader.loadTexture("../images/scoreboard.png")
        scorecard.setTexture(scoreboard_tex)
        scorecard.setPos(19, -9.5, 0)
        scorecard.setHpr(90, 0, 0)
        scorecard.setTwoSided(True)

        # xz positions let y be set to 0
        frame_positions = {
            PlayerTurn.PLAYER_ONE: {
                "R1": (-0.05, 0.75),
                "R2": (0.295, 0.75),
                "R3": (0.64, 0.75),
                "Total": (0.985, 0.75),  #
            },
            PlayerTurn.PLAYER_TWO: {
                "R1": (-0.05, 0.63),
                "R2": (0.295, 0.63),
                "R3": (0.64, 0.63),
                "Total": (0.985, 0.63),
            },
        }

        ## maintain global xz offset for each of the three different types of scores
        frame_1_x_offset = 0
        frame1_z_offset = 0.048
        frame2_x_offset = 0.13
        frame2_z_offset = 0.048
        round_x_offset = 0.13
        round_z_offset = 0
        self.score_offsets = {
            "first_roll": (frame_1_x_offset, frame1_z_offset),
            "second_roll": (frame2_x_offset, frame2_z_offset),
            "total": (round_x_offset, round_z_offset),
        }

        # we should instead insert a tuple of (first roll, second roll, total) per frame
        print("creating nodes for p1")
        self.p1_frames = []
        for i in range(3):
            frame_nodes = []
            base_pos = frame_positions[PlayerTurn.PLAYER_ONE][f"R{i + 1}"]
            # Create nodes for first roll, second roll, and total
            for score_type, offset in self.score_offsets.items():
                text = TextNode(f"p1_frame_{i}_{score_type}")
                text.setText("")
                text.setAlign(TextNode.ACenter)
                text.setTextColor(0, 0, 0, 1)
                text_np = aspect2d.attachNewNode(text)

                # Position with offset
                text_np.setPos(base_pos[0] + offset[0], 0, base_pos[1] + offset[1])
                text_np.setScale(0.05)
                frame_nodes.append(text_np)

            self.p1_frames.append(frame_nodes)

        # Similar setup for Player 2
        self.p2_frames = []
        for i in range(3):
            frame_nodes = []
            base_pos = frame_positions[PlayerTurn.PLAYER_TWO][f"R{i + 1}"]
            for score_type, offset in self.score_offsets.items():
                text = TextNode(f"p2_frame_{i}_{score_type}")
                text.setText("")
                text.setAlign(TextNode.ACenter)
                text.setTextColor(0, 0, 0, 1)
                text_np = aspect2d.attachNewNode(text)
                text_np.setPos(base_pos[0] + offset[0], 0, base_pos[1] + offset[1])
                text_np.setScale(0.05)
                frame_nodes.append(text_np)

            self.p2_frames.append(frame_nodes)

        # p1 total
        self.p1_total = TextNode("p1_total")
        self.p1_total.setText("p1_total")
        self.p1_total.setAlign(TextNode.ACenter)
        self.p1_total.setTextColor(0, 0, 0, 1)
        p1_total_np = aspect2d.attachNewNode(self.p1_total)
        p1_total_np.setPos(
            frame_positions[PlayerTurn.PLAYER_ONE]["Total"][0],
            0,
            frame_positions[PlayerTurn.PLAYER_ONE]["Total"][1],
        )
        p1_total_np.setScale(0.05)

        # p2 total
        self.p2_total = TextNode("p2_total")
        self.p2_total.setText("p2_total")
        self.p2_total.setAlign(TextNode.ACenter)
        self.p2_total.setTextColor(0, 0, 0, 1)
        p2_total_np = aspect2d.attachNewNode(self.p2_total)
        p2_total_np.setPos(
            frame_positions[PlayerTurn.PLAYER_TWO]["Total"][0],
            0,
            frame_positions[PlayerTurn.PLAYER_TWO]["Total"][1],
        )
        p2_total_np.setScale(0.05)

    def format_frame_score(self, player, frame_idx):
        frame = self.game_logic.scores[player][frame_idx]

        first_roll = (
            str(frame.first_roll)
            if (frame.first_roll > 0 and frame.first_roll != 10)
            else ""
        )

        second_roll = ""
        if frame.is_complete:
            if frame.first_roll == 10:
                second_roll = "X"
                total = "10"
                return [first_roll, second_roll, total]
            else:
                second_roll = (
                    "/"
                    if (frame.first_roll + frame.second_roll == 10)
                    else str(frame.second_roll)
                )
        # elif self.game_logic.current_roll == 2:
        #     print("resetting second frame based on cur roll", self.game_logic.current_roll)
        #     second_roll = str(frame.second_roll)

        # Total frame score
        total = ""
        if frame.is_complete:
            total = str(frame.second_roll + frame.first_roll)

        # print(player, frame_idx, [first_roll, second_roll, total])
        return [first_roll, second_roll, total]

    def update_scoreboard(self, task):
        # Update Player 1 frames
        for i in range(3):
            scores = self.format_frame_score(PlayerTurn.PLAYER_ONE, i)
            for j, score in enumerate(scores):
                self.p1_frames[i][j].node().setText(score)

        # Update Player 2 frames
        for i in range(3):
            scores = self.format_frame_score(PlayerTurn.PLAYER_TWO, i)
            for j, score in enumerate(scores):
                self.p2_frames[i][j].node().setText(score)

        # Update totals
        p1_total = self.game_logic.get_current_score(PlayerTurn.PLAYER_ONE)
        p2_total = self.game_logic.get_current_score(PlayerTurn.PLAYER_TWO)

        self.p1_total.setText(str(p1_total))
        self.p2_total.setText(str(p2_total))

        return task.cont
