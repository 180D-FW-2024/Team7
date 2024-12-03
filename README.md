# BerryIMU v3 Module

The original repository for this code can be found at:

https://github.com/oliviamiller/Berry-IMU/tree/main

## Initial Setup

1. Log into the Raspberry Pi 4
  - Use SSH to access the RPi terminal
  ```ssh username@your-rpi-address```
  - Replace address with your local address
  - Default username:
  ``pi``
  - Default password:
  ``raspberry``
2. Activate virtual environment
  ```cd ~/Berry-IMU```
  
3. Activate local Python environment
  ```source .venv/bin/activate```

## Starting the Viam Agent

1. Check Viam Agent Status if agent running:
``ps aux| grep viam``
  
  - If not running, start VIam Agent:
  ```sudo systemctl start viam-agent```
  
2. Restart the Viam Agent (if needed)
  ```sudo systemctl resatrt viam-agent```
3. Stopping Viam
  ```sudo systemctl stop viam-agent```
4. View Logs to debug issues
  ```sudo journalctl -u viam-agent```

## API Key Usage

- Every user interacting with Viam requires a unique API key
  - Log into Viam
  - Navigate to Settings->API Keys-Create Key
  - Assign required permission for new user
- Set API key for your machine in your script
  ```
  opts = RobotClient.Options.with_api_key(
    api_key='<API-KEY>',
    api_key_id='<API-KEY-ID>'
    
  ```
  
## Dependencies

Ensure the following dependencies are installed

1. Required Packages
  
  ```
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip libi2c-dev i2c-tools
  ```
2. Install Python dependencies

  ```
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
3. I2C Communications Setup

  ```
  sudo raspi-config
  ```
4. Check I2C devices: verify if IMU is detected
  
  ```i2cdetect - y 1```
  
## Running the Module

1. Run the main script

```
  cd ~/Berry-IMU/src
  python -m main
```

2. Test API Connection: Run connection test script

```
python connect_machine.py
```

## Acknowledgments
This project uses the Berry-IMU library by Olivia Miller and contributors, licensed under the [Apache License 2.0](https://github.com/oliviamiller/Berry-IMU/blob/main/LICENSE).

The project has been modified to include a connect_machine.py file.