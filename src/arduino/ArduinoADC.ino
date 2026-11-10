const int sensorPin = A0;

float calculateRMS() {

  // Get time since board started, setup other variables
  unsigned long start = millis();
  long sumRaw = 0;
  long sumSquares = 0;
  int samples = 0;
  
  	// Loop that runs for 500 ms, (start minus current times less than 500)
  	// Read raw voltage value, then:
	//  	take raw, add to sum raw
	//	take raw, square raw, add to sum squares
	//	increment samples by one
  while (millis() - start < 500) {
    int raw = analogRead(sensorPin);
    sumRaw += raw;
    sumSquares += (long)raw * raw;
    samples++;
  }

  	// If no samples taken, return early. This COULD happen if for some 
  	// reason, there's an issue taking samples within the given time (though 
	// theoretically, this SHOULDN'T be possible; while loop ensures at least 
	// one sample is taken).
  if (samples == 0) return 0.0;
  
  // Mean is true average. I trust this one more...
  float mean = sumRaw / (float)samples;
 
  // RMS is root mean sum, we send this out instead of the true average...
  float rmsRaw = sqrt((sumSquares / (float)samples) - mean * mean);
  // float rmsRaw = sqrt((sumSquares / (float)samples)); // Take out the subtraction of mean^2

  // Completely unused...
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