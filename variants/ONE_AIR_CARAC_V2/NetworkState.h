#pragma once
NetworkSettings networkSettings={0x4e455431UL,{}, {},0};
bool netReconfigurePending=false;
void netLoad();
bool netApply(const char* ssid);
void netSetupRoutes();
void netSendSettings();
void netForgetProfile(const String& ssid);
bool netSave(NetworkSettings& value);
