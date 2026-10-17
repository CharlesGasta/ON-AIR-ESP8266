"""Exercise actual OTA handlers with an injected flash writer; no LED callbacks/restart before ACK."""
from pathlib import Path
import re,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'ON_AIR_ESP8266.ino').read_text(encoding='utf-8')
def fn(name):
 m=re.search(r'^void '+name+r'\([^;]*?\)\s*\{',s,re.M);assert m,name
 i=m.end();depth=1;quote=False;esc=False
 while depth:
  c=s[i];i+=1
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
 return s[m.start():i]
state=s.split('// BEGIN OTA STATE')[1].split('// END OTA STATE')[0]
handlers='\n'.join(fn(n) for n in ['otaFail','otaStopEffects','otaCancelWriter','handleFirmwareUpload','handleFirmwareComplete','serviceFirmwareUpdate'])
assert 'setRGBLevel' not in handlers and 'pixels.show' not in handlers and 'delay(' not in handlers
assert 'Update.on' not in s and 'otaVisual' not in s
prefix=r'''
#include <stdint.h>
#define F(x) x
#define PSTR(x) x
#include <cstring>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <cassert>
#include <iostream>
#include <cctype>
using std::size_t;
struct String:std::string{
 using std::string::string;String()=default;String(const std::string& x):std::string(x){}
 long toInt()const{try{return std::stol(*this);}catch(...){return 0;}}
 void toLowerCase(){for(char& c:*this)c=(char)std::tolower((unsigned char)c);}
};
String jsonEscape(const String& s){return s;}
uint32_t nowMs=1;uint32_t millis(){return nowMs;}void yield(){}
int pixelWrites=0,reboots=0,begins=0;bool libraryPreviewActive=false;char libraryPreviewToken[41]={};int customOwner=-1;
void blackout(){pixelWrites++;}
const int WIFI_NONE_SLEEP=0,U_FLASH=0;struct{void setSleepMode(int){}} WiFi;
struct{uint32_t free=0x100000;uint32_t getFreeSketchSpace(){return free;}void restart(){reboots++;}} ESP;
enum{UPLOAD_FILE_START,UPLOAD_FILE_WRITE,UPLOAD_FILE_END,UPLOAD_FILE_ABORTED};
struct HTTPUpload{int status=0;String name="firmware";size_t currentSize=0,totalSize=0;uint8_t buf[1024]={};} upload;
struct{void setNoDelay(bool){}} client;
struct{
 std::map<std::string,String> args;int code=0;String response;
 String arg(const char* key){return args[key];}
 HTTPUpload& upload(){return ::upload;}
 void sendHeader(const char*,const char*){}
 void send(int c,const char*,const String& body){code=c;response=body;}
 void send_P(int c,const char* type,const char* body){send(c,type,String(body));}
 auto& client(){return ::client;}
} server;
struct{
 bool running=false,error=false,beginFail=false,writeFail=false,endFail=false;size_t expected=0,written=0;String md5;
 bool isRunning(){return running;}bool hasError(){return error;}
 String getErrorString(){return "Flash / MD5 error";}
 bool begin(size_t n,int){begins++;expected=n;written=0;error=beginFail;running=!error;return !error;}
 bool setMD5(const char* value){md5=value;return md5.length()==32;}
 size_t write(uint8_t*,size_t n){if(writeFail){error=true;return 0;}written+=n;return n;}
 bool end(bool remaining){running=false;if(error||endFail||(!remaining&&written!=expected)){error=true;return false;}return true;}
} Update;
'''
tests=r'''
void reset(){
 otaReceiving=otaValidated=otaRejected=otaRequestOpen=false;otaReceived=otaExpected=otaRestartAt=0;
 otaError[0]=otaExpectedMD5[0]=otaSession[0]=0;server.args.clear();server.code=0;server.response="";
 upload.name="firmware";upload.currentSize=upload.totalSize=0;upload.buf[0]=0xE9;
 Update.running=Update.error=Update.beginFail=Update.writeFail=Update.endFail=false;begins=pixelWrites=reboots=0;nowMs=1;ESP.free=0x100000;
}
void start(const char* size="64",const char* md5="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"){
 server.args["size"]=size;server.args["md5"]=md5;server.args["session"]="test";upload.status=UPLOAD_FILE_START;handleFirmwareUpload();
}
void write(size_t n){upload.status=UPLOAD_FILE_WRITE;upload.currentSize=n;handleFirmwareUpload();}
void finish(size_t total){upload.status=UPLOAD_FILE_END;upload.totalSize=total;handleFirmwareUpload();}
void noReboot(){nowMs+=5000;serviceFirmwareUpdate();assert(reboots==0&&otaRestartAt==0);}
int main(){
 reset();handleFirmwareComplete();assert(server.code==400);noReboot();
 reset();start("0");assert(!otaReceiving&&begins==0);handleFirmwareComplete();assert(server.code==400);noReboot();
 reset();start("64","invalid");assert(begins==0);noReboot();
 reset();ESP.free=0x1000;start();assert(begins==0);noReboot();
 reset();upload.name="filesystem";start();assert(begins==0);noReboot();
 reset();Update.beginFail=true;start();assert(!otaReceiving);noReboot();
 reset();start();assert(otaReceiving&&pixelWrites==1&&begins==1);write(32);int quiet=pixelWrites;noReboot();finish(32);assert(!otaValidated&&pixelWrites==quiet);handleFirmwareComplete();assert(server.code==400);noReboot();
 reset();start();write(32);upload.status=UPLOAD_FILE_ABORTED;handleFirmwareUpload();assert(!otaValidated&&!otaReceiving&&!otaRequestOpen);noReboot();
 reset();start();upload.buf[0]=0x1F;write(64);assert(!otaValidated&&!otaReceiving);noReboot();
 reset();start();write(65);assert(!otaValidated);noReboot();
 reset();start();Update.writeFail=true;write(64);finish(64);handleFirmwareComplete();assert(server.code==400&&!otaValidated);noReboot();
 reset();start();write(64);Update.endFail=true;finish(64);handleFirmwareComplete();assert(server.code==400&&!otaValidated);noReboot();
 reset();start();write(32);write(32);finish(64);assert(otaValidated&&otaRestartAt==0&&reboots==0&&pixelWrites==1);
 handleFirmwareComplete();assert(server.code==200&&otaRestartAt==1801&&reboots==0&&pixelWrites==1);
 handleFirmwareComplete();assert(server.code==409&&otaRestartAt==1801);
 nowMs=1800;serviceFirmwareUpdate();assert(reboots==0);nowMs=1801;serviceFirmwareUpdate();assert(reboots==1);
 reset();start("","");write(64);finish(64);assert(otaValidated);handleFirmwareComplete();assert(server.code==200&&reboots==0); // legacy UI compatibility
 std::cout<<"PASS: real OTA state machine, exact size, MD5 configuration/rejection, truncated writes, invalid file, abort, flash errors, quiet LEDs and ACK before deferred restart\n";
}
'''
compiler=shutil.which('g++') or shutil.which('clang++')
if not compiler:raise SystemExit('Host C++ compiler required; run in GitHub Actions.')
with tempfile.TemporaryDirectory(prefix='onair-ota-') as d:
 source=Path(d)/'ota.cpp';binary=Path(d)/'ota-test';source.write_text(prefix+state+handlers+tests,encoding='utf-8')
 subprocess.run([compiler,'-std=c++14','-Wall','-Wextra','-O2',str(source),'-o',str(binary)],check=True);subprocess.run([str(binary)],check=True)
