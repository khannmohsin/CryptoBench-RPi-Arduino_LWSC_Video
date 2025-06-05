#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;

bool measurementMode = false;
unsigned long previousMillis = 0;
const long interval = 1000; // Interval in milliseconds
float averagePower = 0.0; // Declare averagePower outside setup()
float totalEnergy_mJ = 0.0;
String previousCipher;

void setup() {
  Serial.begin(9600);
  while (!Serial){
    delay(1);
  }

  if (!ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) { delay(10); }
  }
  else {
    Serial.println("INA219 Chip Found. Measuring average voltage of Raspberry Pi.");
    unsigned long startTime = millis();  // Record the start time
    unsigned long measurementDuration = 30000;  // Duration in milliseconds (30 seconds)
    
    float totalPower = 0.0;  // Variable to store the total power
    int numSamples = 0;  // Variable to store the number of samples

    // Loop for 10 seconds
    while (millis() - startTime < measurementDuration) {
      float power_mW = ina219.getPower_mW();
      
      // Accumulate total power
      totalPower += power_mW;
      numSamples++;

      // Print other measurements as before
      // float shuntvoltage = ina219.getShuntVoltage_mV();
      // float busvoltage = ina219.getBusVoltage_V();
      // float current_mA = ina219.getCurrent_mA();
      // float loadvoltage = busvoltage + (shuntvoltage / 1000);
      
      // Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
      // Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
      // Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
      // Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
      // Serial.print("Power:         "); Serial.print(power_mW); Serial.println(" mW");
      // Serial.println("");

      delay(1000); // Add delay to make sure measurements are taken every second
    }

    // Calculate average power
    averagePower = totalPower / numSamples; // Remove the 'float' before averagePower
    // Serial.print("Average Power: "); Serial.print(averagePower); Serial.println(" mW");
  }
  Serial.print("Average Power: "); Serial.print(averagePower); Serial.println(" mW");
}

void loop() {
  // Serial.print("Average Power: "); Serial.print(averagePower); Serial.println(" mW");
  static float totalEnergy = 0.0; // Declared as static to persist its value across loop iterations
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    // Serial.println(data);
    String ciphers[] = {"aes", "py-aes", "present", "py-present","xtea" ,"py-xtea", "clefia", "simon", "speck", "py-simon", "py-speck", "ascon" , "grain-128a", "mickey", "trivium", "salsa", "sosemanuk", "py-rabbit", "grain-v1"};
    bool foundCipher = false; // Flag to track if any cipher is found
    for (int i = 0; i < sizeof(ciphers) / sizeof(ciphers[0]); i++) {
      if (data.indexOf(ciphers[i]) != -1) {
        // Cipher found in the received string
        // Your code here
        Serial.println("Received '" + ciphers[i] + "', entering measurement mode...");
        measurementMode = true;
        previousCipher = data;
        previousMillis = millis();
        foundCipher = true; // Set the flag to true
        break; // Exit the loop once a cipher is found
      }
    }
    
    if (!foundCipher) {
      Serial.print(previousCipher); Serial.print(": "); Serial.print(totalEnergy);
      Serial.println("");
      Serial.print("Completed measuring the energy consumption in mJ for "); Serial.print(previousCipher);
      Serial.println("");
      measurementMode = false;
      totalEnergy = 0.0;
    }
  }

  // If in measurement mode, take measurements at regular intervals
  if (measurementMode) {
    unsigned long currentMillis = millis();
    // Serial.print("Current Time: "); Serial.print(currentMillis); Serial.println(" mS");
    unsigned long elapsedTime = currentMillis - previousMillis;
    // Serial.print("Initial Elapsed Time: "); Serial.print(elapsedTime); Serial.println(" mS");
    if (elapsedTime >= interval) {
      previousMillis = currentMillis;
      // float shuntvoltage = ina219.getShuntVoltage_mV();
      // float busvoltage = ina219.getBusVoltage_V();
      // float current_mA = ina219.getCurrent_mA();
      float power_mW = ina219.getPower_mW();
      // Serial.print("Pawar Kuta yeth: "); Serial.print(power_mW); Serial.println(" mW");
      // float loadvoltage = busvoltage + (shuntvoltage / 1000);

      float enc_power_mW = power_mW - averagePower;
      // Serial.print("Encryption Power: "); Serial.print(enc_power_mW); Serial.println(" mW");
      // Serial.print("Elapsed Time: "); Serial.print(elapsedTime); Serial.println(" mS");
      float energy = (enc_power_mW /1000.0) * (elapsedTime / 1000.0);
      // Serial.print("Energy in Joules: "); Serial.print(energy); Serial.println(" J");
      float energy_mJ = energy * 1000;
      // Serial.print("Energy: "); Serial.print(energy_mJ); Serial.println(" mJ");
      totalEnergy += energy_mJ;
  
      // Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
      // Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
      // Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
      // Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
    }
  }
}




