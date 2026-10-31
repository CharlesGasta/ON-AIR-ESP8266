#pragma once
#include "TriCasterRecCore.h"

TcRecSettings tcSettings = {0x54435232UL,0,0,5951,{192,0,2,1},1,2,0,0};
WiFiClient tcClient;
TcRecParser tcParser;
bool tcKnown=false, tcRecording=false, tcPaused=false;
bool tcRecKnown=false, tcStreamKnown=false, tcStreaming=false;
uint32_t tcLastAttempt=0, tcConnectedAt=0, tcHeartbeatAt=0;
uint32_t tcUpdates=0;
int tcApplied=-1;

bool tcControlActive();
void tcLoadSettings();
void tcUpdate();
void tcPause();
void tcSendSettings();
void tcSendBanner();
void tcSetupRoutes();
bool tcSaveSettings(TcRecSettings& value);
