from pathlib import Path
import hashlib,re
root=Path(__file__).resolve().parents[2]
old=(root/'ON_AIR_ESP8266.ino').read_text(encoding='utf8')
new=(Path(__file__).parent/'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf8')
assert hashlib.sha256(old.encode()).hexdigest()=='7b3010ae8240ad5f1682806d45ad3e967c754fe2ac6b2226f4d709422a0fdafd','Original Damien source changed'
for name in ['MacroConfig','KnownWiFi','Config','BackupHeader']:
 pattern=r'\bstruct '+name+r'\s*\{[^}]+};'
 assert re.search(pattern,old).group()==re.search(pattern,new).group(),name
start='// BEGIN PORTABLE MOTION ENGINE';end='// END PORTABLE MOTION ENGINE'
assert old.split(start)[1].split(end)[0]==new.split(start)[1].split(end)[0]
for marker,next_marker in [('static const char COMMON_CSS','void sendControlPage()'),('void sendMacroSettingsPage(', 'String statusJSON()')]:
 assert old[old.index(marker):old.index(next_marker)]==new[new.index(marker):new.index(next_marker)],marker
assert 'const uint8_t LED_DATA_PIN = D5;' in new
assert 'const uint16_t LED_COUNT = 36;' in new
assert 'const char* MDNS_HOSTNAME = "onair-moc-02";' in new
assert 'const char* DEFAULT_AP_SSID = "ON_AIR-MOC-02";' in new
assert '  tcLoadSettings();' in new and '  tcUpdate();' in new
print('PASS: original untouched; EEPROM/backup layouts, LED engine, editor, macro settings and identities preserved')
