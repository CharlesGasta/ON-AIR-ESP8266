from pathlib import Path
import subprocess, tempfile, shutil
root=Path(__file__).parent
src=(root/'ONE_AIR_CARAC_RGB_01.ino').read_text(encoding='utf-8')
assert '#include <Adafruit_NeoPixel.h>' not in src
assert 'ON_AIR-MOC-02' not in src
assert 'ON_AIR-MOC-01' in src and 'onair-moc-01' in src
assert 'WiFi.setAutoReconnect(false)' in src
adapter=(root/'AnalogRgb01.h').read_text()
capture=src[src.index('uint8_t rgb01Legacy[340]'):src.index('void setup() {',src.index('uint8_t rgb01Legacy[340]'))]
prefix=r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <initializer_list>
#include <string>
#define D2 4
#define D1 5
#define D5 14
#define LOW 0
#define OUTPUT 1
#define F(x) x
int pwm[17]={},pwmRange=0,pwmFreq=0;
void digitalWrite(int p,int v){assert(v==0);}
void pinMode(int,int){}
void analogWriteRange(int n){pwmRange=n;}
void analogWriteFreq(int n){pwmFreq=n;}
void analogWrite(int p,int v){assert(p==4||p==5||p==14);assert(v>=0&&v<=1023);pwm[p]=v;}
void delay(int){throw 1;}
struct Log{void println(const char*){}}Serial;
size_t strlcpy(char* o,const char* s,size_t n){size_t l=strlen(s);if(n){memcpy(o,s,l<n-1?l:n-1);o[l<n-1?l:n-1]=0;}return l;}
struct IPAddress{
 uint8_t a[4]={};bool fromString(const char* s){unsigned x[4];char tail;if(sscanf(s,"%u.%u.%u.%u%c",x,x+1,x+2,x+3,&tail)!=4)return false;for(int i=0;i<4;i++){if(x[i]>255)return false;a[i]=x[i];}return true;}
 uint8_t operator[](int i)const{return a[i];}
};
constexpr int EEPROM_SIZE=2048;
struct EE{uint8_t a[2048]={};int writes=0;void begin(int){}uint8_t read(int i){return a[i];}}EEPROM;
struct MacroConfig{uint8_t r,g,b,intensity;bool idleOff;uint8_t idleR,idleG,idleB,idleIntensity;};
struct Config{bool externalWiFiEnabled;MacroConfig macro[4];}config;
struct NetworkProfile{char ssid[33];uint8_t mode,ip[4],gateway[4],mask[4],dns1[4],dns2[4];};
struct NetworkSettings{uint32_t magic;NetworkProfile profiles[5];uint8_t reserved[2];uint32_t checksum;}networkSettings;
struct TC{uint8_t enabled;uint16_t port;uint8_t ip[4];}tcSettings;
std::string rememberedSSID,rememberedPassword;
bool storageOK=true;int configsSaved=0;
void rememberWiFi(const char* s,const char* p){rememberedSSID=s;rememberedPassword=p;}
bool netSave(NetworkSettings& n){return storageOK;}
bool tcSaveSettings(TC& t){return storageOK;}
void saveConfig(){configsSaved++;EEPROM.writes++;}
void fixture(bool dhcp){
 memset(EEPROM.a,0,sizeof(EEPROM.a));uint32_t magic=0xca0a1a10;memcpy(EEPROM.a,&magic,4);
 strcpy((char*)EEPROM.a+4,"Test-Network");strcpy((char*)EEPROM.a+37,"private-test-value");EEPROM.a[102]=dhcp;
 strcpy((char*)EEPROM.a+103,"10.15.10.89");strcpy((char*)EEPROM.a+119,"10.15.10.1");
 strcpy((char*)EEPROM.a+135,"255.255.255.0");strcpy((char*)EEPROM.a+151,"10.15.10.1");strcpy((char*)EEPROM.a+167,"10.15.10.20");
 EEPROM.a[331]=255;EEPROM.a[334]=100;EEPROM.a[335]=255;EEPROM.a[336]=255;EEPROM.a[337]=255;EEPROM.a[338]=100;
}
'''
main=r'''
int main(){
 AnalogRgb01 rgb;rgb.begin();assert(pwmRange==1023&&pwmFreq==1000);assert(!pwm[4]&&!pwm[5]&&!pwm[14]);
 for(int i=0;i<36;i++)rgb.setPixelColor(i,AnalogRgb01::Color(255,0,0));rgb.show();assert(pwm[4]==1023&&pwm[5]==0&&pwm[14]==0);
 for(int i=0;i<36;i++)rgb.setPixelColor(i,AnalogRgb01::Color(0,255,0));rgb.show();assert(pwm[4]==0&&pwm[5]==1023&&pwm[14]==0);
 for(int i=0;i<36;i++)rgb.setPixelColor(i,AnalogRgb01::Color(0,0,255));rgb.show();assert(pwm[4]==0&&pwm[5]==0&&pwm[14]==1023);
 rgb.clear();for(int i=0;i<18;i++)rgb.setPixelColor(i,AnalogRgb01::Color(255,0,0));rgb.show();assert(pwm[4]==511);
 rgb.setPixelColor(100,0xffffff);rgb.show();assert(pwm[4]==511);
 rgb.setBrightness(0);rgb.show();assert(!pwm[4]&&!pwm[5]&&!pwm[14]);
 rgb.setBrightness(255);rgb.clear();rgb.show();assert(!pwm[4]&&!pwm[5]&&!pwm[14]);
 for(bool dhcp:{false,true}){
  fixture(dhcp);rgb01CaptureLegacy();assert(rgb01LegacyValid);int before=configsSaved;rgb01MigrateLegacy();
  assert(configsSaved==before+1&&!rgb01LegacyValid&&config.externalWiFiEnabled);
  assert(rememberedSSID=="Test-Network"&&rememberedPassword=="private-test-value");
  assert(networkSettings.profiles[0].mode==(dhcp?0:1));assert(networkSettings.profiles[0].ip[3]==89);
  assert(tcSettings.enabled&&tcSettings.port==5951&&tcSettings.ip[3]==20);
  for(int i=1;i<4;i++){assert(config.macro[i].r==255&&config.macro[i].g==0&&config.macro[i].intensity==100);assert(!config.macro[i].idleOff&&config.macro[i].idleG==255&&config.macro[i].idleIntensity==100);}
  for(auto b:rgb01Legacy)assert(!b);
 }
 fixture(false);EEPROM.a[0]=0;rgb01CaptureLegacy();assert(!rgb01LegacyValid);
 fixture(false);EEPROM.a[231]='x';try{rgb01CaptureLegacy();assert(false);}catch(int){}assert(!rgb01LegacyValid);
 fixture(false);rgb01CaptureLegacy();storageOK=false;int before=configsSaved;try{rgb01MigrateLegacy();assert(false);}catch(int){}assert(configsSaved==before&&EEPROM.a[0]==0x10);
 puts("PASS RGB01: physical pins, active-high PWM, boundaries, mixing, blackout, static/DHCP migration, colours, credentials preservation, unsupported layout and storage failures");
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'test.cpp').write_text(prefix+adapter.replace('#pragma once','')+capture+main,encoding='utf-8')
 compiler=shutil.which('g++') or shutil.which('clang++')
 assert compiler,'Host C++ compiler required'
 subprocess.run([compiler,'-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
