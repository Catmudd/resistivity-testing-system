const int sensorPin = A0;

float calculateRMS() {
  unsigned long start = millis();
  long sumRaw = 0;
  long sumSquares = 0;
  int samples = 0;
  
  while (millis() - start < 500) {
    int raw = analogRead(sensorPin);
    sumRaw += raw;
    sumSquares += (long)raw * raw;
    samples++;
  }
  if (samples == 0) return 0.0;
  
  float mean = sumRaw / (float)samples;
  float rmsRaw = sqrt((sumSquares / (float)samples) - mean * mean);
  float voltageOutRMS = abs(rmsRaw-12.4) * (250.0 / 300);
  
  return rmsRaw;  // Raw output voltage RMS from ZMPT101B
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'A') {
      float rms = calculateRMS();
      Serial.println(rms, 4);  // Send as float with 4 decimals
    }
  }
}