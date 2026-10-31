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
      saved=tcSettings;saved.enabled=old.enabled;saved.macro=old.macro;saved.port=old.port;
      memcpy(saved.ip,old.ip,4);
      if(tcSettingsValid(saved,MACRO_COUNT)) {tcSettings=saved;tcSaveSettings(tcSettings);}
    }
    return;
  }
  bool ok=f.size()==sizeof(saved) && f.read((uint8_t*)&saved,sizeof(saved))==sizeof(saved);
  f.close();
  if (ok && tcSettingsValid(saved,MACRO_COUNT) && saved.checksum==configChecksum((const uint8_t*)&saved,16)) tcSettings=saved;
  else Serial.println(F("[TRICASTER] Configuration invalide : mode manuel conserve"));
}

bool tcSaveSettings(TcRecSettings& value) {
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
  if (!tcControlActive()) return;
  tcPaused=true; tcApplied=-1;
  Serial.println(F("[TRICASTER] Suivi REC/STREAM suspendu par OFF"));
}

const char* tcStatusText() {
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
  if (!startupSequenceComplete || settingsPreviewActive || libraryPreviewActive || tcPaused) return;
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
  if (!tcControlActive()) return;
  String c=F("<section class='section' style='margin:12px 0'><b id='tcLiveStatus'>");
  c+=tcStatusText();
  c+=F("</b><p><a href='/settings#tricaster'>Mode et reglages TriCaster</a></p>"
    "<form method='POST' action='/tricaster/resume'><button type='submit'>Reprendre le suivi REC / STREAM</button></form></section>"
    "<script>setInterval(function(){fetch('/api/tricaster/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{var e=document.getElementById('tcLiveStatus');if(e)e.textContent=s.message}).catch(()=>{})},2000)</script>");
  sendHtmlChunk(c);
}

void tcSendSettings() {
  String c=F("<form method='POST' action='/saveTriCaster'><details id='tricaster' class='section' open>"
    "<summary>Mode de fonctionnement</summary><label>Mode</label><select name='mode'>"
    "<option value='manual'");
  if (!tcControlActive()) c+=F(" selected");
  c+=F(">Manuel</option><option value='tricaster'");
  if (tcControlActive()) c+=F(" selected");
    c+=F(">TriCaster — REC / STREAM</option></select>"
    "<p class='small'>Le boitier suit l'enregistrement et la diffusion sans commander le TriCaster.</p>"
    "<label>Adresse IP du TriCaster</label><input name='tcIP' required value='");
  c+=IPAddress(tcSettings.ip[0],tcSettings.ip[1],tcSettings.ip[2],tcSettings.ip[3]).toString();
  c+=F("'><label>Port de connexion</label><input name='tcPort' type='number' min='1' max='65535' value='");
  c+=String(tcSettings.port);
  c+=F("'><label>REC seul — emission et animation</label><select name='tcMacro'>");
  for (uint8_t i=0;i<MACRO_COUNT;++i) {
    c+=F("<option value='");c+=String(i);c+=F("'");
    if (i==tcSettings.macro)c+=F(" selected");
    c+=F(">");c+=htmlEscape(config.macro[i].name);c+=F("</option>");
  }
  c+=F("</select><label>STREAM seul — emission et animation</label><select name='tcStreamMacro'>");
  for (uint8_t i=0;i<MACRO_COUNT;++i) {
    c+=F("<option value='");c+=String(i);c+=F("'");
    if(i==tcSettings.streamMacro)c+=F(" selected");
    c+=F(">");c+=htmlEscape(config.macro[i].name);c+=F("</option>");
  }
  c+=F("</select><label>REC + STREAM — emission et animation</label><select name='tcBothMacro'>");
  for (uint8_t i=0;i<MACRO_COUNT;++i) {
    c+=F("<option value='");c+=String(i);c+=F("'");
    if(i==tcSettings.bothMacro)c+=F(" selected");
    c+=F(">");c+=htmlEscape(config.macro[i].name);c+=F("</option>");
  }
  c+=F("</select><label>Wi-Fi du routeur de regie</label>"
    "<input name='tcSSID' maxlength='32' value='"
  );
  if(config.knownWiFiCount)c+=htmlEscape(config.knownWiFi[0].ssid);
  c+=F("' placeholder='Nom du Wi-Fi de regie'>"
    "<label>Mot de passe Wi-Fi</label><input name='tcPassword' type='password' maxlength='64' autocomplete='new-password' placeholder='Vide : conserver celui de ce reseau'>"
    "<p class='small'>Choisis une emission differente pour chacun des trois cas. "
    "Personnalise leurs animations dans les reglages des emissions. REC et STREAM arretes : extinction. "
    "Orange clignotant : connexion ou etats indisponibles. OFF suspend le suivi jusqu'a Reprendre.</p>"
    "<button type='submit' class='save'>ENREGISTRER LE MODE</button></details></form>");
  sendHtmlChunk(c);
  tcSendBanner();
}

