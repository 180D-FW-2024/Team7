#!/usr/bin/env python
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBaseGlobal import aspect2d
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode, CardMaker
from direct.gui import DirectGuiGlobals as DGG
import speech_recognition as sr

#extra dependencies: pip install pocketsphinx

class IntroScreen:
    def __init__(self, game, options):
        self.game = game
        self.enable_print = options.enable_print
        self.disable_speech = options.disable_speech
        
        # Initialize player names
        self.p1_name = ""
        self.p2_name = ""
        self.current_player = 1
        
        # Create black background
        self.setup_background()
        self.setup_prompts()
        self.setup_buttons()
        
        # If speech is disabled, skip naming
        if self.disable_speech:
            self.p1_name = "Player 1"
            self.p2_name = "Player 2"
            self.start_game()

    def setup_background(self):
        cm = CardMaker("background")
        cm.setFrameFullscreenQuad()
        self.background = aspect2d.attachNewNode(cm.generate())
        self.background.setColor(0, 0, 0, 1)

    def setup_prompts(self):
        self.title = OnscreenText(
            text="Welcome to not Wii Sports!",
            pos=(0, 0.6),
            scale=0.12,
            fg=(1, 1, 1, 1),
            shadow=(0.5, 0.5, 1, 0.5),  # Blue shadow for depth
            align=TextNode.ACenter
        )
        
        self.prompt = OnscreenText(
            text="Player 1: Press Record to Say Your Name",
            pos=(0, 0.3),
            scale=0.08,
            fg=(1, 0.95, 0.8, 1),  # Warm white color
            align=TextNode.ACenter
        )
        
        self.name_display = OnscreenText(
            text="",
            pos=(0, 0),
            scale=0.09,  # Slightly larger
            fg=(0.3, 1, 0.3, 1),  # Brighter green
            shadow=(0, 0.3, 0, 0.3),  # Green shadow
            align=TextNode.ACenter
        )
        
        self.status = OnscreenText(
            text="",
            pos=(0, -0.2),
            scale=0.07,
            fg=(1, 1, 0.3, 1),  # Brighter yellow
            align=TextNode.ACenter
        )

    def setup_buttons(self):
        button_props = {
            'frameSize': (-3, 3, -0.4, 0.8),  # Adjusted size
            'text_scale': 0.6,               # Slightly smaller text
            'relief': DGG.RAISED,
            'text_pos': (0, -0.1),           # Center text vertically
        }
        
        # Record button with multi-state text
        self.record_button = DirectButton(
            text=["Record Name", "Recording...", "Record Name", "Record Name"],
            pos=(0, 0, -0.4),
            scale=0.12,  # Slightly larger
            command=self.record_name,
            frameColor=[
                (0.2, 0.8, 0.2, 1),  # Normal - Green
                (0.9, 0.2, 0.2, 1),  # Click - Bright Red
                (0.3, 0.9, 0.3, 1),  # Hover - Lighter Green
                (0.5, 0.5, 0.5, 0.7)
            ],  # Disabled - Gray
            **button_props
        )
        
        # Confirm and retry buttons
        self.confirm_button = DirectButton(
            text="Confirm Name",
            pos=(0.35, 0, -0.4),  # Moved slightly right
            scale=0.1,
            command=self.confirm_name,
            frameColor=[
                (0.2, 0.2, 0.9, 1),  # Normal - Blue
                (0.3, 0.3, 1, 1),    # Click - Bright Blue
                (0.25, 0.25, 0.95, 1),  
                (0.2, 0.2, 0.5, 0.7)
            ],
            **button_props
        )
        
        self.retry_button = DirectButton(
            text="Try Again",
            pos=(-0.35, 0, -0.4),  # Moved slightly left
            scale=0.1,
            command=self.retry_name,
            frameColor=[
                (0.8, 0.2, 0.2, 1),  # Normal - Red
                (0.9, 0.3, 0.3, 1),  
                (0.85, 0.25, 0.25, 1),
                (0.5, 0.2, 0.2, 0.7)
            ],
            **button_props
        )

        # Hide confirm/retry by default, so they don't interfere initially
        self.confirm_button.hide()
        self.retry_button.hide()

    def record_name(self):
        recognizer = sr.Recognizer()
        try:
            # Disable and switch record button to "recording"
            self.record_button['state'] = DGG.DISABLED
            self.record_button.setText("Recording...")  # Force "Recording..." text
            self.record_button['frameColor'] = (0.8, 0.2, 0.2, 1)  # Red

            with sr.Microphone() as mic:
                self.status.setText("Listening...")
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                audio = recognizer.listen(mic, timeout=5, phrase_time_limit=3)
                
            self.status.setText("Processing...")
            name = recognizer.recognize_sphinx(audio).strip().title()
            self.name_display.setText(f"Heard: {name}")
            self.status.setText("Is this correct?")
            
            # Hide record button and show confirm/retry
            self.record_button.hide()
            self.confirm_button.show()
            self.retry_button.show()
            
            return name

        except Exception as e:
            if self.enable_print:
                print(f"Error: {e}")
            self.status.setText("Error. Please try again.")
            # Reset button state if there's an error
            self.record_button['state'] = DGG.NORMAL
            self.record_button.setText("Record Name")
            self.record_button['frameColor'] = (0.2, 0.8, 0.2, 1)
            return None

    def confirm_name(self):
        name = self.name_display.getText().replace("Heard: ", "")
        if self.current_player == 1:
            self.p1_name = name
            self.current_player = 2
            self.prompt.setText("Player 2: Press Record to Say Your Name")
        else:
            self.p2_name = name
            self.status.setText("Starting game...")
            self.game.taskMgr.doMethodLater(1.5, self.start_game, "startGame")
            return

        # Reset UI for next player's recording
        self.name_display.setText("")
        self.status.setText("")
        self.confirm_button.hide()
        self.retry_button.hide()
        
        # Show and reset record button
        self.record_button.show()
        self.record_button['state'] = DGG.NORMAL
        self.record_button.setText("Record Name")
        self.record_button['frameColor'] = (0.2, 0.8, 0.2, 1)

    def retry_name(self):
        self.name_display.setText("")
        self.status.setText("")
        self.confirm_button.hide()
        self.retry_button.hide()
        
        # Show and reset record button state
        self.record_button.show()
        self.record_button['state'] = DGG.NORMAL
        self.record_button.setText("Record Name")
        self.record_button['frameColor'] = (0.2, 0.8, 0.2, 1)

    def cleanup(self):
        self.background.removeNode()
        self.title.destroy()
        self.prompt.destroy()
        self.name_display.destroy()
        self.status.destroy()
        self.record_button.destroy()
        self.confirm_button.destroy()
        self.retry_button.destroy()

    def start_game(self, task=None):
        self.cleanup()
        self.game.p1_name = self.p1_name
        self.game.p2_name = self.p2_name
        self.game.start_game()
        if task:
            return task.done
