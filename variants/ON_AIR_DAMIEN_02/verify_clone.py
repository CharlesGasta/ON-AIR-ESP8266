from pathlib import Path
import hashlib
root = Path(__file__).resolve().parents[2]
source = (root / "ON_AIR_ESP8266.ino").read_bytes()
clone = (Path(__file__).parent / "ON_AIR_DAMIEN_02.ino").read_bytes()
assert hashlib.sha256(source).hexdigest() == "7b3010ae8240ad5f1682806d45ad3e967c754fe2ac6b2226f4d709422a0fdafd", "Original source changed"
expected = source.replace(b"ON_AIR-MOC", b"ON_AIR-MOC-02").replace(b"onair-moc", b"onair-moc-02")
assert clone == expected, "Clone contains a change beyond device identifiers"
assert b'const uint16_t LED_COUNT = 36;' in clone
assert b'const uint8_t LED_DATA_PIN = D5;' in clone
assert b'strlcpy(config.apSSID, DEFAULT_AP_SSID, sizeof(config.apSSID));' in clone
assert b'strlcpy(config.deviceName, "ON_AIR-MOC-02", sizeof(config.deviceName));' in clone
assert b'const char* MDNS_HOSTNAME = "onair-moc-02";' in clone
assert b'const char* DEFAULT_AP_PASSWORD = "12345678";' in clone
print("PASS: original unchanged; clone differs only in identifiers; defaults, 36 LEDs and D5 verified.")
