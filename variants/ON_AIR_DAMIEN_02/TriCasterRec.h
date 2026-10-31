#pragma once

bool tcControlActive() { return tcSettings.enabled!=0; }

void tcLoadSettings() {
  File f=LittleFS.open("/tricaster.cfg","r");
  if (!f) return;
  TcRecSettings saved={};
  if (f.size()==sizeof(TcRecLegacySettings)) {
    TcRecLegacySettings old={};
    bool valid=f.read((uint8_t*)&old,sizeof(old))==sizeof(old);
    f.close();
    if(valid && old.magic==0x54435231UL && old.enabled<=1 && old.macro<MACRO_COUNT && old.port &&
       old.checksum==configChecksum((const uint8_t*)&old,12)) {
      saved=tcSettings;saved.enabled=old.enabled;saved.port=old.port;
      memcpy(saved.ip,old.ip,4);
      if(tcSettingsValid(saved,MACRO_COUNT)) {tcSettings=saved;tcSaveSettings(tcSettings);}
    }
    return;
  }
  bool ok=f.size()==sizeof(saved) && f.read((uint8_t*)&saved,sizeof(saved))==sizeof(saved);
  f.close();
  if(ok && saved.magic==0x54435232UL && saved.enabled<=1 && saved.checksum==configChecksum((const uint8_t*)&saved,16)) {
    saved.magic=0x54435233UL;saved.macro=1;saved.streamMacro=2;saved.bothMacro=3;saved.reserved=0;
    if(tcSettingsValid(saved,MACRO_COUNT)){tcSettings=saved;tcSaveSettings(tcSettings);}
  }
  else if (ok && tcSettingsValid(saved,MACRO_COUNT) && saved.checksum==configChecksum((const uint8_t*)&saved,16)) tcSettings=saved;
  else Serial.println(F("[TRICASTER] Configuration invalide : mode manuel conserve"));
}

bool tcSaveSettings(TcRecSettings& value) {
  if(!tcSettingsValid(value,MACRO_COUNT))return false;
  value.checksum=configChecksum((const uint8_t*)&value,16);
  File f=LittleFS.open("/tricaster.tmp","w");
  if (!f) return false;
  bool ok=f.write((const uint8_t*)&value,sizeof(value))==sizeof(value);
  f.close();
  return ok && LittleFS.rename("/tricaster.tmp","/tricaster.cfg");
}

void tcResetConnection() {
  tcClient.stop(); tcParser.reset(); tcKnown=false;
  tcRecKnown=false;tcStreamKnown=false;tcRecording=false;tcStreaming=false;
  tcApplied=-1; tcLastAttempt=0;
}

void tcPause() {
  tcManualOverride=false;
  if (!tcControlActive()) return;
  tcPaused=true; tcApplied=-1;
  Serial.println(F("[TRICASTER] Suivi REC/STREAM suspendu par OFF"));
}

void tcReleaseManual() {
  tcManualOverride=false;tcPaused=false;tcApplied=-1;
  blackout();
}

const char* tcStatusText() {
  if(tcManualOverride) return "CARAC : priorite manuelle";
  if (!tcControlActive()) return "Mode manuel";
  if (tcPaused) return "Suivi REC/STREAM suspendu par OFF";
  if (WiFi.status()!=WL_CONNECTED) return "TriCaster : attente du Wi-Fi";
  if (!tcClient.connected()) return "TriCaster : connexion en cours";
  if (!tcKnown) return "TriCaster : attente des etats REC et STREAM";
  if(tcRecording && tcStreaming) return "TriCaster : REC + STREAM";
  if(tcRecording) return "TriCaster : REC seul";
  if(tcStreaming) return "TriCaster : STREAM seul";
  return "TriCaster : REC et STREAM arretes";
}

void tcStatus() {
  String json=F("{\"mode\":\""); json+=tcControlActive()?"tricaster":"manual";
  json+=F("\",\"paused\":");json+=tcPaused?"true":"false";
  json+=F(",\"connected\":");json+=tcClient.connected()?"true":"false";
  json+=F(",\"rec\":");json+=tcRecKnown?(tcRecording?"true":"false"):"null";
  json+=F(",\"stream\":");json+=tcStreamKnown?(tcStreaming?"true":"false"):"null";
  json+=F(",\"updates\":");json+=String(tcUpdates);
  json+=F(",\"message\":\"");json+=tcStatusText();json+=F("\"}");
  server.sendHeader("Cache-Control","no-store");
  server.send(200,"application/json",json);
}

