#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <ctype.h>

// Streaming parser: never allocate a full TriCaster state dictionary.
// A return value of -1 means no valid REC update, 0 stopped, 1 recording.
class TcRecParser {
  char tag[320];
  size_t used = 0;
  bool collecting = false, overflow = false;
  char quote = 0;
  static bool attribute(const char* text, const char* wanted, char* out, size_t capacity) {
    const char* p = text;
    while (*p && !isspace((unsigned char)*p) && *p != '>') ++p;
    while (*p) {
      while (isspace((unsigned char)*p) || *p=='/') ++p;
      if (!*p || *p=='>') break;
      const char* name=p;
      while (isalnum((unsigned char)*p) || *p=='_' || *p=='-' || *p==':') ++p;
      size_t length=p-name;
      if (!length) return false;
      while (isspace((unsigned char)*p)) ++p;
      if (*p++ != '=') return false;
      while (isspace((unsigned char)*p)) ++p;
      char q=*p++;
      if (q!='\'' && q!='"') return false;
      const char* value=p;
      while (*p && *p!=q) ++p;
      if (!*p) return false;
      size_t n=p-value;
      ++p;
      if (length==strlen(wanted) && !strncmp(name,wanted,length)) {
        if (n>=capacity) return false;
        memcpy(out,value,n); out[n]=0; return true;
      }
    }
    return false;
  }
  int parse() {
    const char* p=tag;
    if (*p++!='<') return -1;
    const char* name=p;
    while (*p && !isspace((unsigned char)*p) && *p!='/' && *p!='>') ++p;
    if ((size_t)(p-name)!=14 || strncmp(name,"shortcut_state",14)) return -1;
    char key[48], value[16];
    if (!attribute(tag,"name",key,sizeof(key)) || strcmp(key,"record_toggle")) return -1;
    if (!attribute(tag,"value",value,sizeof(value))) return -1;
    if (!strcmp(value,"1") || !strcmp(value,"true")) return 1;
    if (!strcmp(value,"0") || !strcmp(value,"false")) return 0;
    return -1;
  }
public:
  void reset() { used=0; collecting=false; overflow=false; quote=0; }
  int feed(char c) {
    if (c=='<' && !quote) { used=0; collecting=true; overflow=false; }
    if (!collecting) return -1;
    if (used+1<sizeof(tag)) tag[used++]=c; else overflow=true;
    if (c=='\'' || c=='"') { if (!quote) quote=c; else if (quote==c) quote=0; }
    if (c=='>' && !quote) {
      collecting=false; tag[used]=0;
      return overflow ? -1 : parse();
    }
    return -1;
  }
};

struct TcRecSettings {
  uint32_t magic;
  uint8_t enabled;
  uint8_t macro;
  uint16_t port;
  uint8_t ip[4];
  uint32_t checksum;
};
static_assert(sizeof(TcRecSettings)==16,"TriCaster settings layout");

inline bool tcSettingsValid(const TcRecSettings& s, uint8_t macroCount);
inline bool tcSettingsValid(const TcRecSettings& s, uint8_t macroCount) {
  return s.magic==0x54435231UL && s.enabled<=1 && s.macro<macroCount && s.port!=0 &&
    s.ip[0]>0 && s.ip[0]<224 && s.ip[0]!=127 &&
    (s.ip[0]!=255 || s.ip[1]!=255 || s.ip[2]!=255 || s.ip[3]!=255);
}
