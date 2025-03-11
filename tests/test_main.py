import unittest
from unittest.mock import patch, MagicMock, call
import socket
import threading
import sys
import os

# Add the parent directory to sys.path to import the game module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a mock for bowling_mechanics module BEFORE importing from main
# This is crucial because main.py imports bowling_mechanics directly
mock_bowling_mechanics = MagicMock()
mock_intro_screen = MagicMock()
mock_bowling_mechanics.BowlingMechanics = MagicMock()
mock_intro_screen.IntroScreen = MagicMock()

# Apply module mocks using patch.dict
module_patches = [
    patch.dict('sys.modules', {'bowling_mechanics': mock_bowling_mechanics}),
    patch.dict('sys.modules', {'intro_screen': mock_intro_screen})
]
for p in module_patches:
    p.start()

class TestOptions(unittest.TestCase):
    """Test the Options class functionality"""

    def test_default_options(self):
        # Need to mock sys.argv first
        with patch('sys.argv', ['main.py']):
            # Import directly from the module location
            from main.main import Options
            options = Options()
            
            # Check default values
            self.assertFalse(options.present)
            self.assertFalse(options.disable_speech)
            self.assertFalse(options.enable_print)
            self.assertFalse(options.enable_print_power_mag)
    
    def test_command_line_options(self):
        # Test with various command line arguments
        with patch('sys.argv', ['main.py', '-p', '-ds', '-m']):
            from main.main import Options
            options = Options()
            
            # Check parsed values
            self.assertTrue(options.present)
            self.assertTrue(options.disable_speech)
            self.assertTrue(options.enable_print)
            self.assertTrue(options.enable_print_power_mag)
    
    def test_partial_options(self):
        # Test with just some options
        with patch('sys.argv', ['main.py', '-p']):
            from main.main import Options
            options = Options()
            
            # Check parsed values
            self.assertTrue(options.present)
            self.assertFalse(options.disable_speech)
            self.assertTrue(options.enable_print)
            self.assertFalse(options.enable_print_power_mag)


class MockShowBase:
    """Mock for ShowBase to avoid importing Panda3D"""
    def __init__(self):
        self.camera = MagicMock()
        self.disable_mouse = MagicMock()
        self.accept = MagicMock()
        self.messenger = MagicMock()


class TestBowlingGame(unittest.TestCase):
    """Test the BowlingGame class functionality"""
    
    def setUp(self):
        # Mock modules first
        modules_to_mock = {
            'direct.showbase.ShowBase': MagicMock(),
            'direct.gui.OnscreenImage': MagicMock(),
            'panda3d.core': MagicMock(),
            'simplepbr': MagicMock(),
        }
        
        # Create patches for the modules
        self.module_patches = []
        for module_name, mock_obj in modules_to_mock.items():
            patch_obj = patch.dict('sys.modules', {module_name: mock_obj})
            patch_obj.start()
            self.module_patches.append(patch_obj)
        
        # Other mocks for specific functions
        self.socket_patch = patch('socket.socket')
        self.thread_patch = patch('threading.Thread')
        self.subprocess_patch = patch('subprocess.Popen')
        self.atexit_patch = patch('atexit.register')
        self.loadprc_patch = patch('main.main.loadPrcFile')
        
        # Start remaining patches
        self.mock_socket = self.socket_patch.start()
        self.mock_thread = self.thread_patch.start()
        self.mock_subprocess = self.subprocess_patch.start()
        self.mock_atexit = self.atexit_patch.start()
        self.mock_loadprc = self.loadprc_patch.start()
        
        # Keep track of the socket instances we'll create
        self.mock_socket.return_value = MagicMock()
        
        # Create ShowBase replacement
        self.mock_showbase = MockShowBase
        
        # Patch ShowBase
        self.showbase_patch = patch('main.main.ShowBase', self.mock_showbase)
        self.showbase_patch.start()
        
        # Create mock options
        self.options = MagicMock()
        self.options.enable_print = True

    def tearDown(self):
        # Stop all patches
        self.socket_patch.stop()
        self.thread_patch.stop()
        self.subprocess_patch.stop()
        self.atexit_patch.stop()
        self.showbase_patch.stop()
        self.loadprc_patch.stop()
        
        # Stop module patches
        for patch_obj in self.module_patches:
            patch_obj.stop()
    
    def test_init(self):
        """Test the initialization of BowlingGame"""
        from main.main import BowlingGame
        
        # Create game instance
        game = BowlingGame(self.options)
        
        # Since we've completely replaced the modules, we can only check that
        # the game was created without errors and has the right attributes
        self.assertEqual(game.options, self.options)
        self.assertEqual(game.enable_print, self.options.enable_print)
        
        # Verify that the intro screen was accessed
        # Note: Full verification is difficult due to how we're mocking modules
        self.assertTrue(hasattr(game, 'intro_screen'))
    
    def test_cleanup_basic(self):
        """Test basic functionality of the cleanup method"""
        from main.main import BowlingGame
        
        # Create game instance
        game = BowlingGame(self.options)
        
        # Create mock attributes that should be cleaned up
        game.ble_process = MagicMock()
        game.camera_process = MagicMock()
        game.position_socket = MagicMock()
        game.server_socket = MagicMock()
        game.client_socket = MagicMock()
        
        # Call cleanup
        game.cleanup()
        
        # Verify processes are terminated
        game.ble_process.terminate.assert_called_once()
        game.camera_process.terminate.assert_called_once()


if __name__ == '__main__':
    unittest.main()
    
    # Clean up module patches when done
    for p in module_patches:
        p.stop()