void tcUpdate() {
  if (!tcControlActive()) return;
  uint32_t now=millis();
  if (WiFi.status()!=WL_CONNECTED) {
    if (tcClient.connected() || tcKnown) tcResetConnection();
  } else if (!tcClient.connected()) {
    // A disconnected socket may still contain a final packet: discard it.
    tcKnown=false;
    tcRecKnown=false;tcStreamKnown=false;tcRecording=false;tcStreaming=false;
    if (!tcLastAttempt || (uint32_t)(now-tcLastAttempt)>=3000UL) {
      tcLastAttempt=now;
      tcClient.stop();tcParser.reset();
      IPAddress ip(tcSettings.ip[0],tcSettings.ip[1],tcSettings.ip[2],tcSettings.ip[3]);
      // Bounded connect only; all state ingestion below is incremental.
      tcClient.setTimeout(80);
      if (tcClient.connect(ip,tcSettings.port)) {
        tcClient.setNoDelay(true);
        tcClient.keepAlive(5,5,3);
        tcClient.print(F("<register name=\"NTK_states\"/>\n"));
        tcConnectedAt=now;tcHeartbeatAt=now;
        Serial.println(F("[TRICASTER] Connecte : abonnement aux etats REC et STREAM"));
      }
    }
  }
  if (tcClient.connected()) {
    unsigned long started=micros();
    unsigned budget=1024;
    while (budget-- && tcClient.available() && (uint32_t)(micros()-started)<2000UL) {
      int value=tcParser.feed((char)tcClient.read());
      if (value>=0) {
        if (value<2) {
          if(!tcRecKnown || tcRecording!=(value==1)) {
            Serial.println(value==1?F("[TRICASTER] REC ON"):F("[TRICASTER] REC OFF"));tcApplied=-1;
          }
          tcRecKnown=true;tcRecording=value==1;
        } else {
          if(!tcStreamKnown || tcStreaming!=(value==3)) {
            Serial.println(value==3?F("[TRICASTER] STREAM ON"):F("[TRICASTER] STREAM OFF"));tcApplied=-1;
          }
          tcStreamKnown=true;tcStreaming=value==3;
        }
        tcKnown=tcRecKnown && tcStreamKnown;++tcUpdates;
      }
    }
    // No periodic REC changes are expected while a recording runs. TCP
    // keepalive detects link loss without treating an idle stream as REC OFF.
    if (!tcKnown && (uint32_t)(now-tcConnectedAt)>10000UL) {
      Serial.println(F("[TRICASTER] Etats REC/STREAM incomplets : nouvelle connexion"));
      tcClient.stop();tcParser.reset();
    } else if ((uint32_t)(now-tcHeartbeatAt)>=5000UL) {
      tcHeartbeatAt=now;tcClient.print('\n');
    }
  }
  if (!startupSequenceComplete || settingsPreviewActive || libraryPreviewActive || tcPaused || tcManualOverride) return;
  if (!tcKnown || !tcClient.connected() || WiFi.status()!=WL_CONNECTED) {
    if (tcApplied!=2) { blackout();tcApplied=2; }
    static uint32_t lastErrorFrame=0;
    if ((uint32_t)(now-lastErrorFrame)>=100UL) {
      lastErrorFrame=now;
      setRGBLevel(255,130,0,((now/500UL)&1)?12:0);
    }
  } else if (tcRecording || tcStreaming) {
    int selected=tcSelectedMacro(tcSettings,tcRecKnown,tcStreamKnown,tcRecording,tcStreaming);
    if (tcApplied!=1 || !outputEnabled || activeMacro!=selected) {
      applyMacro(selected);tcApplied=1;
    }
  } else if (tcApplied!=0 || outputEnabled || activeMacro>=0) {
    blackout();tcApplied=0;
  }
}



void tcSendBanner() {
  String c=F("<section class='usage-panel'><div><span class='eyebrow'>PILOTAGE</span><h2>CARAC garde la priorite</h2>"
    "<p id='tcLiveStatus' role='status'>");
  c+=tcStatusText();
  c+=F("</p></div><div class='usage-switch'><form method='POST' action='/usage/mode'>"
    "<input type='hidden' name='mode' value='manual'><button type='submit' aria-pressed='");
  c+=tcControlActive()?"false":"true";
  c+=F("'>CARAC uniquement</button></form><form method='POST' action='/usage/mode'>"
    "<input type='hidden' name='mode' value='tricaster'><button type='submit' aria-pressed='");
  c+=tcControlActive()?"true":"false";
  c+=F("'>CARAC + TriCaster</button></form></div><a class='small' href='/settings#tricaster'>Regler la connexion TriCaster →</a>");
  if(tcControlActive()) c+=F("<form method='POST' action='/tricaster/resume'><button type='submit' class='resume-button'>Reprendre le suivi automatique</button></form>");
  c+=F("</section><script>setInterval(function(){fetch('/api/tricaster/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{const e=document.getElementById('tcLiveStatus');if(e)e.textContent=s.message}).catch(()=>{})},2000)</script>");
  sendHtmlChunk(c);
}

