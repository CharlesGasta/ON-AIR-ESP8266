from pathlib import Path
import re, subprocess, tempfile, shutil
root=Path(__file__).parent
source=(root/'ONE_AIR_CARAC_V2.ino').read_text(encoding='utf8')
core=(root/'TriCasterRecCore.h').read_text(encoding='utf8')
assert core.replace('#pragma once','') in source, 'Embedded parser diverged'
impl=(root/'TriCasterRec.h').read_text(encoding='utf8')
assert impl.replace('#pragma once','') in source, 'Embedded controller diverged'
update=re.search(r'void tcUpdate\(\) \{.*?\n\}',impl,re.S).group()
release=re.search(r'void tcReleaseManual\(\) \{.*?\n\}',impl,re.S).group()
pause=re.search(r'void tcPause\(\) \{.*?\n\}',impl,re.S).group()
reset=re.search(r'void tcResetConnection\(\) \{.*?\n\}',impl,re.S).group()
prefix=r'''
#include <cassert>
#include <string>
#include <vector>
#include <iostream>
#define F(x) x
uint32_t clockMs=100;
uint32_t millis(){return clockMs;}
uint32_t micros(){return clockMs*1000;}
const int WL_CONNECTED=3;
struct IPAddress {IPAddress(int,int,int,int){}};
struct FakeWiFi {int state=3;int status(){return state;}} WiFi;
struct FakeClient {
 bool online=false, connectOK=true; unsigned connections=0; std::string input,writes;
 bool connected(){return online;}
 void stop(){online=false;input.clear();}
 void setTimeout(unsigned){} void setNoDelay(bool){} void keepAlive(int,int,int){}
 bool connect(IPAddress,unsigned){++connections;return online=connectOK;}
 template<class T> void print(T text){writes+=text;}
 int available(){return input.size();}
 int read(){char c=input[0];input.erase(0,1);return c;}
} tcClient;
struct Log {void println(const char*){}} Serial;
TcRecSettings tcSettings={0x54435233UL,0,1,5951,{192,0,2,20},2,3,0,0};
TcRecParser tcParser;
bool tcKnown=false,tcRecording=false,tcPaused=false;
bool tcRecKnown=false,tcStreamKnown=false,tcStreaming=false;
bool tcManualOverride=false;
uint8_t tcLastActiveProfile=1;
uint32_t tcLastAttempt=0,tcConnectedAt=0,tcHeartbeatAt=0,tcUpdates=0;
int tcApplied=-1;
bool startupSequenceComplete=true,settingsPreviewActive=false,libraryPreviewActive=false;
bool outputEnabled=false;int activeMacro=-1;
int applyCount=0,offCount=0,errorFrames=0,idleCount=0;
bool tcControlActive(){return tcSettings.enabled;}
void blackout(){outputEnabled=false;activeMacro=-1;++offCount;}
void applyMacroIdle(int macro){outputEnabled=false;activeMacro=macro;++idleCount;}
void applyMacro(int macro){outputEnabled=true;activeMacro=macro;++applyCount;}
void setRGBLevel(int,int,int,int){++errorFrames;}
'''
main=r'''
std::vector<int> ingest(TcRecParser& p,const std::string& text){
 std::vector<int> out;for(char c:text){int v=p.feed(c);if(v>=0)out.push_back(v);}return out;
}
int main(){
 TcRecParser p;
 assert(ingest(p,"<shortcut_states><shortcut_state name=\"record_toggle\" value=\"1\"/></shortcut_states>")==std::vector<int>{1});
 assert(ingest(p,"<shortcut_state value='0' name='record_toggle' />")==std::vector<int>{0});
 assert(ingest(p,"<shortcut_state name='streaming' value='1'/>").empty());
 assert(ingest(p,"<shortcut_state name='streaming_toggle' value='1'/>")==std::vector<int>{3});
 assert(ingest(p,"<shortcut_state value='0' name='streaming_toggle'/>")==std::vector<int>{2});
 assert(ingest(p,"<shortcut_state name='record_toggle_extra' value='1'/>").empty());
 assert(ingest(p,"<shortcut_state name='record_toggle' value='invalid'/>").empty());
 assert(ingest(p,"<shortcut_state name='record_toggle'/>").empty());
 assert(ingest(p,"<shortcut_state name='record_toggle' value='true'/>")==std::vector<int>{1});
 assert(ingest(p,"<shortcut_state name='record_toggle' value='false'/>")==std::vector<int>{0});
 assert(ingest(p,"<shortcut_state name='record_toggle' note='"+std::string(400,'x')+"' value='1'/>").empty());
 assert(ingest(p,"<shortcut_state name='record_toggle' value='0'/>")==std::vector<int>{0});
 for(int i=0;i<20000;++i)assert(ingest(p,"<shortcut_state name='other' value='0'/>").empty());
 assert(ingest(p,"<shortcut_state name='record_toggle' value='1'/>")==std::vector<int>{1});
 assert(tcSettingsValid(tcSettings,4));tcSettings.macro=4;assert(!tcSettingsValid(tcSettings,4));tcSettings.macro=1;
 // Manual mode must never connect or change LEDs.
 tcUpdate();assert(tcClient.connections==0 && applyCount==0 && offCount==0);
 tcSettings.enabled=1;tcUpdate();assert(tcClient.connections==1 && !tcKnown && !outputEnabled);
 assert(tcClient.writes=="<register name=\"NTK_states\"/>\n");
 // A fragmented initial state cannot light REC before a complete valid tag.
 tcClient.input="<shortcut_state name='streaming_toggle' value='0'/>";tcUpdate();assert(!tcKnown && !outputEnabled);
 tcClient.input="<shortcut_state name='record_toggle' value='";tcUpdate();assert(!tcKnown && !outputEnabled);
 tcClient.input="1'/>";tcUpdate();assert(tcKnown && outputEnabled && activeMacro==1 && applyCount==1);
 tcUpdate();assert(applyCount==1); // Do not restart the animation every loop.
 clockMs+=6000;tcUpdate();assert(outputEnabled && tcKnown); // Quiet stream is not REC OFF.
 tcClient.input="<shortcut_state name='record_toggle' value='0'/>";tcUpdate();assert(!outputEnabled);
 tcClient.input="<shortcut_state name='record_toggle' value='1'/>";tcUpdate();assert(outputEnabled);
 tcPause();blackout();tcUpdate();assert(tcPaused && !outputEnabled);
 tcPaused=false;tcApplied=-1;tcUpdate();assert(outputEnabled);
 // Link failure invalidates REC and cannot leave a false red indication.
 WiFi.state=0;tcUpdate();assert(!tcKnown && !outputEnabled && tcApplied==2);
 WiFi.state=3;tcUpdate();assert(!tcKnown && !outputEnabled);
 // Empty or unsupported state snapshots reconnect after their initial deadline.
 unsigned connections=tcClient.connections;clockMs+=11000;tcUpdate();assert(!tcClient.online && !tcKnown);
 clockMs+=3001;tcUpdate();assert(tcClient.connections>connections);
 // A valid REC state during startup is read but must not interrupt the boot cinematic.
 startupSequenceComplete=false;tcClient.input="<shortcut_state name='record_toggle' value='1'/><shortcut_state name='streaming_toggle' value='0'/>";
 tcUpdate();assert(tcKnown && !outputEnabled);startupSequenceComplete=true;tcUpdate();assert(outputEnabled);
 settingsPreviewActive=true;blackout();tcUpdate();assert(!outputEnabled);
 settingsPreviewActive=false;tcUpdate();assert(outputEnabled);
 // All four combinations use independent animation assignments.
 tcClient.input="<shortcut_state name='record_toggle' value='0'/><shortcut_state name='streaming_toggle' value='0'/>";
 tcUpdate();assert(tcKnown && !outputEnabled && tcApplied==0);
 int idles=idleCount;tcUpdate();tcUpdate();assert(idleCount==idles);
 tcSettings.reserved=3;tcApplied=-1;tcUpdate();assert(activeMacro==3 && !outputEnabled);
 tcSettings.reserved=0;tcApplied=-1;tcUpdate();assert(activeMacro==tcLastActiveProfile && !outputEnabled);
 tcClient.input="<shortcut_state name='record_toggle' value='1'/>";
 tcUpdate();assert(outputEnabled && activeMacro==1);
 tcClient.input="<shortcut_state name='streaming_toggle' value='1'/>";
 tcUpdate();assert(outputEnabled && activeMacro==3);
 tcClient.input="<shortcut_state name='record_toggle' value='0'/>";
 tcUpdate();assert(outputEnabled && activeMacro==2);
 tcClient.input="<shortcut_state name='streaming_toggle' value='0'/>";
 tcUpdate();assert(!outputEnabled);
 assert(tcSelectedMacro(tcSettings,false,true,false,true)==-2);
 assert(tcSelectedMacro(tcSettings,true,false,true,false)==-2);
 // A previous STREAM ON cannot survive a lost connection.
 tcClient.input="<shortcut_state name='streaming_toggle' value='1'/>";tcUpdate();assert(activeMacro==2);
 WiFi.state=0;tcUpdate();assert(!tcKnown && !tcRecKnown && !tcStreamKnown);
 WiFi.state=3;clockMs+=3001;tcUpdate();
 tcClient.input="<shortcut_state name='record_toggle' value='1'/>";tcUpdate();assert(!tcKnown && !outputEnabled);
 tcClient.input="<shortcut_state name='streaming_toggle' value='0'/>";tcUpdate();assert(tcKnown && activeMacro==1);
 tcManualOverride=true;applyMacro(0);tcClient.input="<shortcut_state name='streaming_toggle' value='1'/>";tcUpdate();assert(activeMacro==0 && tcStreaming);
 tcReleaseManual();tcUpdate();assert(activeMacro==3 && !tcManualOverride);
 tcSettings.enabled=0;int calls=applyCount;tcUpdate();assert(applyCount==calls);
 std::cout<<"PASS: independent REC/STREAM, four combinations, three animations, unknown-state guard, fragmented XML, OFF latch, reconnect and link loss"<<std::endl;
}
'''
with tempfile.TemporaryDirectory() as temp:
 cpp=Path(temp)/'test.cpp';exe=Path(temp)/'test'
 cpp.write_text(core+'\n'+prefix+reset+pause+release+update+main,encoding='utf8')
 compiler=shutil.which('g++') or shutil.which('clang++');assert compiler
 subprocess.run([compiler,'-std=c++17','-Wall','-Wextra',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('PASS: actual controller and parser embedded in the standalone sketch match tested sources')
