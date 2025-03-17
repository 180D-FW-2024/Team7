/****************************************************************
 * remote.ino
 * Adapted from ICM 20948 Arduino Library Demo
 * and esp32-c6 qwiic pocket BLE notify example
 * 
 * Uncomment all SERIAL_PORT.print to print data via serial
 ***************************************************************/

#include "ICM_20948.h"

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <BLE2901.h>

// IMU defs
#define SERIAL_PORT Serial
#define WIRE_PORT Wire // Your desired Wire port.
// The value of the last bit of the I2C address.
// On the SparkFun 9DoF IMU breakout the default is 1, and when the ADR jumper is closed the value becomes 0
#define AD0_VAL 1

ICM_20948_I2C myICM; // create an ICM_20948_I2C object

// init ble objs
BLEServer *pServer = NULL;
BLECharacteristic *pAccelCharacteristic = NULL;
BLECharacteristic *pGyroCharacteristic = NULL;
BLE2901 *descriptor_2901 = NULL;

bool deviceConnected = false;
bool oldDeviceConnected = false;
uint32_t value = 0;

#define SERVICE_UUID        "1b9998a2-1234-5678-1234-56789abcdef0"
#define ACCEL_CHARACTERISTIC_UUID "2713d05a-1234-5678-1234-56789abcdef1"
#define GYRO_CHARACTERISTIC_UUID "2713d05b-1234-5678-1234-56789abcdef2"

class KalmanFilter {
private:
  float Q = 0.025; //Process noise
  float R = 0.5; // measurement noise
  float P = 0.0; // Estimation error
  float K = 0.0; // Kalman gain
  float X = 0.0; // state estimate
public:
  void setParameters(float process_noise, float measurement_noise) {
    Q = process_noise;
    R = measurement_noise;
  }

  float update(float measurements) {
    // prediction update
    P = P + Q;

    // measurement update
    K = P / (P + R);
    X = X + K * (measurements - X);
    P = (1 - K) * P;

    return X;
  }
};

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer) {
    deviceConnected = false;
  }
};

typedef struct __attribute__((packed)) {
    float accX;
    float accY;
    float accZ;
} AccelPacket;

typedef struct __attribute__((packed)) {
    float gyrX;
    float gyrY;
    float gyrZ;
} GyroPacket;

typedef struct {
    float roll;
    float pitch;
    float yaw;
} Orientation;

const float GRAVITY = 9.81;
Orientation deviceOrientation;

// Calculate device orientation from gyro data
void updateOrientation(GyroPacket *gp, float deltaTime) {
    deviceOrientation.roll += gp->gyrX * deltaTime;
    deviceOrientation.pitch += gp->gyrY * deltaTime;
    deviceOrientation.yaw += gp->gyrZ * deltaTime;
}

// Remove effect of gravity
void removeGravity(AccelPacket *ap, Orientation *orientation) {
    // Convert orientation to radians
    float rollRad = orientation->roll * M_PI / 180.0;
    float pitchRad = orientation->pitch * M_PI / 180.0;
    
    // Calculate gravity components in sensor frame
    float gravityX = GRAVITY * sin(pitchRad);
    float gravityY = -GRAVITY * cos(pitchRad) * sin(rollRad);
    float gravityZ = -GRAVITY * cos(pitchRad) * cos(rollRad);
    
    // Remove gravity from accelerometer readings
    ap->accX -= gravityX;
    ap->accY -= gravityY;
    ap->accZ -= gravityZ;
}

AccelPacket accelPacket;
GyroPacket gyroPacket;

// Create Kalman filter instances
KalmanFilter kalmanAccX, kalmanAccY, kalmanAccZ;
KalmanFilter kalmanGyrX, kalmanGyrY, kalmanGyrZ;

