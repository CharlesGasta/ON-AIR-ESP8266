"""Reject firmware whose static RAM leaves too little space for Wi-Fi and HTTP."""
from pathlib import Path
import re, sys
text=Path(sys.argv[1]).read_text(encoding="utf-8",errors="replace")
m=re.search(r"Variables and constants in RAM.*?used\s+(\d+)\s*/",text)
assert m,"ESP8266 RAM report missing"
used=int(m.group(1))
print(f"Static RAM: {used} bytes; maximum allowed: 55000 bytes")
assert used <= 55000,"Static RAM budget exceeded: HTTP/Wi-Fi need more dynamic memory"
