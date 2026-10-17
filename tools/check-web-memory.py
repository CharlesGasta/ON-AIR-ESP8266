"""Exercise the actual admission guard under healthy, depleted and fragmented RAM."""
from pathlib import Path
import re,shutil,subprocess,tempfile
s=(Path(__file__).resolve().parents[1]/"ON_AIR_ESP8266.ino").read_text(encoding="utf-8")
body=re.search(r"bool webMemoryReady\(\)\{.*?^\}",s,re.S|re.M).group()
code=r"""
#include <stdint.h>
#include <cassert>
#include <iostream>
#define F(x) x
#define PSTR(x) x
uint32_t webMinimumHeap=0,webRefusedPages=0;
struct {uint32_t heap=24000,block=18000;uint32_t getFreeHeap(){return heap;}uint32_t getMaxFreeBlockSize(){return block;}} ESP;
struct {int code=0;void sendHeader(const char*,const char*){}void send_P(int c,const char*,const char*){code=c;}} server;
"""+body+r"""
int main(){
 for(int i=0;i<10000;i++)assert(webMemoryReady());
 assert(webRefusedPages==0);ESP.heap=3336;ESP.block=3032;assert(!webMemoryReady());assert(server.code==503);
 ESP.heap=24000;ESP.block=5000;assert(!webMemoryReady());
 ESP.heap=12000;ESP.block=6000;assert(webMemoryReady());
 assert(webMinimumHeap==3336&&webRefusedPages==2);
 std::cout<<"PASS: healthy requests accepted; exhausted and fragmented memory refused; recovery accepted\n";
}
"""
compiler=shutil.which("g++") or shutil.which("clang++")
assert compiler,"Host compiler required"
with tempfile.TemporaryDirectory() as d:
 source=Path(d)/"test.cpp";binary=Path(d)/"test";source.write_text(code,encoding="utf-8")
 subprocess.run([compiler,"-std=c++11",str(source),"-o",str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
