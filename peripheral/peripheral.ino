/****************************************************************
 * peripheral.ino
 * Adapted from ICM 20948 Arduino Library Demo
 * and esp32-c6 qwiic pocket BLE notify example
 * 
 * Uncomment all SERIAL_PORT.print to print data via serial
 ***************************************************************/

#include "ICM_20948.h" // Click here to get the library: http://librarymanager/All#SparkFun_ICM_20948_IMU

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

AccelPacket accelPacket;
GyroPacket gyroPacket;

void setup() {

  imu_setup();

  accelPacket.accX = 0.0;
  accelPacket.accY = 0.0;
  accelPacket.accZ = 0.0;

  gyroPacket.gyrX = 0.0;
  gyroPacket.gyrY = 0.0;
  gyroPacket.gyrZ = 0.0;

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
  ap->accX = sensor->accX();
  ap->accY = sensor->accY();
  ap->accZ = sensor->accZ();

  gp->gyrX = sensor->gyrX();
  gp->gyrY = sensor->gyrY();
  gp->gyrZ = sensor->gyrZ();
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
