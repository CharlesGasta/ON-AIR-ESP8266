#pragma once

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
