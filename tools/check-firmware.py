"""Verify that the mobile redesign leaves the LED engine and saved data untouched."""
from pathlib import Path
import subprocess,re

root=Path(__file__).resolve().parents[1]
old=subprocess.check_output(['git','show','dfaecbc:ON_AIR_ESP8266.ino'],cwd=root).decode('utf-8')
new=(root/'ON_AIR_ESP8266.ino').read_text(encoding='utf-8')

def remove_function(s,name):
    start=s.index('void '+name+'(');brace=s.index('{',start)
    level=1;i=brace+1;quoted=False;escape=False
    while level:
        c=s[i];i+=1
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='{':level+=1
        elif c=='}':level-=1
    return s[:start]+s[i:]

def normalize(s):
    # Preserve string literals while stripping comments.
    s=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',lambda m:'' if m[0].startswith('/') else m[0],s,flags=re.S)
    s=re.sub(r'#define FIRMWARE_VERSION "[^"]*"','#define FIRMWARE_VERSION VERSION',s)
    s=re.sub(r'/style\.css\?v=\d+','/style.css',s)
    s=s.replace("<html lang='fr'>",'<html>')
    return re.sub(r'\s+','',s)

assert normalize(old[:old.index('static const char COMMON_CSS')])==normalize(new[:new.index('static const char COMMON_CSS')]),'LED engine or configuration changed'
a=old[old.index('String statusJSON()'):]
b=new[new.index('String statusJSON()'):]
for name in ['sendDiagnosticsPage']:
    a=remove_function(a,name);b=remove_function(b,name)
b=re.sub(r'static const char FIRMWARE_PAGE\[\] PROGMEM = R"FWPAGE\(.*?\)FWPAGE";','',b,flags=re.S)
b=remove_function(b,'sendFirmwarePage')
b=b.replace('server.on("/firmware", HTTP_GET, sendFirmwarePage);','')
assert normalize(a)==normalize(b),'Unexpected change to backend handlers, Wi-Fi, OTA or loop'
assert 'const uint16_t LED_COUNT = 36;' in new
assert 'const uint8_t LED_GLOBAL_MAX_PERCENT = 100;' in new
print('PASS: LED engine, config structures/defaults/migrations, backend handlers, Wi-Fi, existing OTA and loop unchanged from v3.0.4; only new firmware UI GET route added.')