void setup() {

  imu_setup();

  // Initialize the packets
  accelPacket.accX = 0.0;
  accelPacket.accY = 0.0;
  accelPacket.accZ = 0.0;

  gyroPacket.gyrX = 0.0;
  gyroPacket.gyrY = 0.0;
  gyroPacket.gyrZ = 0.0;

  // Configure Kalman filters
  // Accel usually needs more aggressive filtering

  kalmanAccX.setParameters(0.025, 0.5);
  kalmanAccY.setParameters(0.025, 0.5);
  kalmanAccZ.setParameters(0.025, 0.5);

  kalmanGyrX.setParameters(0.025, 0.5);
  kalmanGyrY.setParameters(0.025, 0.5);
  kalmanGyrZ.setParameters(0.025, 0.5);

  // Init orientation
  deviceOrientation.roll = 0.0;
  deviceOrientation.pitch = 0.0;
  deviceOrientation.yaw = 0.0;

  // SERIAL_PORT.begin(115200); called in imu_setup()

  // Create the BLE Device
  BLEDevice::init("IMU_Sensor");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create Accel Characteristic
  pAccelCharacteristic = pService->createCharacteristic(
    ACCEL_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE
  );

  // Create Gyro Characteristic
  pGyroCharacteristic = pService->createCharacteristic(
    GYRO_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE
  );

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  // SERIAL_PORT.println("Waiting for a client connection to notify...");
}

void loop()
{
  // notify changed value
  if (deviceConnected) {
    
    if (myICM.dataReady())
    {
      myICM.getAGMT();         // The values are only updated when you call 'getAGMT'
                              //    printRawAGMT( myICM.agmt );     // Uncomment this to see the raw values, taken directly from the agmt structure
      // printScaledAGMT(&myICM); // This function takes into account the scale settings from when the measurement was made to calculate the values with units

      populatePackets(&myICM, &accelPacket, &gyroPacket);
      
      delay(30);
    }
    else
    {
      // SERIAL_PORT.println("Waiting for data");
      delay(500);
    }

    pAccelCharacteristic->setValue((uint8_t *)&accelPacket, sizeof(AccelPacket));
    pAccelCharacteristic->notify();
    pGyroCharacteristic->setValue((uint8_t *)&gyroPacket, sizeof(GyroPacket));
    pGyroCharacteristic->notify();
    delay(60); // test different values -- try 90
  }
  // disconnecting
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);                   // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising();  // restart advertising
    // SERIAL_PORT.println("start advertising");
    oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected) {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
  }
}

void imu_setup()
{

  // SERIAL_PORT.begin(115200);
  // while (!SERIAL_PORT)
  // {
  // };

  WIRE_PORT.begin();
  WIRE_PORT.setClock(400000);

  //myICM.enableDebugging(); // Uncomment this line to enable helpful debug messages on Serial

  bool initialized = false;
  while (!initialized)
  {
    myICM.begin(WIRE_PORT, AD0_VAL);

    // SERIAL_PORT.print(F("Initialization of the sensor returned: "));
    // SERIAL_PORT.println(myICM.statusString());
    if (myICM.status != ICM_20948_Stat_Ok)
    {
      // SERIAL_PORT.println("Trying again...");
      delay(500);
    }
    else
    {
      initialized = true;
    }
  }
}

void populatePackets(ICM_20948_I2C *sensor, AccelPacket *ap, GyroPacket *gp) 
{
  static unsigned long lastTime = 0;
  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;

  // Get Data

  ap->accX = sensor->accX() * 9.81 / 1000.0;
  ap->accY = sensor->accY() * 9.81 / 1000.0;
  ap->accZ = sensor->accZ() * 9.81 / 1000.0;

  gp->gyrX = sensor->gyrX();
  gp->gyrY = sensor->gyrY();
  gp->gyrZ = sensor->gyrZ();

  // Update orientation and remove gravity

  updateOrientation(gp, deltaTime);
  removeGravity(ap, &deviceOrientation);

  // Apply Kalman filter

  ap->accX = kalmanAccX.update(ap->accX);
  ap->accY = kalmanAccY.update(ap->accY);
  ap->accZ = kalmanAccZ.update(ap->accZ);

  gp->gyrX = kalmanGyrX.update(gp->gyrX);
  gp->gyrY = kalmanGyrY.update(gp->gyrY);
  gp->gyrZ = kalmanGyrZ.update(gp->gyrZ);

  ap->accX = kalmanAccX.update(ap->accX) * 1000.0 / 9.81;
  ap->accY = kalmanAccY.update(ap->accY) * 1000.0 / 9.81;
  ap->accZ = kalmanAccZ.update(ap->accZ) * 1000.0 / 9.81;

}

