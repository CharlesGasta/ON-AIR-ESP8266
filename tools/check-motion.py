"""Compile and exercise the actual portable LED code, scheduler and persistence.

Requires a host C++ compiler (g++/clang++); runs in GitHub Actions before firmware.
"""
from pathlib import Path
import re,shutil,subprocess,tempfile

root=Path(__file__).resolve().parents[1]
s=(root/'ON_AIR_ESP8266.ino').read_text(encoding='utf-8')
def function(name):
    m=re.search(r'^(?:void|bool|uint32_t|uint16_t) '+name+r'\([^;]*?\)\s*\{',s,re.M)
    assert m,name
    i=m.end();level=1;quoted=False;escape=False
    while level:
        c=s[i];i+=1
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='{':level+=1
        elif c=='}':level-=1
    return s[m.start():i]

engine=s.split('// BEGIN PORTABLE MOTION ENGINE')[1].split('// END PORTABLE MOTION ENGINE')[0]
types=s[s.index('const uint32_t CONFIG_MAGIC'):s.index('ESP8266WebServer server')]
enum=re.search(r'enum StartupIndicatorState[^}]+};',s).group()
prefix=r'''
#include <stdint.h>
#define F(x) x
#define PSTR(x) x
#include <cstdio>
#include <stddef.h>
#include <math.h>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <cassert>
#include <iostream>
#include <algorithm>
using std::size_t;
'''
stubs=r'''
const unsigned long LIBRARY_PREVIEW_LEASE_MS=15000UL;
static uint8_t customData[1356];static int customOwner=-1;static bool customValid=false,customPreview=false,customPreviewAlert=false;
bool libraryPreviewActive=false,libraryPreviewPlaying=false;uint8_t libraryPreviewCue=0;unsigned long libraryPreviewStarted=0,libraryPreviewLastFrame=0,settingsPreviewUntil=0;char libraryPreviewToken[41]={},libraryPreviewRevokedToken[41]={};
bool otaVisualActive=false;unsigned long otaVisualLastFrame=0,otaErrorUntil=0;
uint32_t clockMs=0;uint32_t millis(){return clockMs;}
int activeMacro=-1,alertMacro=-1;
bool outputEnabled=false,alertRunning=false,settingsPreviewActive=false,alertTestMode=false;
struct {void println(const char*){}} Serial;
bool startupSequenceComplete=true,startupTestActive=false,startupAPFailed=false;
int startupRestoreMacro=-1;
unsigned long startupStateStartedAt=0,startupSessionStartedAt=0,startupIndicatorLastToggle=0;
StartupIndicatorState startupIndicatorState=STARTUP_IND_OFF;
const int AP_IP=42,WL_CONNECTED=3;
struct {int sta=0,ap=42;int status(){return sta;}int softAPIP(){return ap;}} WiFi;
const uint16_t LED_COUNT=36;
uint8_t displayed[36][3]={};int shown=0;
struct {void show(){shown++;}} pixels;
void setPixelLevel(uint16_t i,uint8_t r,uint8_t g,uint8_t b,uint8_t intensity){assert(i<36);displayed[i][0]=r*intensity/100;displayed[i][1]=g*intensity/100;displayed[i][2]=b*intensity/100;}
void updateLedStatusReference(uint8_t,uint8_t,uint8_t,uint8_t){}
void setRGBLevel(uint8_t r,uint8_t g,uint8_t b,uint8_t intensity){for(int i=0;i<36;i++)setPixelLevel(i,r,g,b,intensity);shown++;}
void ledsOff(){memset(displayed,0,sizeof(displayed));shown++;}
void renderCurrentOutput(){ledsOff();}
void applyMacroIdle(uint8_t);
bool failWrite=false,failRename=false;
std::map<std::string,std::vector<uint8_t>> files;
struct File {
 std::string name;bool valid=false;size_t at=0;
 operator bool()const{return valid;}
 size_t size(){return valid?files[name].size():0;}
 size_t read(uint8_t* dst,size_t n){if(!valid)return 0;n=std::min(n,files[name].size()-at);memcpy(dst,files[name].data()+at,n);at+=n;return n;}
 size_t write(const uint8_t* data,size_t n){if(!valid||failWrite)return 0;auto& bytes=files[name];if(bytes.size()<at+n)bytes.resize(at+n);memcpy(bytes.data()+at,data,n);at+=n;return n;}
 void flush(){}void close(){}
};
struct {
 bool exists(const char* name){return files.count(name);}
 File open(const char* name,const char* mode){File f;f.name=name;if(mode[0]=='w'){files[name].clear();f.valid=true;}else f.valid=files.count(name);return f;}
 bool rename(const char* from,const char* to){if(failRename||!files.count(from))return false;files[to]=files[from];files.erase(from);return true;}
} LittleFS;
enum {UPLOAD_FILE_START,UPLOAD_FILE_WRITE,UPLOAD_FILE_END,UPLOAD_FILE_ABORTED};
struct HTTPUpload{int status;size_t currentSize;uint8_t buf[2048];} upload;
std::vector<uint8_t> exported;
struct WiFiClient{size_t write(const uint8_t* p,size_t n){exported.insert(exported.end(),p,p+n);return n;}};
struct {
 HTTPUpload& upload(){return ::upload;}
 void sendHeader(const char*,const char*){}
 void setContentLength(size_t){}
 void send(int,const char*,const char*){exported.clear();}
 void send_P(int,const char*,const char*){exported.clear();}
 WiFiClient client(){return WiFiClient();}
} server;
struct {bool error=false;bool hasError(){return error;}} Update;
void delay(unsigned long ms){clockMs+=ms;}
int configWrites=0;void saveConfig(){configWrites++;}
'''
functions='\n'.join(function(n) for n in ['configChecksum','resetMotionSettings','validMotionSettings','saveMotionSettings','loadMotionSettings','showMotionFrame','renderSpatialMotion','cancelStartupIndicator','setStartupIndicatorState','enterStartupState','updateStartupIndicatorNetworkState','finishStartupSequence','updateStartupIndicator','customWord','validCustom','loadCustom','renderCustomOutput','renderLibraryOutput','renderMacroDirect','updateDirectMotion','startupAnimation','blackout','handleConfigExport','handleConfigImportData','validLibraryName','libraryReadName','libraryWrite','libraryNamesEqual','migrateAnimationLibrary','stopLibraryPreview','updateLibraryPreview',])
tests=r'''
void applyMacroIdle(uint8_t i){cancelStartupIndicator();activeMacro=i;outputEnabled=false;ledsOff();}
void tick(uint32_t ms){clockMs=ms;updateStartupIndicatorNetworkState();updateStartupIndicator();}
void beginBoot(bool external,int station=0,bool test=false){
 config.startupAnimation=true;config.externalWiFiEnabled=external;config.knownWiFiCount=external?1:0;
 activeMacro=-1;outputEnabled=false;alertRunning=false;settingsPreviewActive=false;
 WiFi.sta=station;WiFi.ap=42;startupTestActive=test;clockMs=0;startupAnimation();
}
std::vector<uint8_t> backupV1(){
 BackupHeader h={BACKUP_SIGNATURE,CONFIG_MAGIC,(uint16_t)sizeof(Config),1,0};
 h.checksum=configChecksum(reinterpret_cast<uint8_t*>(&config),sizeof(config));
 std::vector<uint8_t> v(sizeof(h)+sizeof(config));memcpy(v.data(),&h,sizeof(h));memcpy(v.data()+sizeof(h),&config,sizeof(config));return v;
}
void importBytes(const std::vector<uint8_t>& bytes){
 upload.status=UPLOAD_FILE_START;handleConfigImportData();
 for(size_t i=0;i<bytes.size();i+=37){upload.status=UPLOAD_FILE_WRITE;upload.currentSize=std::min(size_t(37),bytes.size()-i);memcpy(upload.buf,bytes.data()+i,upload.currentSize);handleConfigImportData();}
 upload.status=UPLOAD_FILE_END;handleConfigImportData();
}
int main(){
 static_assert(sizeof(Config)<=EEPROM_SIZE,"EEPROM capacity");
 assert(logoX(0)==1&&logoY(0)==1&&logoX(11)==0&&logoY(11)==1);
 for(int i=12;i<17;i++){assert(logoX(i)==0);if(i>12)assert(logoY(i)<logoY(i-1));}
 for(int i=17;i<31;i++){assert(logoY(i)==0);if(i>17)assert(logoX(i)>logoX(i-1));}
 for(int i=31;i<36;i++){assert(logoX(i)==1);if(i>31)assert(logoY(i)>logoY(i-1));}
 uint8_t frame[36][3];
 renderContourFrame(255,0,0,100,0,7200,frame);for(auto& p:frame)assert(p[0]==0);
 renderContourFrame(255,0,0,100,1800,7200,frame);assert(frame[0][0]==255&&frame[17][0]==255&&frame[18][0]==0);
 renderContourFrame(255,0,0,100,3600,7200,frame);for(auto& p:frame)assert(p[0]==255);
 renderContourFrame(255,0,0,100,5400,7200,frame);assert(frame[0][0]==0&&frame[17][0]==0&&frame[18][0]==255);
 renderContourFrame(255,0,0,100,7199,7200,frame);for(auto& p:frame)assert(p[0]<=3);
 uint8_t effectData[1356]={};memcpy(effectData,"CUE1",4);effectData[4]=2;effectData[5]=1;effectData[6]=50;effectData[7]=0xA5;
 effectData[8]=0x10;effectData[9]=0x0e;effectData[10]=100;effectData[11]=0x80;effectData[12]=35;effectData[13]=0;effectData[14]=255;
 uint32_t extendedCrc=configChecksum(effectData,1352);memcpy(effectData+1352,&extendedCrc,4);assert(validCustom(effectData));
 renderCueFrame(effectData,100,0,frame);assert(frame[35][0]==127&&frame[0][0]==0);
 renderCueFrame(effectData,100,3500,frame);assert(frame[0][0]==127&&frame[35][0]==0);
 effectData[10]=20;effectData[11]=0xC0;memset(effectData+12,0,108);effectData[13]=255;effectData[15]=1;effectData[19]=8;
 extendedCrc=configChecksum(effectData,1352);memcpy(effectData+1352,&extendedCrc,4);assert(validCustom(effectData));
 renderCueFrame(effectData,100,0,frame);assert(frame[0][1]==127&&frame[35][1]==127&&frame[1][1]==0);
 renderCueFrame(effectData,100,20,frame);for(auto& p:frame)for(auto c:p)assert(c==0);
 effectData[10]=19;extendedCrc=configChecksum(effectData,1352);memcpy(effectData+1352,&extendedCrc,4);assert(!validCustom(effectData));
 effectData[10]=20;effectData[4]=1;effectData[6]=effectData[7]=0;extendedCrc=configChecksum(effectData,1352);memcpy(effectData+1352,&extendedCrc,4);assert(!validCustom(effectData));
 for(int mode: {2,3,5,8,9}){uint8_t outward[36][3],back[36][3];renderMotionFrame(mode,255,0,0,100,1000,4000,outward,true);renderMotionFrame(mode,255,0,0,100,3000,4000,back,true);for(int i=0;i<36;i++)for(int k=0;k<3;k++)assert(std::abs((int)outward[i][k]-(int)back[i][k])<=1);}
 for(int mode=0;mode<10;mode++)for(int peak: {0,15,60,100})for(uint32_t ms=0;ms<12000;ms+=33){
  renderMotionFrame(mode,255,130,70,peak,ms,4000,frame);
  for(auto& pixel:frame)for(auto value:pixel)assert(value<=255*peak/100+1);
 }
 renderMotionFrame(2,255,0,0,100,400,4000,frame);assert(frame[12][0]>frame[31][0]);
 renderMotionFrame(3,255,0,0,100,400,4000,frame);assert(frame[31][0]>frame[12][0]);
 renderMotionFrame(1,255,0,0,60,2000,4000,frame);assert(frame[0][0]==153);
 renderMotionFrame(1,255,0,0,60,0,4000,frame);assert(frame[0][0]<30);
 for(uint32_t ms=0;ms<4500;ms+=17){assert(renderBootFrame(ms,frame));for(auto& p:frame)for(auto c:p)assert(c<=179);}
 assert(renderBootFrame(1720,frame)&&frame[0][0]>170&&frame[0][0]==frame[0][1]);
 renderBootFrame(3900,frame);for(auto& pixel:frame)assert(pixel[0]>160&&pixel[1]==0&&pixel[2]==0);
 assert(!renderBootFrame(4500,frame));for(auto& p:frame)for(auto c:p)assert(c==0);

 for(int mode: {2,3,5,7,8,9})for(uint32_t ms=0;ms<4000;ms+=31){
  renderMotionFrame(mode,255,255,255,100,ms,4000,frame,true);
  for(int led=0;led<36;led++){bool side=(led>=12&&led<17)||led>=31;
   if((mode<8&&side)||(mode>=8&&!side))for(auto c:frame[led])assert(c==0);
  }
 }
 renderMotionFrame(8,255,0,0,100,400,4000,frame,true);assert(frame[16][0]>frame[12][0]);
 renderMotionFrame(9,255,0,0,100,400,4000,frame,true);assert(frame[12][0]>frame[16][0]);
 memset(customData,0,sizeof(customData));memcpy(customData,"CUE1",4);customData[4]=1;customData[5]=2;
 customData[8]=232;customData[9]=3;customData[12]=200;
 customData[120]=232;customData[121]=3;customData[122]=232;customData[123]=3;customData[125]=200;
 uint32_t crc=configChecksum(customData,1352);memcpy(customData+1352,&crc,4);assert(validCustom(customData));
 files["/custom0.bin"]=std::vector<uint8_t>(customData,customData+1356);customOwner=-1;
 config.macro[0].intensity=100;renderCustomOutput(0,0);assert(displayed[0][0]==200&&displayed[0][1]==0);
 renderCustomOutput(0,1500);assert(displayed[0][0]==100&&displayed[0][1]==100);
 renderCustomOutput(0,2200);assert(displayed[0][0]==0&&displayed[0][1]==200);
 auto directFile=files["/custom0.bin"];
 auto alertFile=directFile;alertFile[12]=50;uint32_t alertCrc=configChecksum(alertFile.data(),1352);memcpy(alertFile.data()+1352,&alertCrc,4);files["/custom4.bin"]=alertFile;
 renderCustomOutput(0,0,true);assert(displayed[0][0]==50&&files["/custom0.bin"]==directFile);
 renderCustomOutput(0,0,false);assert(displayed[0][0]==200);

 assert(validLibraryName("Studio")&&!validLibraryName("")&&!validLibraryName(" Studio"));
 assert(libraryNamesEqual("STUDIO","studio")&&libraryNamesEqual("ÉTÉ","été")&&!libraryNamesEqual("Studio","Studio 2"));
 assert(libraryWrite(32,"Aurore",files["/custom0.bin"].data()));char savedName[64];assert(libraryReadName(32,savedName)&&std::string(savedName)=="Aurore");
 auto namedFile=files["/anim32.bin"];failRename=true;assert(!libraryWrite(32,"Replacement",files["/custom4.bin"].data()));assert(files["/anim32.bin"]==namedFile);failRename=false;
 customOwner=-1;config.macro[0].intensity=50;renderLibraryOutput(0,32,0);assert(displayed[0][0]==100);config.macro[0].intensity=100;
 resetMotionSettings();motionSettings.mode[0]=32;motionSettings.checksum=configChecksum(reinterpret_cast<uint8_t*>(&motionSettings),sizeof(motionSettings)-4);assert(validMotionSettings(motionSettings));

 strcpy(config.macro[0].name,"ONE FM");motionSettings.mode[0]=10;config.macro[0].alertAnimation=ALERT_CUSTOM;customOwner=-1;migrateAnimationLibrary();
 assert(motionSettings.mode[0]==32&&config.macro[0].alertAnimation==36&&files.count("/library.migrated"));
 assert(libraryReadName(36,savedName));auto originalName=files["/anim32.bin"];migrateAnimationLibrary();assert(files["/anim32.bin"]==originalName);
 for(uint8_t channel=0;channel<4;channel++){config.macro[channel].intensity=25*(channel+1);renderLibraryOutput(channel,32,0);assert(displayed[0][0]==50*(channel+1));}
 config.macro[0].intensity=100;
 auto beforePreviewFiles=files;assert(loadCustom(0));customOwner=-2;libraryPreviewActive=true;settingsPreviewActive=true;libraryPreviewCue=0;libraryPreviewPlaying=false;settingsPreviewUntil=clockMs+LIBRARY_PREVIEW_LEASE_MS;libraryPreviewLastFrame=clockMs-33;
 updateLibraryPreview();assert(displayed[0][0]==200&&files==beforePreviewFiles);
 clockMs+=3001;updateLibraryPreview();assert(libraryPreviewActive);clockMs+=12000;updateLibraryPreview();assert(!libraryPreviewActive&&!settingsPreviewActive&&displayed[0][0]==0);
 libraryPreviewActive=true;settingsPreviewActive=true;customOwner=-2;blackout();int afterOff=shown;updateLibraryPreview();assert(!libraryPreviewActive&&shown==afterOff);
 customOwner=-1;assert(loadCustom(0));customData[20]^=1;assert(!validCustom(customData));customOwner=-1;
 beginBoot(false);tick(4500);assert(startupIndicatorState==STARTUP_IND_AP);tick(5400);assert(startupIndicatorState==STARTUP_IND_FALLBACK);tick(7000);assert(startupSequenceComplete);
 beginBoot(true,3);tick(4500);tick(5400);tick(5425);assert(startupIndicatorState==STARTUP_IND_READY);tick(6475);assert(startupSequenceComplete);
 beginBoot(true);tick(4500);tick(5400);tick(15000);assert(startupIndicatorState==STARTUP_IND_ERROR);tick(16500);assert(startupIndicatorState==STARTUP_IND_FALLBACK);tick(18100);assert(startupSequenceComplete);
 beginBoot(false);WiFi.ap=0;tick(4500);tick(5400);assert(startupIndicatorState==STARTUP_IND_ERROR);tick(6900);assert(startupSequenceComplete);
 beginBoot(false);tick(1000);activeMacro=0;outputEnabled=true;updateStartupIndicatorNetworkState();int previous=shown;tick(5000);assert(startupSequenceComplete&&shown==previous);
 beginBoot(false);blackout();previous=shown;tick(5000);updateDirectMotion();assert(shown==previous&&!outputEnabled&&activeMacro==-1);for(auto& p:displayed)for(auto c:p)assert(c==0);
 beginBoot(false);startupTestActive=true;startupRestoreMacro=2;tick(4500);tick(5400);tick(7000);assert(activeMacro==2&&!outputEnabled);

 beginBoot(false);clockMs=8000;startupAnimation();clockMs=8017;updateStartupIndicator();assert(startupIndicatorState==STARTUP_IND_INTRO);
 clockMs=9700;updateStartupIndicator();assert(startupIndicatorState==STARTUP_IND_INTRO);
 clockMs=12500;updateStartupIndicator();assert(startupIndicatorState==STARTUP_IND_AP);
 resetMotionSettings();assert(motionSettings.mode[0]==0&&motionSettings.cycleMs[0]==4000);
 assert(saveMotionSettings());motionSettings.mode[1]=2;motionSettings.cycleMs[1]=6000;assert(saveMotionSettings());
 resetMotionSettings();loadMotionSettings();assert(motionSettings.mode[1]==2&&motionSettings.cycleMs[1]==6000);
 auto savedFile=files["/motion.cfg"];failRename=true;motionSettings.mode[1]=3;assert(!saveMotionSettings());assert(files["/motion.cfg"]==savedFile);failRename=false;assert(saveMotionSettings());
 files["/motion.cfg"][0]^=1;loadMotionSettings();assert(motionSettings.mode[1]==0);
 memset(&config,0,sizeof(config));config.magic=CONFIG_MAGIC;strcpy(config.deviceName,"DAMIEN");strcpy(config.knownWiFi[0].password,"retain-this");
 auto legacy=backupV1();motionSettings.mode[0]=7;importBytes(legacy);assert(configImportApplied&&motionSettings.mode[0]==0&&motionSettings.cycleMs[0]==4000);
 motionSettings.mode[0]=1;motionSettings.cycleMs[0]=8000;assert(saveMotionSettings());handleConfigExport();auto extended=exported;
 memset(config.deviceName,0,sizeof(config.deviceName));motionSettings.mode[0]=2;
 importBytes(extended);assert(configImportApplied&&std::string(config.deviceName)=="DAMIEN"&&motionSettings.mode[0]==1&&motionSettings.cycleMs[0]==8000);assert(std::string(config.knownWiFi[0].password)=="retain-this");
 auto corrupt=extended;corrupt.back()^=1;int writes=configWrites;importBytes(corrupt);assert(!configImportApplied&&configWrites==writes);
 BackupHeader header;memcpy(&header,corrupt.data(),sizeof(header));header.checksum=configChecksum(corrupt.data()+sizeof(header),corrupt.size()-sizeof(header));memcpy(corrupt.data(),&header,sizeof(header));
 importBytes(corrupt);assert(!configImportApplied&&configWrites==writes);
 upload.status=UPLOAD_FILE_START;handleConfigImportData();upload.status=UPLOAD_FILE_WRITE;upload.currentSize=sizeof(configImportBuffer)+1;handleConfigImportData();assert(!configImportAccepted);
 std::cout<<"PASS: geometry, 8 modes, intensity bounds, boot phases, Wi-Fi success/failure/AP fallback, user priority, atomic settings, legacy/new/corrupt/oversize backups\n";
}
'''
compiler=shutil.which('g++') or shutil.which('clang++')
if not compiler:raise SystemExit('Host C++ compiler required; run this check in GitHub Actions (Ubuntu).')
with tempfile.TemporaryDirectory(prefix='onair-motion-') as d:
    source=Path(d)/'motion.cpp';binary=Path(d)/'motion-test'
    source.write_text(prefix+types+enum+engine+stubs+functions+tests,encoding='utf-8')
    subprocess.run([compiler,'-std=c++11','-Wall','-Wextra','-O2',str(source),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
