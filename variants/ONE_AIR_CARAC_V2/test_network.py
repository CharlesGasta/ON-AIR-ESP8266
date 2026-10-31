from pathlib import Path
import re,subprocess,tempfile,shutil
root=Path(__file__).parent
s=(root/'ONE_AIR_CARAC_V2.ino').read_text(encoding='utf8')
core=(root/'NetworkCore.h').read_text(encoding='utf8')
impl=(root/'Network.h').read_text(encoding='utf8')
assert core.replace('#pragma once','') in s and impl.replace('#pragma once','') in s
functions='\n'.join(re.search(r'(?:void|bool|int|IPAddress) '+n+r'\([^\n]*\)\s*\{.*?\n\}',impl,re.S).group() for n in ['netFind','netLoad','netSave','netApply'])
checksum=re.search(r'uint32_t configChecksum\([^\n]*\) \{.*?\n\}',s,re.S).group()
prefix=r'''
#include <map>
#include <vector>
#include <memory>
#include <string>
#include <cassert>
#include <cstdio>
#define F(x) x
struct IPAddress{uint8_t a[4];IPAddress(int a0,int a1,int a2,int a3):a{(uint8_t)a0,(uint8_t)a1,(uint8_t)a2,(uint8_t)a3}{}};
IPAddress netAddress(const uint8_t* a){return IPAddress(a[0],a[1],a[2],a[3]);}
std::vector<int> cleared;
void dns_setserver(int index,IPAddress ip){assert(!netNumber(ip.a));cleared.push_back(index);}
struct Radio{
 std::vector<std::vector<uint32_t>> calls;bool success=true;
 bool config(IPAddress ip,IPAddress gw,IPAddress mask,IPAddress dns1,IPAddress dns2){calls.push_back({netNumber(ip.a),netNumber(gw.a),netNumber(mask.a),netNumber(dns1.a),netNumber(dns2.a)});return success;}
}WiFi;
struct Log{void println(const char*){}}Serial;
struct File{
 std::shared_ptr<std::vector<uint8_t>> bytes;size_t pos=0;
 explicit operator bool(){return bool(bytes);}size_t size(){return bytes->size();}
 size_t read(uint8_t* dst,size_t count){size_t n=std::min(count,bytes->size()-pos);memcpy(dst,bytes->data()+pos,n);pos+=n;return n;}
 size_t write(const uint8_t* p,size_t n){bytes->assign(p,p+n);return n;}void close(){}
};
struct FS{
 std::map<std::string,std::shared_ptr<std::vector<uint8_t>>> files;bool fail=false;
 File open(const char* name,const char* mode){if(*mode=='w')files[name]=std::make_shared<std::vector<uint8_t>>();return File{files.count(name)?files[name]:nullptr};}
 bool rename(const char* a,const char* b){if(fail)return false;files[b]=files.at(a);files.erase(a);return true;}
}LittleFS;
NetworkSettings networkSettings={0x4e455431UL,{}, {},0};
bool netSave(NetworkSettings& value);
'''
main=r'''
int main(){
 NetworkProfile p={};strcpy(p.ssid,"Studio-Test");p.mode=1;
 uint8_t ip[]={192,0,2,20},gw[]={192,0,2,1},mask[]={255,255,255,0};
 memcpy(p.ip,ip,4);memcpy(p.gateway,gw,4);memcpy(p.mask,mask,4);
 assert(netProfileValid(p));
 auto bad=p;bad.mask[1]=0;assert(!netProfileValid(bad));
 bad=p;bad.ip[3]=0;assert(!netProfileValid(bad));bad=p;bad.ip[3]=255;assert(!netProfileValid(bad));
 bad=p;bad.gateway[2]=3;assert(!netProfileValid(bad));bad=p;memcpy(bad.gateway,bad.ip,4);assert(!netProfileValid(bad));
 bad=p;bad.ip[0]=224;assert(!netProfileValid(bad));
 bad=p;bad.ip[1]=168;bad.ip[2]=4;memcpy(bad.gateway,bad.ip,4);bad.gateway[3]=1;assert(!netProfileValid(bad));
 bad=p;bad.dns1[0]=255;assert(!netProfileValid(bad));
 // DHCP remains legal and ignores stale static address fields.
 bad=p;bad.mode=0;bad.mask[0]=3;assert(netProfileValid(bad));
 assert(netApply("Unconfigured-Test"));assert(WiFi.calls.back()==std::vector<uint32_t>({0,0,0,0,0}));
 networkSettings.profiles[0]=p;assert(netApply("Studio-Test"));
 assert(WiFi.calls.back()[0]==0xc0000214UL && WiFi.calls.back()[1]==0xc0000201UL);
 assert(WiFi.calls.back()[2]==0xffffff00UL && WiFi.calls.back()[3]==0xc0000201UL);
 assert(netApply("Other-Test"));assert(WiFi.calls.back()==std::vector<uint32_t>({0,0,0,0,0}));
 assert(cleared==std::vector<int>({0,1,0,1,0,1}));
 WiFi.success=false;assert(!netApply("Studio-Test"));WiFi.success=true;
 NetworkSettings saved=networkSettings;assert(netSave(saved));
 networkSettings={0x4e455431UL,{}, {},0};netLoad();assert(netFind("Studio-Test")==0);
 auto previous=*LittleFS.files.at("/network.cfg");saved.profiles[0].ip[3]=21;LittleFS.fail=true;
 assert(!netSave(saved));assert(*LittleFS.files.at("/network.cfg")==previous);LittleFS.fail=false;
 (*LittleFS.files.at("/network.cfg"))[50]^=1;networkSettings={0x4e455431UL,{}, {},0};netLoad();assert(netFind("Studio-Test")==-1);
 saved.profiles[1]=saved.profiles[0];assert(!netSettingsValid(saved));
 puts("PASS: actual network apply/load/save, DHCP reset, per-SSID isolation, IP/mask/gateway/DNS validation, AP overlap and atomic failure");
}
'''
with tempfile.TemporaryDirectory() as temp:
 cpp=Path(temp)/'network.cpp';exe=Path(temp)/'network'
 cpp.write_text(core+'\n'+prefix+checksum+functions+main,encoding='utf8')
 compiler=shutil.which('g++') or shutil.which('clang++');assert compiler
 subprocess.run([compiler,'-std=c++17',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
# Check every station connection path applies the correct network profile.
for name in ['startExternalWiFi','applyPendingExternalWiFi','connectBestKnownWiFi']:
 body=re.search(r'(?:void|bool) '+name+r'\([^\n]*\)\s*\{.*?\n\}',s,re.S).group()
 assert body.index('netApply(')<body.index('WiFi.begin('),name
assert '!netReconfigurePending' in s
