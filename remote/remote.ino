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


/*************************************************************************
 * 
 * TUNABLE PARAMETERS GUIDE:
 * 
 * 1. KALMAN FILTER PARAMETERS (in setup())
 *    For Accelerometer:
 *    - Process noise (Q): kalmanAccX.setParameters(0.01, 1.0)
 *      - Lower values (0.001-0.01): More trust in motion model, smoother output
 *      - Higher values (0.1-1.0): More responsive to changes
 *    - Measurement noise (R): Second parameter in setParameters()
 *      - Lower values: More trust in measurements
 *      - Higher values: More trust in predictions
 * 
 *    For Gyroscope:
 *    - Process noise: kalmanGyrX.setParameters(0.1, 0.1)
 *      - Currently less aggressive filtering than accelerometer
 *      - Adjust based on gyro noise characteristics
 * 
 * 2. SWING DETECTION (in isInSwingPhase())
 *    const float SWING_THRESHOLD = 100.0f;
 *    - Determines sensitivity of swing detection
 *    - Lower values: More sensitive, might catch small movements
 *    - Higher values: Only detects more definitive swings
 *    - Typical range: 50-200 depending on mounting position
 * 
 * 3. SAMPLING AND TIMING
 *    - Sample rate in populatePackets(): delay(30)
 *    - Kalman filter dt in KalmanFilter class: float dt = 0.03
 *    - These should match for optimal performance
 * 
 * 4. GRAVITY COMPENSATION
 *    const float GRAVITY = 9.81;
 *    - Standard gravity value
 * 
 * TESTING PROCEDURE:
 * 1. Start with default parameters
 * 2. Monitor serial output using printScaledAGMT()
 * 3. Adjust parameters in this order (recommended order):
 *    a) First tune SWING_THRESHOLD for motion detection
 *    b) Then adjust Kalman parameters for accelerometer
 *    c) Tune gyroscope parameters
 * 
 ******************************************************************************/

// Enhanced KalmanFilter class
class KalmanFilter {
private:
    float x[3] = {0, 0, 0};  // State: [position, velocity, acceleration]
    float P[3][3] = {{1000,0,0},{0,1000,0},{0,0,1000}}; // Covariance matrix
    float dt = 0.03; // Sample time (adjust based on your actual sample rate)
    float A[3][3] = {
        {1, dt, 0.5f*dt*dt},
        {0, 1, dt},
        {0, 0, 1}
    };
    float H[1][3] = {{1, 0, 0}}; // Measurement matrix
    float Q[3][3]; // Process noise
    float R;       // Measurement noise

public:
    void setParameters(float process_noise, float measurement_noise) {
        // Initialize process noise matrix
        float q = process_noise;
        Q[0][0] = q * dt*dt*dt*dt/4;
        Q[0][1] = q * dt*dt*dt/2;
        Q[0][2] = q * dt*dt/2;
        Q[1][0] = q * dt*dt*dt/2;
        Q[1][1] = q * dt*dt;
        Q[1][2] = q * dt;
        Q[2][0] = q * dt*dt/2;
        Q[2][1] = q * dt;
        Q[2][2] = q;
        
        R = measurement_noise;
    }

    float update(float measurement) {
        // Predict step
        float x_pred[3];
        for(int i = 0; i < 3; i++) {
            x_pred[i] = A[i][0]*x[0] + A[i][1]*x[1] + A[i][2]*x[2];
        }
        
        // Update P
        float P_pred[3][3];
        for(int i = 0; i < 3; i++) {
            for(int j = 0; j < 3; j++) {
                P_pred[i][j] = P[i][j] + Q[i][j];
            }
        }
        
        // Kalman gain
        float S = P_pred[0][0] + R;
        float K[3];
        for(int i = 0; i < 3; i++) {
            K[i] = P_pred[i][0] / S;
        }
        
        // Update state
        float innovation = measurement - x_pred[0];
        for(int i = 0; i < 3; i++) {
            x[i] = x_pred[i] + K[i] * innovation;
        }
        
        // Update P
        for(int i = 0; i < 3; i++) {
            for(int j = 0; j < 3; j++) {
                P[i][j] = P_pred[i][j] - K[i] * P_pred[0][j];
            }
        }
        
        return x[0];
    }

