"""Protect the historical EEPROM data layout while extending LED features."""
from pathlib import Path
import subprocess,re
root=Path(__file__).resolve().parents[1]
old=subprocess.check_output(['git','show','efefbef:ON_AIR_ESP8266.ino'],cwd=root).decode('utf-8')
new=(Path(__file__).resolve().parents[1]/'ON_AIR_ESP8266.ino').read_text(encoding='utf-8')
def structure(s,name):
    return re.search(r'\bstruct '+name+r'\s*\{[^}]+};',s).group()
for name in ['MacroConfigV19','MacroConfigV25','MacroConfig','KnownWiFi','ConfigV11','ConfigSingleWiFi','ConfigV19','ConfigV25','Config','BackupHeader']:
    assert structure(old,name)==structure(new,name),name+' historical data layout changed'
for name in ['CONFIG_MAGIC','EEPROM_SIZE','LED_COUNT','LED_DATA_PIN','LED_GLOBAL_MAX_PERCENT']:
    pattern=r'^const [^\n]+\b'+name+r' = [^;]+;'
    assert re.search(pattern,old,re.M).group()==re.search(pattern,new,re.M).group(),name
assert 'header.backupVersion==1&&header.configSize==sizeof(Config)' in new
assert 'loadMotionSettings();' in new
assert 'updateDirectMotion();' in new
engine=new.split('// BEGIN PORTABLE MOTION ENGINE')[1].split('// END PORTABLE MOTION ENGINE')[0]
assert 'delay(' not in engine and 'EEPROM' not in engine and 'LittleFS' not in engine
assert 'STARTUP_IND_FALLBACK' in new and '15000UL' in new
print('PASS: historical EEPROM structures/magic, 36 LEDs, pin and 100% ceiling unchanged; legacy backups accepted; spatial engine has no blocking waits or persistence.')

# The approved boot cinematic and rainbow branch must remain byte-identical.
import subprocess
previous=subprocess.check_output(['git','show','9fd36bbb627346f8e6a70c49339bc49a015df8f1:ON_AIR_ESP8266.ino'],text=True,encoding='utf-8')
current=(Path(__file__).resolve().parents[1]/'ON_AIR_ESP8266.ino').read_text(encoding='utf-8')
for text in (previous,current):
    assert 'if(mode==6)motionRainbow(x*.8f-p,frame[i],peak);' in text
assert previous.split('bool renderBootFrame(')[1].split('// END PORTABLE MOTION ENGINE')[0] == current.split('bool renderBootFrame(')[1].split('// END PORTABLE MOTION ENGINE')[0]
print('PASS: approved boot cinematic and horizontal rainbow unchanged')
