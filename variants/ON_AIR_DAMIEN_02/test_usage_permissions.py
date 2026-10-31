from pathlib import Path
import re, subprocess, tempfile, shutil
root=Path(__file__).parent
s=(root/'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf8')
core=(root/'TriCasterRecCore.h').read_text(encoding='utf8')
names=['handleDirect','handleAlert','handleAlertTest','handleOff']
functions='\n'.join(re.search(r'void '+n+r'\([^\n]*\)\s*\{.*?\n\}',s,re.S).group() for n in names)
for name in ['handleMacroPreview','handleCustomTest']:
 body=re.search(r'void '+name+r'\([^\n]*\)\s*\{.*?\n\}',s,re.S).group()
 assert 'tcManualAllowed(' in body
 assert body.index('tcManualAllowed(')<body.index('showMacroPreview(')
assert 'if(tcControlActive())' in re.search(r'void handleLibraryPreview\(\).*?\n\}',s,re.S).group()
prefix=r'''
#include <cassert>
#define F(x) x
#define PSTR(x) x
struct Server {
 int code=0;
 void send_P(int c,const char*,const char*){code=c;}
 void sendHeader(const char*,const char*){}
} server;
struct Log {void println(const char*){}} Serial;
bool enabled=false,outputEnabled=false,alertRunning=false,tcManualOverride=false,tcPaused=false;
int activeMacro=-1,requested=0,activations=0,alerts=0;
bool tcControlActive(){return enabled;}
bool parseMacroIndex(uint8_t& out){out=requested;return requested>=0&&requested<4;}
void sendStatusResponse(){server.code=200;}
void applyMacroIdle(int i){activeMacro=i;outputEnabled=false;}
void applyMacro(int i){++activations;activeMacro=i;outputEnabled=true;alertRunning=false;}
void startAlert(int i,bool test=false){(void)test;++alerts;activeMacro=i;alertRunning=true;outputEnabled=false;}
void blackout(){activeMacro=-1;outputEnabled=false;alertRunning=false;}
void tcReleaseManual(){tcManualOverride=false;tcPaused=false;blackout();}
void tcPause(){tcManualOverride=false;if(enabled)tcPaused=true;}
'''
main=r'''
int main(){
 for(int mode=0;mode<2;++mode){enabled=mode;
  for(int profile=1;profile<4;++profile){requested=profile;
   for(auto action:{handleDirect,handleAlert,handleAlertTest}){
    server.code=0;action();assert(server.code==403 || server.code==409);
    assert(activations==0 && alerts==0);
   }
  }
 }
 // CARAC direct takes priority over an active automatic STREAM profile.
 enabled=true;requested=0;activeMacro=2;outputEnabled=true;handleDirect();
 assert(server.code==200 && activeMacro==0 && tcManualOverride && outputEnabled);
 // Pressing CARAC direct again releases it instead of forcing a TriCaster state.
 handleDirect();assert(!tcManualOverride && !outputEnabled && activeMacro==-1);
 // CARAC alert can also take priority over an automatic profile.
 activeMacro=3;outputEnabled=true;handleAlert();assert(alertRunning && activeMacro==0 && tcManualOverride);
 handleOff();assert(!outputEnabled && !alertRunning && !tcManualOverride && tcPaused);
 enabled=false;tcPaused=false;requested=0;handleDirect();assert(outputEnabled && activeMacro==0);
 assert(tcManualAllowed(0) && !tcManualAllowed(1) && !tcManualAllowed(2) && !tcManualAllowed(3));
}
'''
with tempfile.TemporaryDirectory() as temp:
 cpp=Path(temp)/'usage.cpp';exe=Path(temp)/'usage'
 cpp.write_text(core+'\n'+prefix+functions+main,encoding='utf8')
 compiler=shutil.which('g++') or shutil.which('clang++');assert compiler
 subprocess.run([compiler,'-std=c++17','-include','initializer_list',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('PASS: actual HTTP handlers reject all manual automatic-profile commands; CARAC direct/alert priority and OFF verified')
