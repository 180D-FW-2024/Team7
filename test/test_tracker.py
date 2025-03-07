#!/usr/bin/env python3
"""
Standalone tester for position_tracker.py

This script mimics the socket server part of the bowling game, allowing you
to test the position tracker independently without needing to run the full game.
"""

import socket
import subprocess
import threading
import time
import argparse
import sys
import signal
import os

class PositionTrackerTester:
    def __init__(self, tracker_path="position_tracker", verbose=False, test_duration=30, mock_video_path=None):
        self.verbose = verbose
        self.test_duration = test_duration
        self.mock_video_path = mock_video_path
        self.received_data = []
        self.running = True
        self.tracker_process = None
        self.tracker_path = tracker_path
        
    def setup_socket_server(self):
        """Set up socket server on port 8081 just like the game does"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', 8081))
        self.server_socket.listen(1)
        if self.verbose:
            print("Socket server set up on port 8081")
    
    def accept_connections(self):
        """Accept connections from the position tracker"""
        if self.verbose:
            print("Waiting for position tracker connection...")
            
        try:
            self.server_socket.settimeout(10)  # Wait up to 10 seconds for connection
            self.client_socket, addr = self.server_socket.accept()
            if self.verbose:
                print(f"Connected to position tracker at {addr}")
                
            # Go back to blocking mode for data reception
            self.client_socket.settimeout(None)
            
            # Record start time
            start_time = time.time()
            
            while self.running and (time.time() - start_time < self.test_duration):
                try:
                    data = self.client_socket.recv(1024).decode()
                    if not data:
                        if self.verbose:
                            print("Position tracker disconnected")
                        break
                        
                    # Try to convert to float and store
                    try:
                        distance = float(data)
                        self.received_data.append((time.time() - start_time, distance))
                        if self.verbose:
                            print(f"Received distance: {distance:.2f}")
                    except ValueError:
                        if self.verbose:
                            print(f"Received invalid data: {data}")
                except socket.timeout:
                    if self.verbose:
                        print("Socket timeout, no data received")
                except Exception as e:
                    if self.verbose:
                        print(f"Error receiving data: {e}")
                    break
                    
            if self.verbose:
                print(f"Test completed. Received {len(self.received_data)} data points.")
                
        except socket.timeout:
            print("Connection timeout: Position tracker didn't connect within 10 seconds")
        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            self.cleanup()
    
    def start_tracker(self):
        """Start the position tracker subprocess"""
        # Check if we need to use the path or if it's in current directory
        tracker_script = os.path.join(self.tracker_path, "position_tracker.py")
        if not os.path.exists(tracker_script):
            if os.path.exists("position_tracker.py"):
                tracker_script = "position_tracker.py"
            else:
                print(f"Error: position_tracker.py not found in {self.tracker_path} or current directory")
                return False
        
        # Check for model files
        prototxt_file = os.path.join(self.tracker_path, "deploy.prototxt")
        if not os.path.exists(prototxt_file):
            prototxt_file = "deploy.prototxt"
            if not os.path.exists(prototxt_file):
                print("Warning: deploy.prototxt not found")
        
        model_file = os.path.join(self.tracker_path, "res10_300x300_ssd_iter_140000.caffemodel")
        if not os.path.exists(model_file):
            model_file = "res10_300x300_ssd_iter_140000.caffemodel"
            if not os.path.exists(model_file):
                print("Warning: res10_300x300_ssd_iter_140000.caffemodel not found")
        
        tracker_cmd = [
            "python", 
            tracker_script,
            "--prototxt", prototxt_file,
            "--model", model_file,
        ]
    
        if self.mock_video_path:
            tracker_cmd.extend(["--video", self.mock_video_path])
            
        if self.verbose:
            print(f"Starting position tracker: {' '.join(tracker_cmd)}")
            
        try:
            self.tracker_process = subprocess.Popen(tracker_cmd)
            if self.verbose:
                print("Position tracker process started")
            return True
        except Exception as e:
            print(f"Failed to start position tracker: {e}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            
        # Close server socket
        if hasattr(self, 'server_socket'):
            try:
                self.server_socket.close()
            except:
                pass
                
        # Terminate tracker process
        if self.tracker_process:
            try:
                self.tracker_process.terminate()
                self.tracker_process.wait(timeout=5)
            except:
                if self.verbose:
                    print("Warning: Could not terminate tracker process cleanly")
                try:
                    self.tracker_process.kill()
                except:
                    pass
                
    def save_test_results(self, filename=None):
        """Save test results to a CSV file and a summary report"""
        if not self.received_data:
            print("No data to save")
            return False
            
        if filename is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"tracker_test_{timestamp}"
        
        # Save raw data to CSV
        csv_file = f"{filename}_data.csv"
        with open(csv_file, 'w') as f:
            f.write("timestamp,distance\n")
            for timestamp, distance in self.received_data:
                f.write(f"{timestamp:.3f},{distance:.2f}\n")
        
        # Calculate statistics for summary report
        distances = [d for _, d in self.received_data]
        timestamps = [t for t, _ in self.received_data]
        
        avg_distance = sum(distances) / len(distances)
        min_distance = min(distances)
        max_distance = max(distances)
        range_distance = max_distance - min_distance
        
        # Calculate data rate
        if len(timestamps) > 1:
            data_rate = (len(timestamps) - 1) / (timestamps[-1] - timestamps[0])
        else:
            data_rate = 0
        
        # Calculate movement metrics
        if len(distances) > 10:
            changes = [abs(distances[i] - distances[i-1]) for i in range(1, len(distances))]
            avg_movement = sum(changes) / len(changes)
            max_movement = max(changes)
        else:
            avg_movement = 0
            max_movement = 0
        
        # Create summary report
        report_file = f"{filename}_report.txt"
        with open(report_file, 'w') as f:
            f.write("=== Position Tracker Test Results ===\n")
            f.write(f"Test date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test duration: {self.test_duration:.1f} seconds\n")
            f.write(f"Data points received: {len(self.received_data)}\n")
            f.write(f"Data rate: {data_rate:.2f} points/sec\n\n")
            
            f.write("=== Position Data ===\n")
            f.write(f"Average distance from center: {avg_distance:.2f}\n")
            f.write(f"Min distance: {min_distance:.2f}\n")
            f.write(f"Max distance: {max_distance:.2f}\n")
            f.write(f"Range: {range_distance:.2f}\n\n")
            
            f.write("=== Movement Analysis ===\n")
            f.write(f"Average movement between frames: {avg_movement:.2f}\n")
            f.write(f"Maximum movement between frames: {max_movement:.2f}\n")
            
            # Add assessment
            f.write("\n=== Assessment ===\n")
            if data_rate < 10:
                f.write("WARNING: Low data rate. Check tracker performance.\n")
            else:
                f.write("Data rate is good.\n")
                
            if range_distance < 10:
                f.write("WARNING: Very little position variation detected.\n")
            else:
                f.write("Position tracking range is good.\n")
                
            if avg_movement < 1:
                f.write("WARNING: Very little movement detected.\n")
            else:
                f.write("Movement detection is working correctly.\n")
        
        print(f"Results saved to {csv_file} and {report_file}")
        return True

    
    def analyze_results(self):
        """Analyze the collected distance data"""
        if not self.received_data:
            print("No data was received from the position tracker.")
            return False
            
        # Basic statistics
        distances = [d for _, d in self.received_data]
        timestamps = [t for t, _ in self.received_data]
        
        avg_distance = sum(distances) / len(distances)
        min_distance = min(distances)
        max_distance = max(distances)
        range_distance = max_distance - min_distance
        
        # Calculate data rate
        if len(timestamps) > 1:
            data_rate = (len(timestamps) - 1) / (timestamps[-1] - timestamps[0])
        else:
            data_rate = 0
        
        # Print analysis
        print("\n=== Position Tracker Test Results ===")
        print(f"Test duration: {self.test_duration:.1f} seconds")
        print(f"Data points received: {len(self.received_data)}")
        print(f"Data rate: {data_rate:.2f} points/sec")
        print(f"Average distance from center: {avg_distance:.2f}")
        print(f"Range of distances: {min_distance:.2f} to {max_distance:.2f} (range: {range_distance:.2f})")
        
        if range_distance < 1.0:
            print("\nWARNING: Very little variation in distance values. The tracker may not be detecting movement correctly.")
            
        if abs(avg_distance) > 200:
            print("\nWARNING: Extreme distance values detected. The tracker may be miscalibrated or detecting objects incorrectly.")
        
        # Movement analysis
        if len(distances) > 10:
            changes = [distances[i] - distances[i-1] for i in range(1, len(distances))]
            movement_detected = any(abs(change) > 10 for change in changes)
            
            if movement_detected:
                print("\nMovement detected during the test. The tracker appears to be responding to changes in position.")
            else:
                print("\nLittle or no movement detected. Try moving in front of the camera to verify tracking.")
                
        return True
    
    def run_test(self):
        """Run the full test"""
        try:
            # Setup socket server first
            self.setup_socket_server()
            
            # Start socket accepting thread
            socket_thread = threading.Thread(target=self.accept_connections)
            socket_thread.daemon = True
            socket_thread.start()
            
            time.sleep(1)
            
            # Start the tracker process
            if not self.start_tracker():
                return False
            
            # Wait for test to complete
            if self.verbose:
                print(f"Test running for {self.test_duration} seconds...")
                
            # Wait for socket thread to finish (or timeout)
            socket_thread.join(self.test_duration + 15)  # Add buffer time
            
            if self.analyze_results():
                self.save_test_results()
                return True
            
            return self.analyze_results()
           
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        finally:
            self.cleanup()
            
        return False


def main():
    """Command line interface for the tester"""
    parser = argparse.ArgumentParser(description='Test position_tracker.py without the main game')
    parser.add_argument('-p', '--tracker-path', default='position_tracker', 
                        help='Path to the position_tracker directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-t', '--time', type=float, default=30, help='Test duration in seconds')
    parser.add_argument('--video', help='Path to mock video file for testing (requires position_tracker.py modification)')
    
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nInterrupted by user. Cleaning up...")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the test
    tester = PositionTrackerTester(
        tracker_path=args.tracker_path,
        verbose=args.verbose, 
        test_duration=args.time, 
        mock_video_path=args.video
    )
    success = tester.run_test()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()