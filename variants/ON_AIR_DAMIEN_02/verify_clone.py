from pathlib import Path
import hashlib,re
root=Path(__file__).resolve().parents[2]
original=(root/'ON_AIR_ESP8266.ino').read_text(encoding='utf8')
new=(Path(__file__).parent/'ON_AIR_DAMIEN_02.ino').read_text(encoding='utf8')
assert hashlib.sha256(original.encode()).hexdigest()=='7b3010ae8240ad5f1682806d45ad3e967c754fe2ac6b2226f4d709422a0fdafd'
old=original.replace('ON_AIR-MOC','ON_AIR-MOC-02').replace('onair-moc','onair-moc-02')
# Preserve all persistence, LED rendering, animation library and complete UI.
for start,end in [('const uint8_t LED_DATA_PIN','unsigned long lastExternalReconnectAt'),('String htmlEscape(', 'void beginWiFiScanAsync()'),('void finishWiFiScan(', 'void startAccessPoint()')]:
    assert old[old.index(start):old.index(end)] == new[new.index(start):new.index(end)], start
for name in ['MacroConfig','KnownWiFi','Config','BackupHeader']:
    pattern=r'\bstruct '+name+r'\s*\{[^}]+};'
    assert re.search(pattern,old).group()==re.search(pattern,new).group()
assert 'WiFi.scanNetworks(true, true)' in new
print('PASS: original unchanged; EEPROM, 36 LEDs/D5, motion engine, editor, library, UI and OTA preserved')
