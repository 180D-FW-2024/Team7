#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import loadPrcFile, TransparencyAttrib
import simplepbr
from bowling_mechanics import BowlingMechanics
import socket, threading, subprocess, atexit, time

import sys

loadPrcFile("../config/conf.prc")


class Options:
    def __init__(self):

        self.present = False
        self.disable_speech = False
        self.enable_print = False
        self.enable_print_power_mag = False

        if len(sys.argv) > 1:
            self.present = True
        else:
            return

        if "-ds" in sys.argv:
            self.disable_speech = True

        if "-p" in sys.argv:
            self.enable_print = True

        if "-m" in sys.argv:
            self.enable_print_power_mag = True


class BowlingGame(ShowBase):
    def __init__(self, options):
        super().__init__()
        simplepbr.init()

        # Store options and initialize name variables
        self.options = options
        self.enable_print = options.enable_print
        self.p1_name = ""
        self.p2_name = ""

        # Start with intro screen
        from intro_screen import IntroScreen

        self.intro_screen = IntroScreen(self, options)

    def start_game(self):
        """Called after intro screen completes"""
        # setup camera
        self.disable_mouse()
        self.camera.setPos(-30, -10, 0)
        self.camera.setHpr(-75, 0, 90)

        # Set up crosshairs
        crosshairs = OnscreenImage(
            image="../images/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        # SETTING UP SOCKET CONNECTION AND GAME
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", 8080))
        self.server_socket.listen(1)
        if self.enable_print:
            print("setting up imu socket")

        if self.enable_print:
            self.ble_process = subprocess.Popen(["python", "../ble/central.py", "-p"])
        else:
            self.ble_process = subprocess.Popen(["python", "../ble/central.py"])

        self.socket_thread = threading.Thread(target=self.accept_connections)
        self.socket_thread.daemon = True
        self.socket_thread.start()
        if self.enable_print:
            print("thread started for imu")

        # Set up position tracking
        self.position_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.position_socket.bind(("localhost", 8081))
        self.position_socket.listen(1)
        if self.enable_print:
            print("setting up camera socket")

        self.camera_process = subprocess.Popen(
            [
                "python",
                "../position_tracker/position_tracker.py",
                "--prototxt",
                "../position_tracker/deploy.prototxt",
                "--model",
                "../position_tracker/res10_300x300_ssd_iter_140000.caffemodel",
            ]
        )

        self.position_socket_thread = threading.Thread(
            target=self.accept_position_connections
        )
        self.position_socket_thread.daemon = True
        self.position_socket_thread.start()

        # initialize the game
        self.bowling_mechanics = BowlingMechanics(self, self.options)

        # cleaning up processes and sockets
        self.accept("exit", self.cleanup)
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.enable_print:
            print("cleaning up")
        if hasattr(self, "ble_process"):
            self.ble_process.terminate()
            if self.enable_print:
                print("killed ble process")
        if hasattr(self, "camera_process"):
            self.camera_process.terminate()
            if self.enable_print:
                print("killed camera process")
        if hasattr(self, "position_socket"):
            try:
                self.position_socket.shutdown(socket.SHUT_RDWR)
                self.position_socket.close()
            except:
                pass
            if self.enable_print:
                print("killed position socket")
        if hasattr(self, "server_socket"):
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except:
                pass
            if self.enable_print:
                print("killed server socket")
        if hasattr(self, "client_socket"):
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except:
                pass
            if self.enable_print:
                print("killed client socket")

    def accept_connections(self):
        if self.enable_print:
            print("Waiting for BLE client connection...")
        while True:
            try:
                self.client_socket, addr = self.server_socket.accept()
                if self.enable_print:
                    print(f"Connected to BLE client at {addr}")
                while True:
                    try:
                        data = self.client_socket.recv(1024).decode()
                        if not data:
                            if self.enable_print:
                                print("Client disconnected")
                            break
                        accel_x, accel_y, accel_z = map(float, data.split(","))
                        # if self.enable_print: print("from main", accel_x, accel_y, accel_z)
                        self.messenger.send("accel_data", [accel_x, accel_y, accel_z])
                    except Exception as e:
                        if self.enable_print:
                            print(f"Error receiving data: {e}")
                        break

                self.client_socket.close()
            except Exception as e:
                if self.enable_print:
                    print(f"Socket connection error: {e}")
                time.sleep(1)
                break

        if self.enable_print:
            print("Done accepting IMU Data")

    def accept_position_connections(self):
        if self.enable_print:
            print("Waiting for position tracker connection...")
        while True:
            try:
                self.position_client, addr = self.position_socket.accept()
                if self.enable_print:
                    print(f"Connected to position tracker at {addr}")
                while True:
                    try:
                        data = self.position_client.recv(1024).decode()
                        if not data:
                            if self.enable_print:
                                print("Position tracker disconnected")
                            break
                        distance = float(data)
                        self.messenger.send("position_data", [distance])
                    except:
                        pass
                        # print(f"Error receiving position data: {e}")
                        # accept exception as e
                self.position_client.close()
            except Exception as e:
                if self.enable_print:
                    print(f"Position socket connection error: {e}")
                time.sleep(1)
                break
        if self.enable_print:
            print("Done accepting OpenCV Data")


options = Options()
app = BowlingGame(options)
app.run()
