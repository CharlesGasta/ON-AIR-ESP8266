#pragma once

int netFind(const char* ssid) {
  for(uint8_t i=0;i<5;++i)if(networkSettings.profiles[i].ssid[0]&&!strcmp(networkSettings.profiles[i].ssid,ssid))return i;
  return -1;
}

void netLoad() {
  File f=LittleFS.open("/network.cfg","r");if(!f)return;
  NetworkSettings value={};
  bool ok=f.size()==sizeof(value)&&f.read((uint8_t*)&value,sizeof(value))==sizeof(value);f.close();
  if(ok&&netSettingsValid(value)&&value.checksum==configChecksum((const uint8_t*)&value,offsetof(NetworkSettings,checksum)))networkSettings=value;
  else Serial.println(F("[RESEAU] Profil IP invalide : DHCP conserve"));
}

bool netSave(NetworkSettings& value) {
  if(!netSettingsValid(value))return false;
  value.checksum=configChecksum((const uint8_t*)&value,offsetof(NetworkSettings,checksum));
  File f=LittleFS.open("/network.tmp","w");if(!f)return false;
  bool ok=f.write((const uint8_t*)&value,sizeof(value))==sizeof(value);f.close();
  return ok&&LittleFS.rename("/network.tmp","/network.cfg");
}

IPAddress netAddress(const uint8_t* a) {return IPAddress(a[0],a[1],a[2],a[3]);}

bool netApply(const char* ssid) {
  int index=netFind(ssid);
  if(index<0||networkSettings.profiles[index].mode==0){
    IPAddress zero(0,0,0,0);
    dns_setserver(0,zero);dns_setserver(1,zero);
    bool ok=WiFi.config(zero,zero,zero,zero,zero);
    Serial.println(ok?F("[RESEAU] Adressage DHCP"):F("[RESEAU] Echec activation DHCP"));return ok;
  }
  const NetworkProfile& p=networkSettings.profiles[index];
  if(!netProfileValid(p))return false;
  IPAddress zero(0,0,0,0);dns_setserver(0,zero);dns_setserver(1,zero);
  IPAddress dns1=netNumber(p.dns1)?netAddress(p.dns1):netAddress(p.gateway);
  bool ok=WiFi.config(netAddress(p.ip),netAddress(p.gateway),netAddress(p.mask),dns1,netAddress(p.dns2));
  Serial.println(ok?F("[RESEAU] Adressage IP fixe applique"):F("[RESEAU] Echec application IP fixe"));
  return ok;
}

void netForgetProfile(const String& ssid) {
  int i=netFind(ssid.c_str());if(i<0)return;
  NetworkSettings value=networkSettings;memset(&value.profiles[i],0,sizeof(NetworkProfile));
  if(netSave(value))networkSettings=value;
}

String netStatusJSON() {
  String j=F("{\"connected\":");j+=WiFi.status()==WL_CONNECTED?"true":"false";
  j+=F(",\"ssid\":\"");j+=jsonEscape(WiFi.SSID());
  j+=F("\",\"ip\":\"");j+=WiFi.localIP().toString();
  j+=F("\",\"gateway\":\"");j+=WiFi.gatewayIP().toString();
  j+=F("\",\"mask\":\"");j+=WiFi.subnetMask().toString();
  j+=F("\",\"dns1\":\"");j+=WiFi.dnsIP(0).toString();
  j+=F("\",\"dns2\":\"");j+=WiFi.dnsIP(1).toString();
  j+=F("\",\"mac\":\"");j+=WiFi.macAddress();
  j+=F("\",\"rssi\":");j+=String(WiFi.status()==WL_CONNECTED?WiFi.RSSI():0);
  j+=F(",\"ap_ip\":\"");j+=WiFi.softAPIP().toString();
  int i=netFind(WiFi.SSID().c_str());j+=F("\",\"mode\":\"");
  j+=(i>=0&&networkSettings.profiles[i].mode)?"static":"dhcp";
  j+=F("\",\"hostname\":\"");j+=MDNS_HOSTNAME;j+=F(".local\"}");return j;
}

