#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_LEDBackpack.h>

// Your WiFi credentials
const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";

// GitHub credentials
const char* githubToken = "your_github_token";
const char* username = "your_github_username";

// GitHub GraphQL API endpoint
const char* githubApiUrl = "https://api.github.com/graphql";

// Define the LED matrix
Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

void setup() {
  // Initialize the serial port for debugging
  Serial.begin(115200);
  
  // Initialize the LED matrix
  matrix.begin(0x70);  // I2C address for the matrix
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Fetch and display contribution data
  fetchAndDisplayContributions();
  
  // Wait for an hour before refreshing
  delay(3600000);  // 1 hour
}

void fetchAndDisplayContributions() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Prepare the GraphQL query
    String query = String("{ user(login: \"") + username + "\") { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }";
    String body = String("{\"query\": \"") + query + "\"}";
    
    // Set up the HTTP request
    http.begin(githubApiUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", String("Bearer ") + githubToken);
    
    // Send the request and get the response
    int httpResponseCode = http.POST(body);
    if (httpResponseCode > 0) {
      String response = http.getString();
      
      // Parse the JSON response
      DynamicJsonDocument doc(4096);
      DeserializationError error = deserializeJson(doc, response);
      if (!error) {
        // Clear the matrix
        matrix.clear();
        
        // Process the data and update the matrix
        JsonArray weeks = doc["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"].as<JsonArray>();
        int totalWeeks = weeks.size();
        
        for (int week = 0; week < 32; week++) {  // Display the last 32 weeks
          int weekIndex = totalWeeks - 1 - week;  // Start from the most recent week
          if (weekIndex >= 0) {
            JsonArray days = weeks[weekIndex]["contributionDays"].as<JsonArray>();
            for (int day = 0; day < 7; day++) {
              int count = days[day]["contributionCount"];
              int x = 31 - week;  // Column, starting from the last matrix
              int y = day;  // Row, Sunday is 0
              
              if (count > 0) {
                matrix.drawPixel(x, y, LED_ON);
              } else {
                matrix.drawPixel(x, y, LED_OFF);
              }
            }
          }
        }
        
        // Show the updated matrix
        matrix.writeDisplay();
      } else {
        Serial.println("Failed to parse JSON");
      }
    } else {
      Serial.println("HTTP request failed");
    }
    
    // Close the connection
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}
