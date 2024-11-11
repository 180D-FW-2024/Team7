import socket
from network.config import SERVER_IP, PORT
from logger import get_logger

logger = get_logger(__name__)


#tcp client base

def connect_server():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))
        logger.info("Connected to server")
        return client_socket
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return None

def send_data(client_socket, data):
    try:
        client_socket.send(data.encode())
        logger.info(f"Data sent: {data}")
        
        # Receive acknowledgment from the server
        ack = client_socket.recv(1024)
        logger.info(f"Acknowledgment received: {ack.decode()}")
    except Exception as e:
        logger.error(f"Failed to send data: {e}")