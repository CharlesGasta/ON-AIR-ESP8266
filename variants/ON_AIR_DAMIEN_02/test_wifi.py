from pathlib import Path
import subprocess, tempfile, shutil

source = (Path(__file__).parent / 'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf-8')
def function(name, next_name):
    start = source.index(name + '() {')
    start = source.rfind('\n', 0, start) + 1
    end = source.index(next_name, start)
    return source[start:end]

retry = function('connectBestKnownWiFi', 'void startMDNSIfPossible();')
update = function('updateExternalWiFi', '// BEGIN TRICASTER IMPLEMENTATION')
prefix = r'''
#include <cassert>
#include <cstdint>
#include <string>
#include <vector>
#include <cstdio>
constexpr int WIFI_AP_STA=3, WL_CONNECTED=3;
uint32_t clockNow=0;
unsigned long millis(){return clockNow;}
struct Saved { const char* ssid; const char* password; };
struct Config { bool externalWiFiEnabled=true; unsigned knownWiFiCount=2;
  Saved knownWiFi[2]={{"Sarah_Charles_Home","test-password"},{"Backup","other-password"}};
} config;
struct FakeWiFi {
 int state=0, radioMode=3, clients=2, disconnects=0;
 std::vector<std::string> attempts, passwords;
 int status(){return state;} int getMode(){return radioMode;}
 void mode(int value){radioMode=value;} void hostname(const char*){}
 void disconnect(bool off){assert(!off);++disconnects;state=0;}
 void begin(const char* ssid,const char* password){attempts.push_back(ssid);passwords.push_back(password);}
 unsigned softAPgetStationNum(){return clients;}
} WiFi;
struct Log {template<class... T> void printf(const char*,T...) {}} Serial;
const char* MDNS_HOSTNAME="onair-moc-02";
int currentKnownWiFiAttempt=-1, mdnsCalls=0;
bool wifiScanRunning=false,wifiScanStartRequested=false,pendingExternalWiFiApply=false;
bool mdnsStarted=false,externalConnectStarted=false;
unsigned long lastExternalReconnectAt=0;
const unsigned long EXTERNAL_RECONNECT_MS=30000;
void startMDNSIfPossible(){++mdnsCalls;}
'''
main = r'''
int main(){
 config.externalWiFiEnabled=false; updateExternalWiFi(); assert(WiFi.attempts.empty());
 config.externalWiFiEnabled=true; config.knownWiFiCount=0; updateExternalWiFi(); assert(WiFi.attempts.empty());
 config.knownWiFiCount=2;
 // Two AP clients, no scan API available: still attempt manually saved SSID.
 updateExternalWiFi(); assert(WiFi.attempts.size()==1);
 assert(WiFi.attempts[0]=="Sarah_Charles_Home" && WiFi.passwords[0]=="test-password");
 clockNow=29999; updateExternalWiFi(); assert(WiFi.attempts.size()==1);
 clockNow=30000; updateExternalWiFi(); assert(WiFi.attempts.size()==2 && WiFi.attempts[1]=="Backup");
 clockNow=60000; updateExternalWiFi(); assert(WiFi.attempts.size()==3 && WiFi.attempts[2]=="Sarah_Charles_Home");
 clockNow=90000;
 wifiScanRunning=true; updateExternalWiFi(); assert(WiFi.attempts.size()==3); wifiScanRunning=false;
 wifiScanStartRequested=true; updateExternalWiFi(); assert(WiFi.attempts.size()==3); wifiScanStartRequested=false;
 pendingExternalWiFiApply=true; updateExternalWiFi(); assert(WiFi.attempts.size()==3); pendingExternalWiFiApply=false;
 WiFi.state=WL_CONNECTED; updateExternalWiFi(); assert(WiFi.attempts.size()==3 && mdnsCalls==1);
 WiFi.state=0; updateExternalWiFi(); assert(WiFi.attempts.size()==4);
 // Single saved target is retried, never blocked on discovery or AP clients.
 config.knownWiFiCount=1; currentKnownWiFiAttempt=0; clockNow=120000;
 updateExternalWiFi(); assert(WiFi.attempts.size()==5 && WiFi.attempts.back()=="Sarah_Charles_Home");
 assert(WiFi.disconnects==5);
 puts("PASS: saved SSID retries without discovery; AP clients allowed; rotation, timing, scan guards and connected state verified");
}
'''
with tempfile.TemporaryDirectory() as temp:
    cpp=Path(temp)/'wifi.cpp'; exe=Path(temp)/'wifi-test'
    cpp.write_text(prefix+retry+update+main,encoding='utf-8')
    compiler=shutil.which('g++') or shutil.which('clang++')
    assert compiler, 'Host C++ compiler required'
    subprocess.run([compiler,'-std=c++17',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