void tcHandleSave() {
  String mode=server.arg("mode");
  IPAddress ip;
  long port=server.arg("tcPort").toInt();
  long macro=server.arg("tcMacro").toInt();
  long streamMacro=server.arg("tcStreamMacro").toInt();
  long bothMacro=server.arg("tcBothMacro").toInt();
  if ((mode!="manual" && mode!="tricaster") || !server.hasArg("tcMacro") ||
      !server.hasArg("tcStreamMacro") || !server.hasArg("tcBothMacro") ||
      !ip.fromString(server.arg("tcIP")) || port<1 || port>65535 || macro<0 || macro>=MACRO_COUNT ||
      streamMacro<0 || streamMacro>=MACRO_COUNT || bothMacro<0 || bothMacro>=MACRO_COUNT) {
    server.send_P(400,PSTR("text/plain"),PSTR("Mode, IP, port ou emission invalide"));return;
  }
  TcRecSettings value=tcSettings;
  value.enabled=mode=="tricaster";value.macro=macro;value.port=port;
  value.streamMacro=streamMacro;value.bothMacro=bothMacro;
  for(uint8_t i=0;i<4;++i)value.ip[i]=ip[i];
  if(!tcSettingsValid(value,MACRO_COUNT)) {
    server.send_P(400,PSTR("text/plain"),PSTR("Adresse TriCaster invalide"));return;
  }
  String ssid=server.arg("tcSSID"),password=server.arg("tcPassword");ssid.trim();
  if(value.enabled && (ssid.length()==0 || ssid.length()>32 || password.length()>64 ||
      (password.length()>0 && password.length()<8) || (findKnownWiFi(ssid)<0 && password.length()==0))) {
    server.send_P(400,PSTR("text/plain"),PSTR("Renseigne le Wi-Fi de regie et son mot de passe s'il n'est pas deja memorise"));return;
  }
  if(!tcSaveSettings(value)) {server.send_P(500,PSTR("text/plain"),PSTR("Echec sauvegarde du mode : reglages precedents conserves"));return;}
  tcResetConnection();tcSettings=value;tcPaused=false;
  libraryPreviewActive=false;settingsPreviewActive=false;blackout();
  if(value.enabled) {
    rememberWiFi(ssid,password);config.externalWiFiEnabled=true;saveConfig();
    pendingExternalWiFiApply=true;pendingExternalWiFiApplyAt=millis()+EXTERNAL_APPLY_DELAY_MS;
  }
  server.sendHeader("Location","/settings#tricaster",true);
  server.send_P(303,PSTR("text/plain"),PSTR(""));
}

void tcSetupRoutes() {
  server.on("/saveTriCaster",HTTP_POST,tcHandleSave);
  server.on("/api/tricaster/status",HTTP_GET,tcStatus);
  server.on("/tricaster/resume",HTTP_POST,[](){
    tcPaused=false;tcApplied=-1;
    server.sendHeader("Location","/",true);
    server.send_P(303,PSTR("text/plain"),PSTR(""));
  });
}