void tcSendAutomaticCard(uint8_t i) {
  String c=F("<section class='card automatic-card' id='macro-");c+=String(i);
  c+=F("'><div class='macrohead'>");
  if(logoAvailable(i)){c+=F("<img class='logo' alt='' src='/logo?i=");c+=String(i);c+=F("'>");}
  c+=F("<div class='mname'><span class='eyebrow'>TRICASTER UNIQUEMENT</span><h2>");
  c+=i==1?F("REC"):i==2?F("STREAM"):F("REC + STREAM");
  c+=F("</h2></div></div><div class='automatic-state' id='auto-state-");c+=String(i);
  c+=F("' role='status'>Etat en attente</div><a class='profile-link' href='/macro?i=");c+=String(i);
  c+=F("'>Regler l'animation →</a></section>");sendHtmlChunk(c);
}

void tcSendSettings() {
  String c=F("<form method='POST' action='/saveTriCaster'><details id='tricaster' class='section'>"
    "<summary>TriCaster — connexion automatique</summary>"
    "<p>REC, STREAM et REC + STREAM sont declenches uniquement par le TriCaster. "
    "Les commandes CARAC restent prioritaires.</p><input type='hidden' name='mode' value='");
  c+=tcControlActive()?"tricaster":"manual";
  c+=F("'><label>Adresse IP du TriCaster</label><input name='tcIP' required value='");
  c+=IPAddress(tcSettings.ip[0],tcSettings.ip[1],tcSettings.ip[2],tcSettings.ip[3]).toString();
  c+=F("'><details><summary>Connexion avancee</summary><label>Port TriCaster</label>"
    "<input name='tcPort' type='number' min='1' max='65535' value='");c+=String(tcSettings.port);
  c+=F("'></details><p class='small'>Le Wi-Fi du boitier se regle dans <a href='#network'>Connexion reseau</a>.</p>"
    "<div class='fixed-roles'><a href='/macro?i=1'>REC seul · regler l'animation →</a>"
    "<a href='/macro?i=2'>STREAM seul · regler l'animation →</a>"
    "<a href='/macro?i=3'>REC + STREAM · regler l'animation →</a></div>"
    "<button type='submit' class='save'>ENREGISTRER LA CONNEXION</button></details></form>");sendHtmlChunk(c);
}

void tcHandleSave() {
  String mode=server.arg("mode");IPAddress ip;long port=server.arg("tcPort").toInt();
  if((mode!="manual" && mode!="tricaster") || !ip.fromString(server.arg("tcIP")) || port<1 || port>65535){
    server.send_P(400,PSTR("text/plain"),PSTR("Adresse IP ou port invalide"));return;
  }
  TcRecSettings value=tcSettings;
  value.enabled=mode=="tricaster";value.port=port;
  value.macro=1;value.streamMacro=2;value.bothMacro=3;
  for(uint8_t i=0;i<4;++i)value.ip[i]=ip[i];
  if(!tcSaveSettings(value)){server.send_P(500,PSTR("text/plain"),PSTR("Connexion non enregistree : reglages precedents conserves"));return;}
  tcResetConnection();tcSettings=value;
  server.sendHeader("Location","/settings#tricaster",true);server.send_P(303,PSTR("text/plain"),PSTR(""));
}

void tcSetupRoutes() {
  server.on("/saveTriCaster",HTTP_POST,tcHandleSave);
  server.on("/api/tricaster/status",HTTP_GET,tcStatus);
  server.on("/usage/mode",HTTP_POST,[](){
    String mode=server.arg("mode");
    if(mode!="manual" && mode!="tricaster"){server.send_P(400,PSTR("text/plain"),PSTR("Mode invalide"));return;}
    bool enable=mode=="tricaster";
    if(enable && (tcSettings.ip[0]==192 && tcSettings.ip[1]==0 && tcSettings.ip[2]==2)){
      server.sendHeader("Location","/settings#tricaster",true);server.send_P(303,PSTR("text/plain"),PSTR(""));return;
    }
    if(enable && (!config.externalWiFiEnabled || !config.knownWiFiCount)){
      server.sendHeader("Location","/settings#network",true);server.send_P(303,PSTR("text/plain"),PSTR(""));return;
    }
    TcRecSettings value=tcSettings;value.enabled=enable;
    if(!tcSaveSettings(value)){server.send_P(500,PSTR("text/plain"),PSTR("Mode non enregistre"));return;}
    tcResetConnection();tcSettings=value;tcPaused=false;
    // Keep a manual CARAC direct/alert running when changing automatic follow.
    if(!tcManualOverride)blackout();
    server.sendHeader("Location","/",true);server.send_P(303,PSTR("text/plain"),PSTR(""));
  });
  server.on("/usage/release",HTTP_POST,[](){
    tcReleaseManual();server.sendHeader("Location","/",true);server.send_P(303,PSTR("text/plain"),PSTR(""));
  });
  server.on("/tricaster/resume",HTTP_POST,[](){
    tcReleaseManual();server.sendHeader("Location","/",true);server.send_P(303,PSTR("text/plain"),PSTR(""));
  });
}