void netProfileJSON() {
  String ssid=server.arg("ssid");int index=netFind(ssid.c_str());
  NetworkProfile p={};strlcpy(p.ssid,ssid.c_str(),sizeof(p.ssid));
  if(index>=0)p=networkSettings.profiles[index];
  else if(WiFi.status()==WL_CONNECTED&&WiFi.SSID()==ssid){
    IPAddress values[]={WiFi.localIP(),WiFi.gatewayIP(),WiFi.subnetMask(),WiFi.dnsIP(0),WiFi.dnsIP(1)};
    uint8_t* fields[]={p.ip,p.gateway,p.mask,p.dns1,p.dns2};
    for(uint8_t n=0;n<5;++n)for(uint8_t k=0;k<4;++k)fields[n][k]=values[n][k];
  }
  String j=F("{\"mode\":\"");j+=p.mode?"static":"dhcp";
  const char* keys[]={"ip","gateway","mask","dns1","dns2"};
  const uint8_t* fields[]={p.ip,p.gateway,p.mask,p.dns1,p.dns2};
  for(uint8_t n=0;n<5;++n){j+=F("\",\"");j+=keys[n];j+=F("\":\"");j+=netAddress(fields[n]).toString();}
  j+=F("\"}");server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",j);
}

bool netReadAddress(const char* key,uint8_t* out,bool optional) {
  String text=server.arg(key);text.trim();
  if(optional&&!text.length()){memset(out,0,4);return true;}
  IPAddress ip;if(!ip.fromString(text))return false;
  for(uint8_t i=0;i<4;++i)out[i]=ip[i];return true;
}

void netHandleSave() {
  String ssid=server.arg("ssid"),mode=server.arg("addressMode");ssid.trim();
  if(findKnownWiFi(ssid)<0||(mode!="dhcp"&&mode!="static")){
    server.send_P(400,PSTR("text/plain"),PSTR("Selectionne un reseau memorise et un mode IP valide"));return;
  }
  NetworkProfile p={};strlcpy(p.ssid,ssid.c_str(),sizeof(p.ssid));p.mode=mode=="static";
  if(p.mode&&(!netReadAddress("ip",p.ip,false)||!netReadAddress("gateway",p.gateway,false)||
     !netReadAddress("mask",p.mask,false)||!netReadAddress("dns1",p.dns1,true)||!netReadAddress("dns2",p.dns2,true)||!netProfileValid(p))){
    server.send_P(400,PSTR("text/plain"),PSTR("IP fixe invalide : verifier IP, masque, passerelle, DNS et absence de chevauchement avec le Wi-Fi autonome"));return;
  }
  int index=netFind(ssid.c_str());
  if(index<0)for(uint8_t i=0;i<5;++i)if(!networkSettings.profiles[i].ssid[0]||findKnownWiFi(networkSettings.profiles[i].ssid)<0){index=i;break;}
  if(index<0){server.send_P(409,PSTR("text/plain"),PSTR("Aucun emplacement de profil disponible"));return;}
  NetworkSettings value=networkSettings;value.profiles[index]=p;
  if(!netSave(value)){server.send_P(500,PSTR("text/plain"),PSTR("Profil non enregistre : reglage precedent conserve"));return;}
  networkSettings=value;rememberWiFi(ssid,"");config.externalWiFiEnabled=true;saveConfig();
  netReconfigurePending=true;pendingExternalWiFiApply=true;pendingExternalWiFiApplyAt=millis()+1500UL;
  String page=F("<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width'><h2>Reglages reseau enregistres</h2><p>La connexion va etre reappliquee.</p><p>");
  if(p.mode){page+=F("Nouvelle adresse : <a href='http://");page+=netAddress(p.ip).toString();page+=F("/'>http://");page+=netAddress(p.ip).toString();page+=F("</a>");}
  else {page+=F("L'adresse sera attribuee par le routeur. Acces : <a href='http://");page+=MDNS_HOSTNAME;page+=F(".local/'>");page+=MDNS_HOSTNAME;page+=F(".local</a>");}
  page+=F("</p><p>Acces autonome conserve : <a href='http://192.168.4.1/'>192.168.4.1</a> depuis le Wi-Fi du boitier.</p>");
  server.sendHeader("Connection","close");server.send(200,"text/html; charset=utf-8",page);
}

