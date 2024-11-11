import network
import utime
from network.config import SSID, PASSWORD

#wifi base

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    logger.info("Connecting to Wi-Fi...")
    
    MAX_RETRIES = 10 #Time out
    attempts = 0

    while not wlan.isconnected() and attempts < MAX_RETRIES:
        logger.info(".", end="")
        utime.sleep(1)
        attempts += 1
        
        if wlan.isconnected():
            logger.info("Connected to Wi-Fi with IP configuration: %s", wlan.ifconfig())
        else:
            logger.error("Failed to connect to Wi-Fi")

    return wlan