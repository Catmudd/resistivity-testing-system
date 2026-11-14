// #define DEBUG

const int SENSOR_PIN = A0;
const double ANALOG_UNIT_MAX = 1024;          // Maximum units in an Arduino analog read
const double ANALOG_VOLTAGE_MAX = 5;          // Maximum voltage Arduino can read
const double SENSOR_IN_VOLTAGE_MAX = 250;     // Maximum voltage ZMPT101B can read
const double SENSOR_OUT_VOLTAGE_MAX = 5;      // "VCC" of ZMPT101B, should be same as ANALOG_VOLTAGE_MAX

const int RMS_NUM_SAMPLES = 32;               // RMS number of samples
const int RMS_WAIT_TIME = 1;                  // RMS sample wait time in seconds

double getTrueVoltage()
{
  // 1) Raw 0 to ANALOG_UNIT_MAX analog read (representing 0V to 5V from the ZMPT101B).
  // 2) Convert analog read to actual voltage coming in from ZMPT101B.
  // 3) Convert voltage coming in from ZMPT101B to voltage actually sensed by ZMPT101B.
  double rawUnit = analogRead(SENSOR_PIN);
  double rawVolt = rawUnit * (ANALOG_VOLTAGE_MAX / ANALOG_UNIT_MAX);
  double trueVolt = (rawVolt - (SENSOR_OUT_VOLTAGE_MAX / 2)) * ((SENSOR_IN_VOLTAGE_MAX * 2) / SENSOR_OUT_VOLTAGE_MAX);

#ifdef DEBUG
  Serial.print("rawUnit: ");
  Serial.print(rawUnit);
  Serial.print("\n");

  Serial.print("rawVolt: ");
  Serial.print(rawVolt);
  Serial.print("\n");

  Serial.print("trueVolt: ");
  Serial.print(trueVolt);
  Serial.print("\n");
#endif

  return trueVolt;
}

double getTrueVoltageRMS()
{
  double sumSamples = 0;
  double sumSquares = 0;

  // Take NUM_SAMPLES samples
  for(int i = 0; i < RMS_NUM_SAMPLES; i++)
  {
    double sample = getTrueVoltage();
    sumSamples += sample;
    sumSquares += sample * sample;
    delay(RMS_WAIT_TIME);
  }

  double trueMean = sumSamples / RMS_NUM_SAMPLES;
  double trueRMS = sqrt(sumSquares / RMS_NUM_SAMPLES);

#ifdef DEBUG
  Serial.print("trueMean: ");
  Serial.print(trueMean);
  Serial.print("\n");

  Serial.print("trueRMS: ");
  Serial.print(trueRMS);
  Serial.print("\n");
#endif

  return trueRMS;
}

double getTrueVoltageRMSNormalized()
{
  return getTrueVoltageRMS() * sqrt(2.0);
}

void setup() 
{
  Serial.begin(9600);
}

void loop() 
{
  if (Serial.available() > 0) 
  {
    char cmd = Serial.read();
    if (cmd == 'A') 
    {
      double rmsn = getTrueVoltageRMS(); // Do not normalize?
      Serial.println(rmsn, 4);  // Send as double with 4 decimals
    }
  }
}