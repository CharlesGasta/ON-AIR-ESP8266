#pragma once
#include <stdint.h>
#include <string.h>

// Three independent active-high PWM outputs for N-channel MOSFET gates.
// Logical animation cells are averaged in linear RGB, never sent as data bits.
class AnalogRgb01 {
 public:
  static constexpr uint8_t RED_PIN = D2;
  static constexpr uint8_t GREEN_PIN = D1;
  static constexpr uint8_t BLUE_PIN = D5;
  static constexpr uint16_t CELL_COUNT = 36;
  static uint32_t Color(uint8_t r,uint8_t g,uint8_t b){return ((uint32_t)r<<16)|((uint32_t)g<<8)|b;}
  void begin(){
    for(uint8_t pin : {RED_PIN,GREEN_PIN,BLUE_PIN}){digitalWrite(pin,LOW);pinMode(pin,OUTPUT);}
    analogWriteRange(1023);analogWriteFreq(1000);clear();show();
  }
  void setBrightness(uint8_t value){brightness=value;}
  void clear(){memset(cells,0,sizeof(cells));}
  void setPixelColor(uint16_t i,uint32_t color){if(i<CELL_COUNT)cells[i]=color;}
  void show(){
    uint32_t sums[3]={};
    for(uint32_t color:cells){sums[0]+=(color>>16)&255;sums[1]+=(color>>8)&255;sums[2]+=color&255;}
    const uint8_t pins[]={RED_PIN,GREEN_PIN,BLUE_PIN};
    for(uint8_t c=0;c<3;++c){
      uint32_t pwm=(uint64_t)sums[c]*brightness*1023/(CELL_COUNT*255UL*255UL);
      analogWrite(pins[c],pwm);
    }
  }
 private:
  uint32_t cells[CELL_COUNT]={};
  uint8_t brightness=255;
};
