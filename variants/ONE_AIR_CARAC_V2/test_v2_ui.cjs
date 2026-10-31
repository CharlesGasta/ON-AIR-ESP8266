const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/ONE_AIR_CARAC_V2.ino','utf8');
assert(!source.includes('CARAC garde la priorite'));
assert(source.includes('One air Carac v2'));
const solid=source.match(/function solidCue[^\n]+/)[0];
const start=source.indexOf('const templates=['),end=source.indexOf('function replaceTimeline',start);
const bank=vm.runInNewContext(solid+'\n'+source.slice(start,end)+'\ntemplates');
assert(bank.length>=14);
for(const [name,make] of bank){
 const cues=make();assert(cues.length>=1&&cues.length<=12,name);
 for(const cue of cues){
  assert(cue.rgb.length===108,name);assert(cue.rgb.every(v=>Number.isInteger(v)&&v>=0&&v<=255),name);
  assert(cue.hold>=100&&cue.hold<=60000,name);assert(cue.fade>=0&&cue.fade<=20000,name);
  if(cue.kind==='chase'){assert(cue.start>=0&&cue.end<=35&&cue.speed>=20,name);}
 }
}
for(const name of ['CARAC · signature tricolore','TriCaster · bleu et orange','REC + STREAM · double signature'])assert(bank.some(x=>x[0]===name));
function luminance(hex){return hex.match(/\w\w/g).map(x=>parseInt(x,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);}
function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
for(const [fg,bg] of [['26354f','edf1f7'],['eef3fc','2b3345'],['ffffff','245cc5']]){
 assert(contrast(fg,bg)>=4.5,fg+' / '+bg);
 assert(source.includes('#'+fg)&&source.includes('#'+bg));
}
assert(source.includes("name='addressMode'"));
for(const key of ['ip','mask','gateway','dns1','dns2'])assert(source.includes('"'+key+'"'));
assert(source.includes("name='tcOffProfile'"));
const macroPage=source.slice(source.indexOf('void sendMacroSettingsPage('),source.indexOf('String statusJSON()'));
const hide=macroPage.indexOf('if(i>0)sendHtmlFlash(PSTR("<div hidden>"))');
assert(hide>macroPage.indexOf('Etat OFF'));
assert(hide<macroPage.indexOf('<h3>Alerte'));
console.log('PASS: 14 animation templates valid; light/dark/active button contrast >= 4.5; DHCP/static UI and connected OFF controls exposed');