void netSendSettings() {
  String c=F("<section id='network-status' class='section'><h2>Reseau</h2><div id='networkLive' class='small'>Lecture de la connexion…</div></section>"
    "<form method='POST' action='/saveNetwork'><details id='network-address' class='section'><summary>Adresse IP — DHCP ou fixe</summary>"
    "<label>Reseau memorise</label><select id='netSSID' name='ssid'>");
  for(uint8_t i=0;i<config.knownWiFiCount;++i){c+=F("<option value='");c+=htmlEscape(config.knownWiFi[i].ssid);c+=F("'>");c+=htmlEscape(config.knownWiFi[i].ssid);c+=F("</option>");}
  c+=F("</select><label>Adressage</label><select id='addressMode' name='addressMode'><option value='dhcp'>DHCP — automatique</option><option value='static'>IP fixe</option></select><fieldset id='staticFields' style='border:0;padding:0;margin:0' disabled>");
  const char* names[]={"ip","mask","gateway","dns1","dns2"};
  const char* labels[]={"Adresse IPv4 du boitier","Masque de sous-reseau","Passerelle du routeur","DNS principal (vide = passerelle)","DNS secondaire (facultatif)"};
  for(uint8_t i=0;i<5;++i){c+=F("<label>");c+=labels[i];c+=F("</label><input name='");c+=names[i];c+=F("' id='net-");c+=names[i];c+=F("' inputmode='decimal' maxlength='15'>");}
  c+=F("</fieldset><p class='small'>Un profil IP par reseau. Choisis une adresse libre, de preference reservee dans le routeur. Le Wi-Fi autonome reste disponible.</p><button class='save' type='submit'>ENREGISTRER ET APPLIQUER</button></details></form>"
    "<script>(function(){const ids=['ip','mask','gateway','dns1','dns2'],mode=document.getElementById('addressMode'),ssid=document.getElementById('netSSID');const enabled=()=>document.getElementById('staticFields').disabled=mode.value!=='static';mode.onchange=enabled;async function load(){if(!ssid.value)return;try{const s=await fetch('/api/network/profile?ssid='+encodeURIComponent(ssid.value),{cache:'no-store'}).then(r=>r.json());mode.value=s.mode;ids.forEach(k=>document.getElementById('net-'+k).value=s[k]==='0.0.0.0'?'':s[k]);enabled()}catch(e){}}ssid.onchange=load;load();async function status(){try{const s=await fetch('/api/network/status',{cache:'no-store'}).then(r=>r.json()),e=document.getElementById('networkLive');e.replaceChildren();for(const t of [s.connected?'Connecte a '+s.ssid:'Wi-Fi externe deconnecte','Adressage : '+(s.mode==='static'?'IP fixe':'DHCP'),'IP : '+s.ip+' · Masque : '+s.mask,'Passerelle : '+s.gateway,'DNS : '+s.dns1+' / '+s.dns2,'Signal : '+s.rssi+' dBm · MAC : '+s.mac,'Acces : '+s.hostname,'Wi-Fi autonome : '+s.ap_ip]){const line=document.createElement('div');line.textContent=t;e.append(line)}}catch(e){}}status();setInterval(status,5000)})();</script>");
  sendHtmlChunk(c);
}

void netSetupRoutes() {
  server.on("/saveNetwork",HTTP_POST,netHandleSave);
  server.on("/api/network/profile",HTTP_GET,netProfileJSON);
  server.on("/api/network/status",HTTP_GET,[](){server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",netStatusJSON());});
}
