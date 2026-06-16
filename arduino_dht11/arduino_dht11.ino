#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --- Configuration ---
#define DHTPIN A0        // DHT11 DATA pin connected to A0
#define DHTTYPE DHT11   
DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal_I2C lcd(0x27, 16, 2); 


String firstRowText = "Aaron - DHT11 Temp Monitoring "; 
int textLen;
int scrollPos = 0;

unsigned long lastScrollTime = 0;
const int scrollDelay = 400; // ms per scroll step

unsigned long lastTempTime = 0;
const int tempDelay = 2000; 

float currentTemp = 0.0;

void setup() {
  Serial.begin(9600); 
  dht.begin();
  
  lcd.init();
  lcd.backlight();
  
  textLen = firstRowText.length();
  
  // Initial display setup
  lcd.clear();
  if (textLen <= 16) {
    lcd.setCursor(0, 0);
    lcd.print(firstRowText);
  }
}

void loop() {
  unsigned long currentMillis = millis();

  // 1. Read and update Temperature every `tempDelay` ms
  if (currentMillis - lastTempTime >= tempDelay) {
    lastTempTime = currentMillis;
    
    
    float t = dht.readTemperature();
    
    
    if (isnan(t)) {
      lcd.setCursor(0, 1);
      lcd.print("Sensor Error    ");
    } else {
      currentTemp = t;
      // Send to PC via Serial
      Serial.print("TEMP:");
      Serial.println(currentTemp);
      
      // Update LCD second row
      lcd.setCursor(0, 1);
      lcd.print("Temp: ");
      lcd.print(currentTemp, 1);
      lcd.print(" C      "); 
    }
  }

  
  if (textLen > 16) {
    if (currentMillis - lastScrollTime >= scrollDelay) {
      lastScrollTime = currentMillis;
      
     
      String displayStr = firstRowText.substring(scrollPos) + firstRowText.substring(0, scrollPos);
      
      lcd.setCursor(0, 0);
      lcd.print(displayStr.substring(0, 16));
      
      scrollPos++;
      if (scrollPos >= textLen) {
        scrollPos = 0;
      }
    }
  }
}
