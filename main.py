from imu.imu_handler import initialize_imu, read_imu_data
from network.wifi_connect import connect_wifi
from network.tcp_client import connect_server, send_data

logger = get_logger(__name__)

def main():
  
    wlan = connect_wifi()
    if not wlan:
        logger.error("Failed to connect to Wi-Fi")
        return
    client_socket = connect_server()
    
    if client_socket is None:
        logger.error("Failed to connect to server")
        return
    
    try:
        while True:
            # Read IMU data
            accel_data, gyro_data = read_imu_data()
            logger.info(f"Accelerometer: {accel_data}, Gyroscope: {gyro_data}")

            # Send IMU data to the server
            send_data(client_socket, f"Accel: {accel_data}, Gyro: {gyro_data}")
            utime.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        client_socket.close()
        logger.info("Disconnected from server")

if __name__ == "__main__":
    main()