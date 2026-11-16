#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>

struct NetworkProfile {
  char ssid[33];
  uint8_t mode; // 0 DHCP, 1 static
  uint8_t ip[4],gateway[4],mask[4],dns1[4],dns2[4];
};
struct NetworkSettings {
  uint32_t magic;
  NetworkProfile profiles[5];
  uint8_t reserved[2];
  uint32_t checksum;
};
static_assert(sizeof(NetworkProfile)==54,"Network profile layout");
static_assert(sizeof(NetworkSettings)==280,"Network settings layout");
inline bool netProfileValid(const NetworkProfile& p);
inline bool netSettingsValid(const NetworkSettings& s);

inline uint32_t netNumber(const uint8_t* a) {
  return ((uint32_t)a[0]<<24)|((uint32_t)a[1]<<16)|((uint32_t)a[2]<<8)|a[3];
}
inline bool netUnicast(uint32_t ip) {
  return (ip>>24)>0 && (ip>>24)<224 && (ip>>24)!=127;
}
inline bool netProfileValid(const NetworkProfile& p) {
  if(!memchr(p.ssid,0,sizeof(p.ssid)) || p.mode>1)return false;
  if(!p.ssid[0])return p.mode==0;
  if(p.mode==0)return true;
  uint32_t ip=netNumber(p.ip),gw=netNumber(p.gateway),mask=netNumber(p.mask),inverse=~mask;
  if(!netUnicast(ip)||!netUnicast(gw)||!mask||inverse<3||(inverse&(inverse+1)))return false;
  if((ip&mask)!=(gw&mask)||ip==gw)return false;
  if(!(ip&inverse)||(ip&inverse)==inverse||!(gw&inverse)||(gw&inverse)==inverse)return false;
  // A static station subnet must not overlap the autonomous rescue AP.
  uint32_t low=ip&mask,high=low|inverse,apLow=0xc0a80400UL,apHigh=0xc0a804ffUL;
  if(low<=apHigh && high>=apLow)return false;
  uint32_t dns1=netNumber(p.dns1),dns2=netNumber(p.dns2);
  return (!dns1||netUnicast(dns1)) && (!dns2||netUnicast(dns2));
}
inline bool netSettingsValid(const NetworkSettings& s) {
  if(s.magic!=0x4e455431UL || s.reserved[0] || s.reserved[1])return false;
  for(unsigned i=0;i<5;++i){
    if(!netProfileValid(s.profiles[i]))return false;
    for(unsigned j=0;j<i;++j)if(s.profiles[i].ssid[0]&&!strcmp(s.profiles[i].ssid,s.profiles[j].ssid))return false;
  }
  return true;
}
