#include "FastLED.h"

#define NUM_LEDS 40
#define DATA_PIN 2

CRGB leds[NUM_LEDS];

int brightness = 255;

//Turns the hardware data addresses into a standard row column structure for the led matrix
int x[40] = {7, 8, 23, 24, 39, 6, 9, 22, 25, 38, 5, 10, 21, 26, 37, 4, 11, 20, 27, 36, 3, 12, 19, 28, 35, 2, 13, 18, 29, 34, 1, 14, 17, 30, 33, 0, 15, 16, 31, 32};

void setup() {
  Serial.begin(9600);
  
  FastLED.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
  FastLED.setBrightness(brightness);
}

//this separates a string into values based on a separater character
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void loop() {

  if(Serial.available() > 0) {
    //commands are sent to the arduino in this format r,g,b
    //Ex: 255,0,0 to display full red
    String command = Serial.readStringUntil('\n');
    String r = getValue(command,',',0);
    String g = getValue(command,',',1);
    String b = getValue(command,',',2);;
    int rDR = (int)r.toInt();
    int gDR = (int)g.toInt();
    int bDR = (int)b.toInt();

    //for now we just change all the LEDs to the color given
    //red and green are switched because the LEDs we used were GRB and not RGB
    for(int j = 0; j < NUM_LEDS; j++) { 
      leds[x[j]] = CRGB(gDR, rDR, bDR);
    }
    FastLED.show();
  }

    

}