    void reset() {
        for(int i = 0; i < 3; i++) {
            x[i] = 0;
            for(int j = 0; j < 3; j++) {
                P[i][j] = (i == j) ? 1000 : 0;
            }
        }
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
const float SWING_THRESHOLD = 100.0f; // Adjust based on testing
Orientation deviceOrientation = {0.0f, 0.0f, 0.0f};
bool inSwingPhase = false;

// Create Kalman filter instances
KalmanFilter kalmanAccX, kalmanAccY, kalmanAccZ;
KalmanFilter kalmanGyrX, kalmanGyrY, kalmanGyrZ;

// Swing phase detection
bool isInSwingPhase(const GyroPacket& gp) {
    float totalAngularVelocity = sqrt(gp.gyrX*gp.gyrX + 
                                    gp.gyrY*gp.gyrY + 
                                    gp.gyrZ*gp.gyrZ);
    return totalAngularVelocity > SWING_THRESHOLD;
}

// Updated orientation calculation
void updateOrientation(GyroPacket *gp, float deltaTime) {
    // Convert to radians
    float dtSec = deltaTime;
    deviceOrientation.roll += gp->gyrX * dtSec;
    deviceOrientation.pitch += gp->gyrY * dtSec;
    deviceOrientation.yaw += gp->gyrZ * dtSec;
    
    // Normalize angles to -180 to 180
    deviceOrientation.roll = fmod(deviceOrientation.roll, 360.0f);
    deviceOrientation.pitch = fmod(deviceOrientation.pitch, 360.0f);
    deviceOrientation.yaw = fmod(deviceOrientation.yaw, 360.0f);
}

// Remove effect of gravity
void removeGravity(AccelPacket *ap, Orientation *orientation) {
    float rollRad = orientation->roll * M_PI / 180.0f;
    float pitchRad = orientation->pitch * M_PI / 180.0f;
    
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

void setup() {

  imu_setup();

  // Initialize the packets

  accelPacket.accX = 0.0;
  accelPacket.accY = 0.0;
  accelPacket.accZ = 0.0;
  // accelPacket.filteredAccX = 0.0;
  // accelPacket.filteredAccY = 0.0;
  // accelPacket.filteredAccZ = 0.0;

  gyroPacket.gyrX = 0.0;
  gyroPacket.gyrY = 0.0;
  gyroPacket.gyrZ = 0.0;
  // gyroPacket.filteredGyrX = 0.0;
  // gyroPacket.filteredGyrY = 0.0;
  // gyroPacket.filteredGyrZ = 0.0;

  ////////////////////////////////////////////////////////////////
  // Kalman filter parameters
  // Process noise: The variance of the noise in the system.
  // Measurement noise: The variance of the noise in the measurements.
  //
  // Smaller values for process noise and measurement noise result in more accurate
  // estimates, but also a higher risk of the filter diverging from the true state.

  //Precise parametters to be determiend durng testing!
  // For acceleration (more aggressive filtering)
  kalmanAccX.setParameters(0.01, 1.0);  // Less process noise, more measurement noise
  kalmanAccY.setParameters(0.01, 1.0);
  kalmanAccZ.setParameters(0.01, 1.0);

  // For gyroscope (less aggressive filtering)
  kalmanGyrX.setParameters(0.1, 0.1);  // More process noise, less measurement noise
  kalmanGyrY.setParameters(0.1, 0.1);
  kalmanGyrZ.setParameters(0.1, 0.1);

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

  // Get Raw Data first
  ap->accX = sensor->accX() * 9.81 / 1000.0;
  ap->accY = sensor->accY() * 9.81 / 1000.0;
  ap->accZ = sensor->accZ() * 9.81 / 1000.0;

  gp->gyrX = sensor->gyrX();
  gp->gyrY = sensor->gyrY();
  gp->gyrZ = sensor->gyrZ();

  // Update orientation using gyro data first
  updateOrientation(gp, deltaTime);

  // Check if we're in swing phase
    bool currentlyInSwing = isInSwingPhase(*gp);
    
    if (currentlyInSwing != inSwingPhase) {
        if (currentlyInSwing) {
            // Reset Kalman filters at start of swing
            kalmanAccX.reset();
            kalmanAccY.reset();
            kalmanAccZ.reset();
        }
        inSwingPhase = currentlyInSwing;
    }
  
  // Remove gravity BEFORE Kalman filtering
  removeGravity(ap, &deviceOrientation);

  if (inSwingPhase) {
        ap->accX = kalmanAccX.update(ap->accX);
        ap->accY = kalmanAccY.update(ap->accY);
        ap->accZ = kalmanAccZ.update(ap->accZ);
        
        gp->gyrX = kalmanGyrX.update(gp->gyrX);
        gp->gyrY = kalmanGyrY.update(gp->gyrY);
        gp->gyrZ = kalmanGyrZ.update(gp->gyrZ);
    }

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
  /*
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
  */

  // Print filtered values
  SERIAL_PORT.print("FILTERED - Acc (m/s^2) [ ");
  printFormattedFloat(filtered_accX, 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(filtered_accY, 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(filtered_accZ, 5, 2);
  SERIAL_PORT.print(" ], Gyr (DPS) [ ");
  printFormattedFloat(filtered_gyrX, 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(filtered_gyrY, 5, 2);
  SERIAL_PORT.print(", ");
  printFormattedFloat(filtered_gyrZ, 5, 2);
  SERIAL_PORT.print(" ]");
  SERIAL_PORT.println();

  // Print swing state
  // SERIAL_PORT.print("Swing State: ");
  // SERIAL_PORT.println(inSwingPhase ? "IN SWING" : "STATIC");
  // SERIAL_PORT.println();
}