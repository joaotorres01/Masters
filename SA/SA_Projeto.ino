#include <ESP8266WiFi.h>

// Replace with your network credentials
const char* ssid     = "SSID";
const char* password = "PASSWORD";

// Replace with your server's address
const char* serverAddress = "your_SERVER_ADDRESS";

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to Wi-Fi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Set Wi-Fi module to station mode
  WiFi.mode(WIFI_STA);

}

void loop() {
  // Detect nearby Wi-Fi networks
  int n = WiFi.scanNetworks();
  if (n == 0) {
    Serial.println("No networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      // Print information about each network
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.println(")");
    }
  }

  // Connect to server
  WiFiClient client;
  if (!client.connect(serverAddress, 80)) {
    Serial.println("Connection to server failed");
    return;
  }

  // Send data to server
  String url = "/data?value=" + String(n); // Send the number of networks detected
  client.println("GET " + url + " HTTP/1.1");
  client.println("Host: " + String(serverAddress));
  client.println("Connection: close");
  client.println();

  // Wait for response
  while (client.connected() && !client.available()) delay(10);

  // Print response
  while (client.available()) {
    Serial.write(client.read());
  }

  delay(1000); // Wait for next reading
}
