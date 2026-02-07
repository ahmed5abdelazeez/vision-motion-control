// Control LED on pin 13 using Serial commands: ON / OFF

const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  while (!Serial) { ; }  // safe for boards like Leonardo/Micro
  Serial.println("Ready. Send ON or OFF.");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();                 // remove spaces/newlines
    cmd.toUpperCase();          // make it case-insensitive

    if (cmd == "1") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED ON");
    } 
    else if (cmd == "0") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED OFF");
    } 
    else {
      Serial.print("Unknown command: ");
      Serial.println(cmd);
      Serial.println("Use ON or OFF");
    }
  }
}
