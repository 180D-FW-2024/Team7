#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import loadPrcFile, TransparencyAttrib
import simplepbr
from bowling_mechanics import BowlingMechanics
import socket, threading, subprocess, atexit, time

loadPrcFile("../config/conf.prc")

class BowlingGame(ShowBase):
    def __init__(self):
        super().__init__()
        simplepbr.init()

        # setup camera
        self.disable_mouse()
        self.camera.setPos(-30, -10, 0)
        self.camera.setHpr(-75, 0, 90)

        # Set up crosshairs, this will be via camera connection
        crosshairs = OnscreenImage(
            image="../images/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        # SETTING UP SOCKET CONNECTION AND GAME
        # set up socket to receive data from ble_central
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8080))
        self.server_socket.listen(1)
        print("setting up imu socket")

        # creating a separate process to run ble_central
        self.ble_process = subprocess.Popen(['python', '../ble/ble_central_2.py'])

        # Accept connections in a separate thread
        self.socket_thread = threading.Thread(target=self.accept_connections)
        self.socket_thread.daemon = True
        self.socket_thread.start()
        print("thread started for imu")


        #### BALL POSITION SOCKET
        self.position_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position_socket.bind(('localhost', 8081))  # Use different port
        self.position_socket.listen(1)
        print("setting up camera socket")
        self.camera_process = subprocess.Popen([
            'python',
            '../position_tracker/position_tracker.py',
            '--prototxt',
            '../position_tracker/deploy.prototxt',  # Add full relative path
            '--model',
            '../position_tracker/res10_300x300_ssd_iter_140000.caffemodel'  # Add full relative path
        ])
        self.position_socket_thread = threading.Thread(target=self.accept_position_connections)
        self.position_socket_thread.daemon = True
        self.position_socket_thread.start()
        # initialize the game
        self.bowling_mechanics = BowlingMechanics(self)

        # cleaning up processes and sockets
        self.accept('exit', self.cleanup)
        self.accept('accel_data', self.bowling_mechanics.handle_accel_update)
        atexit.register(self.cleanup)

    def cleanup(self):
        if hasattr(self, 'ble_process'):
            self.ble_process.terminate()
            print("killed ble process")
        if hasattr(self, 'camera_process'):
            self.camera_process.terminate()
        if hasattr(self, 'server_socket'):
            print("killed server socket")
            self.server_socket.close()
        if hasattr(self, 'client_socket'):
            self.client_socket.close()
            print("killed client socket")

    def accept_connections(self):
        print("Waiting for BLE client connection...")
        while True:
            try:
                self.client_socket, addr = self.server_socket.accept()
                print(f"Connected to BLE client at {addr}")
                while True:
                    try:
                        data = self.client_socket.recv(1024).decode()
                        if not data:
                            print("Client disconnected")
                            break
                        accel_x, accel_y, accel_z = map(float, data.split(','))
                        print("from main", accel_x, accel_y, accel_z)
                        self.messenger.send('accel_data', [accel_x, accel_y, accel_z])
                    except Exception as e:
                        print(f"Error receiving data: {e}")
                        break

                self.client_socket.close()
            except Exception as e:
                print(f"Socket connection error: {e}")
                time.sleep(1)

    def accept_position_connections(self):
        print("Waiting for position tracker connection...")
        while True:
            try:
                self.position_client, addr = self.position_socket.accept()
                print(f"Connected to position tracker at {addr}")
                while True:
                    try:
                        data = self.position_client.recv(1024).decode()
                        if not data:
                            print("Position tracker disconnected")
                            break
                        distance = float(data)
                        self.messenger.send('position_data', [distance])
                    except Exception as e:
                        print(f"Error receiving position data: {e}")
                        break
                self.position_client.close()
            except Exception as e:
                print(f"Position socket connection error: {e}")
                time.sleep(1)

app = BowlingGame()
app.run()
