#pragma once

bool tcControlActive() { return tcSettings.enabled!=0; }

void tcLoadSettings() {
  File f=LittleFS.open("/tricaster.cfg","r");
  if (!f) return;
  TcRecSettings saved={};
  bool ok=f.size()==sizeof(saved) && f.read((uint8_t*)&saved,sizeof(saved))==sizeof(saved);
  f.close();
  if (ok && tcSettingsValid(saved,MACRO_COUNT) && saved.checksum==configChecksum((const uint8_t*)&saved,12)) tcSettings=saved;
  else Serial.println(F("[TRICASTER] Configuration invalide : mode manuel conserve"));
}

bool tcSaveSettings(TcRecSettings& value) {
  value.checksum=configChecksum((const uint8_t*)&value,12);
  File f=LittleFS.open("/tricaster.tmp","w");
  if (!f) return false;
  bool ok=f.write((const uint8_t*)&value,sizeof(value))==sizeof(value);
  f.close();
  return ok && LittleFS.rename("/tricaster.tmp","/tricaster.cfg");
}

void tcResetConnection() {
  tcClient.stop(); tcParser.reset(); tcKnown=false;
  tcApplied=-1; tcLastAttempt=0;
}

void tcPause() {
  if (!tcControlActive()) return;
  tcPaused=true; tcApplied=-1;
  Serial.println(F("[TRICASTER] Suivi REC suspendu par OFF"));
}

const char* tcStatusText() {
  if (!tcControlActive()) return "Mode manuel";
  if (tcPaused) return "Suivi REC suspendu par OFF";
  if (WiFi.status()!=WL_CONNECTED) return "TriCaster : attente du Wi-Fi";
  if (!tcClient.connected()) return "TriCaster : connexion en cours";
  if (!tcKnown) return "TriCaster : attente de l'etat REC";
  return tcRecording ? "TriCaster : REC en cours" : "TriCaster : REC arrete";
}

void tcStatus() {
  String json=F("{\"mode\":\""); json+=tcControlActive()?"tricaster":"manual";
  json+=F("\",\"paused\":");json+=tcPaused?"true":"false";
  json+=F(",\"connected\":");json+=tcClient.connected()?"true":"false";
  json+=F(",\"rec\":");json+=tcKnown?(tcRecording?"true":"false"):"null";
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
        Serial.println(F("[TRICASTER] Connecte : abonnement aux etats REC"));
      }
    }
  }
  if (tcClient.connected()) {
    unsigned long started=micros();
    unsigned budget=1024;
    while (budget-- && tcClient.available() && (uint32_t)(micros()-started)<2000UL) {
      int value=tcParser.feed((char)tcClient.read());
      if (value>=0) {
        if (!tcKnown || tcRecording!=(value==1)) {
          Serial.println(value?F("[TRICASTER] REC ON"):F("[TRICASTER] REC OFF"));
          tcApplied=-1;
        }
        tcKnown=true;tcRecording=value==1;++tcUpdates;
      }
    }
    // No periodic REC changes are expected while a recording runs. TCP
    // keepalive detects link loss without treating an idle stream as REC OFF.
    if (!tcKnown && (uint32_t)(now-tcConnectedAt)>10000UL) {
      Serial.println(F("[TRICASTER] Aucun etat REC recu : nouvelle connexion"));
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
  } else if (tcRecording) {
    if (tcApplied!=1 || !outputEnabled || activeMacro!=tcSettings.macro) {
      applyMacro(tcSettings.macro);tcApplied=1;
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
    "<form method='POST' action='/tricaster/resume'><button type='submit'>Reprendre le suivi REC</button></form></section>"
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
  c+=F(">TriCaster — suivre REC</option></select>"
    "<p class='small'>Le boitier lit l'enregistrement. Il ne commande pas le TriCaster.</p>"
    "<label>Adresse IP du TriCaster</label><input name='tcIP' required value='");
  c+=IPAddress(tcSettings.ip[0],tcSettings.ip[1],tcSettings.ip[2],tcSettings.ip[3]).toString();
  c+=F("'><label>Port de connexion</label><input name='tcPort' type='number' min='1' max='65535' value='");
  c+=String(tcSettings.port);
  c+=F("'><label>Emission allumee pendant REC</label><select name='tcMacro'>");
  for (uint8_t i=0;i<MACRO_COUNT;++i) {
    c+=F("<option value='");c+=String(i);c+=F("'");
    if (i==tcSettings.macro)c+=F(" selected");
    c+=F(">");c+=htmlEscape(config.macro[i].name);c+=F("</option>");
  }
  c+=F("</select><label>Wi-Fi du routeur de regie</label>"
    "<input name='tcSSID' maxlength='32' value='CARAC 2.4G'>"
    "<label>Mot de passe Wi-Fi</label><input name='tcPassword' type='password' maxlength='64' autocomplete='new-password' placeholder='Vide : conserver celui de ce reseau'>"
    "<p class='small'>REC allume l'emission avec son animation. REC arrete eteint le boitier. "
    "Orange clignotant : connexion ou etat REC indisponible. OFF suspend le suivi jusqu'a Reprendre.</p>"
    "<button type='submit' class='save'>ENREGISTRER LE MODE</button></details></form>");
  sendHtmlChunk(c);
  tcSendBanner();
}

void tcHandleSave() {
  String mode=server.arg("mode");
  IPAddress ip;
  long port=server.arg("tcPort").toInt();
  long macro=server.arg("tcMacro").toInt();
  if ((mode!="manual" && mode!="tricaster") || !server.hasArg("tcMacro") ||
      !ip.fromString(server.arg("tcIP")) || port<1 || port>65535 || macro<0 || macro>=MACRO_COUNT) {
    server.send_P(400,PSTR("text/plain"),PSTR("Mode, IP, port ou emission invalide"));return;
  }
  TcRecSettings value=tcSettings;
  value.enabled=mode=="tricaster";value.macro=macro;value.port=port;
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
