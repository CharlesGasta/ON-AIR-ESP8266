from pathlib import Path
import re, subprocess, tempfile, shutil
root=Path(__file__).parent
source=(root/'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf8')
core=(root/'TriCasterRecCore.h').read_text(encoding='utf8')
impl=(root/'TriCasterRec.h').read_text(encoding='utf8')
functions='\n'.join(re.search(r'(?:void|bool) '+name+r'\([^\n]*\) \{.*?\n\}',impl,re.S).group() for name in ['tcLoadSettings','tcSaveSettings'])
checksum=re.search(r'uint32_t configChecksum\([^\n]*\) \{.*?\n\}',source,re.S).group()
prefix=r'''
#include <map>
#include <vector>
#include <string>
#include <memory>
#include <cassert>
#include <cstdio>
#define F(x) x
constexpr int MACRO_COUNT=4;
struct Log {void println(const char*){}} Serial;
struct File {
 std::shared_ptr<std::vector<uint8_t>> bytes;size_t position=0;
 explicit operator bool(){return bool(bytes);}
 size_t size(){return bytes->size();}
 size_t read(uint8_t* dst,size_t count){size_t n=std::min(count,bytes->size()-position);memcpy(dst,bytes->data()+position,n);position+=n;return n;}
 size_t write(const uint8_t* src,size_t count){bytes->assign(src,src+count);return count;}
 void close(){}
};
struct FS {
 std::map<std::string,std::shared_ptr<std::vector<uint8_t>>> files;
 bool failRename=false;
 File open(const char* name,const char* mode){
  if(*mode=='w')files[name]=std::make_shared<std::vector<uint8_t>>();
  return File{files.count(name)?files[name]:nullptr};
 }
 bool rename(const char* from,const char* to){if(failRename)return false;files[to]=files.at(from);files.erase(from);return true;}
} LittleFS;
TcRecSettings defaults={0x54435233UL,0,1,5951,{192,0,2,20},2,3,0,0};
TcRecSettings tcSettings=defaults;
bool tcSaveSettings(TcRecSettings& value);
'''
main=r'''
template<class T> void store(const T& s){
 auto p=std::make_shared<std::vector<uint8_t>>((const uint8_t*)&s,(const uint8_t*)&s+sizeof(s));LittleFS.files["/tricaster.cfg"]=p;
}
int main(){
 tcLoadSettings();assert(!tcSettings.enabled);
 TcRecLegacySettings legacy={0x54435231UL,1,3,5951,{192,0,2,20},0};
 legacy.checksum=configChecksum((const uint8_t*)&legacy,12);store(legacy);
 tcLoadSettings();assert(tcSettings.enabled && tcSettings.macro==1 && tcSettings.streamMacro==2 && tcSettings.bothMacro==3);
 assert(LittleFS.files.at("/tricaster.cfg")->size()==20);
 TcRecSettings saved=tcSettings;tcSettings=defaults;tcLoadSettings();
 assert(tcSettings.macro==1 && tcSettings.checksum==saved.checksum);
 TcRecSettings previousVersion={0x54435232UL,1,0,5951,{192,0,2,20},1,2,0,0};
 previousVersion.checksum=configChecksum((const uint8_t*)&previousVersion,16);store(previousVersion);
 tcSettings=defaults;tcLoadSettings();
 assert(tcSettings.enabled && tcSettings.macro==1 && tcSettings.streamMacro==2 && tcSettings.bothMacro==3);
 assert(tcSettings.ip[3]==20 && tcSettings.port==5951 && tcSettings.magic==0x54435233UL);
 TcRecSettings edited=saved;edited.port=5952;
 assert(tcSaveSettings(edited));tcSettings=defaults;tcLoadSettings();
 assert(tcSettings.macro==1 && tcSettings.streamMacro==2 && tcSettings.bothMacro==3 && tcSettings.port==5952);
 auto previous=*LittleFS.files.at("/tricaster.cfg");
 LittleFS.failRename=true;edited.port=5953;assert(!tcSaveSettings(edited));
 assert(*LittleFS.files.at("/tricaster.cfg")==previous);LittleFS.failRename=false;
 edited.macro=0;assert(!tcSaveSettings(edited));assert(*LittleFS.files.at("/tricaster.cfg")==previous);
 (*LittleFS.files.at("/tricaster.cfg"))[8]^=1;tcSettings=defaults;tcLoadSettings();assert(!tcSettings.enabled);
 legacy.checksum^=1;store(legacy);tcSettings=defaults;tcLoadSettings();assert(!tcSettings.enabled);
 saved.streamMacro=4;assert(!tcSettingsValid(saved,4));saved.streamMacro=0;saved.bothMacro=4;assert(!tcSettingsValid(saved,4));
 puts("PASS: real settings I/O; old role mappings corrected, network retained, manual role protected, checksums and atomic save failure");
}
'''
with tempfile.TemporaryDirectory() as temp:
 cpp=Path(temp)/'settings.cpp';exe=Path(temp)/'settings'
 cpp.write_text(core+'\n'+prefix+checksum+functions+main,encoding='utf8')
 compiler=shutil.which('g++') or shutil.which('clang++');assert compiler
 subprocess.run([compiler,'-std=c++17',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
