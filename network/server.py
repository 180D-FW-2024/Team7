import socket
from logger import get_logger

logger = get_logger(__name__)

HOST = '0.0.0.0' #all interfaces
PORT = 65432

def process_data(data):
    """Process incoming data and return acknowledgement"""
    return "Data received successfully"

def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            logger.info(f"Server is listening on {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                logger.info(f"Connected by {addr}")

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    logger.info(f"Received data: {data.decode()}")

                    # Process the data and send an acknowledgment
                    ack = process_data(data)
                    conn.sendall(ack.encode())

                conn.close()

    except Exception as e:
        logger.error(f"Error occurred: {e}")

if __name__ == "__main__":
    start_server()