// Below here are some helper functions to print the data nicely!

void printPaddedInt16b(int16_t val)
{
  if (val > 0)
  {
    SERIAL_PORT.print(" ");
    if (val < 10000)
    {
      SERIAL_PORT.print("0");
    }
    if (val < 1000)
    {
      SERIAL_PORT.print("0");
    }
    if (val < 100)
    {
      SERIAL_PORT.print("0");
    }
    if (val < 10)
    {
      SERIAL_PORT.print("0");
    }
  }
  else
  {
    SERIAL_PORT.print("-");
    if (abs(val) < 10000)
    {
      SERIAL_PORT.print("0");
    }
    if (abs(val) < 1000)
    {
      SERIAL_PORT.print("0");
    }
    if (abs(val) < 100)
    {
      SERIAL_PORT.print("0");
    }
    if (abs(val) < 10)
    {
      SERIAL_PORT.print("0");
    }
  }
  SERIAL_PORT.print(abs(val));
}

void printRawAGMT(ICM_20948_AGMT_t agmt)
{
  SERIAL_PORT.print("RAW. Acc [ ");
  printPaddedInt16b(agmt.acc.axes.x);
  SERIAL_PORT.print(", ");
  printPaddedInt16b(agmt.acc.axes.y);
  SERIAL_PORT.print(", ");
  printPaddedInt16b(agmt.acc.axes.z);
  SERIAL_PORT.print(" ], Gyr [ ");
  printPaddedInt16b(agmt.gyr.axes.x);
  SERIAL_PORT.print(", ");
  printPaddedInt16b(agmt.gyr.axes.y);
  SERIAL_PORT.print(", ");
  printPaddedInt16b(agmt.gyr.axes.z);
  SERIAL_PORT.print(" ]");
  SERIAL_PORT.println();
}

void printFormattedFloat(float val, uint8_t leading, uint8_t decimals)
{
  float aval = abs(val);
  if (val < 0)
  {
    SERIAL_PORT.print("-");
  }
  else
  {
    SERIAL_PORT.print(" ");
  }
  for (uint8_t indi = 0; indi < leading; indi++)
  {
    uint32_t tenpow = 0;
    if (indi < (leading - 1))
    {
      tenpow = 1;
    }
    for (uint8_t c = 0; c < (leading - 1 - indi); c++)
    {
      tenpow *= 10;
    }
    if (aval < tenpow)
    {
      SERIAL_PORT.print("0");
    }
    else
    {
      break;
    }
  }
  if (val < 0)
  {
    SERIAL_PORT.print(-val, decimals);
  }
  else
  {
    SERIAL_PORT.print(val, decimals);
  }
}

void printScaledAGMT(ICM_20948_I2C *sensor)
{
  SERIAL_PORT.print("Scaled. Acc (mg) [ ");
  printFormattedFloat(sensor->accX(), 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(sensor->accY(), 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(sensor->accZ(), 5, 2);
  SERIAL_PORT.print(" ], Gyr (DPS) [ ");
  printFormattedFloat(sensor->gyrX(), 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(sensor->gyrY(), 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(sensor->gyrZ(), 5, 2);
  SERIAL_PORT.print(" ]");
  SERIAL_PORT.println();
}