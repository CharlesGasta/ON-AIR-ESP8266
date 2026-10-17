// Render the actual streamed firmware page generators with small host-side stubs.
// No independent copy of the HTML/CSS/JS: preview stays tied to the firmware source.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'ON_AIR_ESP8266.ino'),'utf8');
const out=path.join(root,'preview');fs.mkdirSync(out,{recursive:true});
const assets={};
for(const m of source.matchAll(/static const char (\w+)\[\] PROGMEM = R"(\w+)\(([\s\S]*?)\)\2";/g))assets[m[1]]=m[3];
function extract(name){const start=source.indexOf('void '+name+'(');let brace=source.indexOf('{',start),level=1,i=brace+1,inString=false,escape=false;
 for(;i<source.length&&level;i++){const c=source[i];if(inString){if(escape)escape=false;else if(c==='\\')escape=true;else if(c==='"')inString=false;}else if(c==='"')inString=true;else if(c==='{')level++;else if(c==='}')level--;}
 return source.slice(brace+1,i-1);
}
function transpile(name){let literals=[],body=extract(name).replace(/"(?:\\.|[^"\\])*"|\/\/[^\n]*|\/\*[\s\S]*?\*\//g,m=>{if(m.startsWith('/'))return '';const n=literals.push(m)-1;return `__L${n}__`;});
 body=body.replace(/(__L\d+__)\s+(?=__L\d+__)/g,'$1 + ')
 .replace(/\bString (\w+);/g,"let $1='';")
 .replace(/\bString (\w+)\s*=/g,'let $1 =')
 .replace(/\bMacroConfig& (\w+) =/g,'let $1 =')
 .replace(/\buint8_t (\w+)\s*=/g,'let $1 =')
 .replace(/const uint16_t cycles\[\]=\{([^}]+)\};/g,'const cycles=[$1];')
 .replace(/\b\w+\.reserve\([^;]*;/g,'')
 .replace(/Serial\.println\([\s\S]*?\);/g,'')
 .replace(/\byield\(\)/g,'tick()');
 body=body.replace(/__L(\d+)__/g,(_,n)=>literals[+n]);
 return `function ${name}(i){${body}}`;
}
let html='';
const names=['ONE FM','RADIO LAC','LFM','ROUGE'];
const colors=[[239,75,70],[80,172,223],[153,115,213],[214,51,63]];
const macros=names.map((name,i)=>({name,r:colors[i][0],g:colors[i][1],b:colors[i][2],intensity:100,idleR:0,idleG:0,idleB:15,idleIntensity:10,idleOff:true,alertDuration:5,blinkMs:500,alertAnimation:i,logoPath:'builtin:'+i}));
const ctx={F:x=>x,PSTR:x=>x,webMemoryReady:()=>true,sendHtmlFlash:s=>html+=s,...assets,config:{deviceName:'ON AIR-MOC',apSSID:'ON_AIR-MOC',externalWiFiEnabled:false,startupAnimation:true,knownWiFiCount:1,knownWiFi:[{ssid:'Studio broadcast'}],macro:macros},motionSettings:{mode:[0,0,0,0],cycleMs:[4000,4000,4000,4000]},libraryOptions:selected=>[32,33].map((id,n)=>`<option value='${id}'${selected===id?" selected":""}>${["Aurore","Pulse"][n]}</option>`).join(""),MACRO_COUNT:4,FIRMWARE_VERSION:'3.4.2 MEMORY 36LED 100PCT',CONTENT_LENGTH_UNKNOWN:-1,WL_CONNECTED:3,WiFi:{status:()=>0},ESP:{getFreeHeap:()=>28000,getMaxFreeBlockSize:()=>24000},String,htmlEscape:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll("'",'&#39;').replaceAll('"','&quot;'),rgbToHex:(r,g,b)=>'#'+[r,g,b].map(x=>x.toString(16).padStart(2,'0')).join(''),logoAvailable:()=>true,isBuiltinLogo:()=>true,strlen:s=>s.length,tick:()=>{},beginChunkedHtml:()=>{},endChunkedHtml:()=>{},sendHtmlChunk:s=>html+=s,server:{setContentLength:()=>{},sendHeader:()=>{},send:()=>{},sendContent:s=>html+=s,sendContent_P:s=>html+=s},ALERT_CUSTOM:14,ALERT_SWEEP_TB:12,ALERT_SWEEP_BT:13,ALERT_CLASSIC:0,ALERT_FADE_TO_BLACK:1,ALERT_TRAFFIC_GRADIENT:2,ALERT_ACCELERATING:3,ALERT_DOUBLE_FLASH:4,ALERT_LOGO_CHASE:5,ALERT_LOGO_DRAW:6};
vm.createContext(ctx);
for(const [name,file] of [['sendControlPage','index.html'],['sendSettingsPage','settings.html'],['sendMacroSettingsPage','macro.html']]){html='';vm.runInContext(transpile(name),ctx);vm.runInContext(name+'(0)',ctx);fs.writeFileSync(path.join(out,file),html);}
fs.writeFileSync(path.join(out,'style.css'),assets.COMMON_CSS);
fs.writeFileSync(path.join(out,'firmware.html'),assets.FIRMWARE_PAGE);
fs.writeFileSync(path.join(out,'animation.html'),assets.ANIMATION_EDITOR_HTML);
for(const [i,name] of ['ONE_FM','RADIO_LAC','LFM','ROUGE'].entries()){
 const m=source.match(new RegExp(`const uint8_t LOGO_${name}\\[\\] PROGMEM = \\{([\\s\\S]*?)\\};`));
 const bytes=Array.from(m[1].matchAll(/0x([\da-f]{2})/gi),m=>parseInt(m[1],16));fs.writeFileSync(path.join(out,`logo-${i}.jpg`),Buffer.from(bytes));
}
fs.writeFileSync(path.join(out,'generators.json'),JSON.stringify({htmlFiles:['index.html','settings.html','macro.html'],cssBytes:Buffer.byteLength(assets.COMMON_CSS),jsBytes:Buffer.byteLength(assets.CONTROL_PAGE_JS)},null,2));
console.log('Rendered actual page generators to '+out);
