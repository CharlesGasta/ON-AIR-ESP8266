from pathlib import Path
import re,subprocess,tempfile,shutil,base64
root=Path(__file__).parent
s=(root/'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf8')
def fn(name):return re.search(r'void '+name+r'\([^\n]*\)\s*\{.*?\n\}',s,re.S).group()
css=re.search(r'COMMON_CSS\[\].*?R"CSS\((.*?)\)CSS";',s,re.S).group(1)
control=re.search(r'CONTROL_PAGE_JS\[\].*?R"JS\((.*?)\)JS";',s,re.S).group(1)
prefix=r'''
#include <string>
#include <iostream>
#include <cstdint>
#include <cstdio>
#define F(x) x
#define PSTR(x) x
class String:public std::string{
public:using std::string::operator+=;
 String(){} String(const char* p):std::string(p){} String(const std::string& p):std::string(p){}
 String(int i):std::string(std::to_string(i)){} String(unsigned i):std::string(std::to_string(i)){}
};
std::string html;
struct Server{
 void sendHeader(const char*,const char*){} void setContentLength(int){}
 void send(int,const char*,const char*){}
 void sendContent(const std::string& s){html+=s;}
 void sendContent_P(const char* s){html+=s;}
} server;
struct Log{void println(const std::string&){}}Serial;
struct Device{int getFreeHeap(){return 50000;}int getMaxFreeBlockSize(){return 40000;}}ESP;
const int CONTENT_LENGTH_UNKNOWN=-1,MACRO_COUNT=4;
struct MacroConfig{
 const char* name;uint8_t r=255,g=0,b=0,intensity=100,idleR=0,idleG=0,idleB=0,idleIntensity=0;bool idleOff=true;
};
struct Config{const char* deviceName="ON_AIR-MOC-02";MacroConfig macro[4]={{"CARAC"},{"REC"},{"STREAM"},{"REC + STREAM"}};}config;
void yield(){} bool webMemoryReady(){return true;} bool logoAvailable(uint8_t){return true;}
String htmlEscape(const String& s){return s;}
String rgbToHex(uint8_t r,uint8_t g,uint8_t b){char out[8];snprintf(out,sizeof(out),"#%02x%02x%02x",r,g,b);return String(out);}
bool tcControlActive(){return true;}const char* tcStatusText(){return "TriCaster : REC + STREAM";}
void sendHtmlChunk(const String& s){html+=s;}void sendHtmlFlash(const char* s){html+=s;}
'''
main=r'''
int main(){sendControlPage();std::cout<<html;}
'''
with tempfile.TemporaryDirectory() as temp:
 cpp=Path(temp)/'ui.cpp';exe=Path(temp)/'ui'
 cpp.write_text(prefix+'\nconst char* CONTROL_PAGE_JS=R"PAGE('+control+')PAGE";\n'+fn('tcSendBanner')+fn('tcSendAutomaticCard')+fn('sendControlPage')+main,encoding='utf8')
 compiler=shutil.which('g++') or shutil.which('clang++');assert compiler
 subprocess.run([compiler,'-std=c++17',str(cpp),'-o',str(exe)],check=True)
 html=subprocess.check_output([str(exe)]).decode('utf8')
html=re.sub(r'<link rel=\'stylesheet\' href=\'/style.css[^\']*\'>','<style>'+css+'</style>',html)
for i in range(4):assert f"id='macro-{i}'" in html
assert "id='direct-0'" in html and "id='alert-0'" in html
for i in range(1,4):
 assert f"id='direct-{i}'" not in html and f"id='alert-{i}'" not in html
 assert f"id='auto-state-{i}'" in html
assert 'Rendre la main au TriCaster' in html
assert html.count('TRICASTER UNIQUEMENT')==3
assert "name='tcMacro'" not in fn('tcSendSettings')
assert "name='tcStreamMacro'" not in fn('tcSendSettings')
print('PASS: actual console renderer exposes CARAC controls only; three read-only automatic cards, fixed roles and release control')
print('USAGE_HTML_BASE64='+base64.b64encode(html.encode()).decode())
