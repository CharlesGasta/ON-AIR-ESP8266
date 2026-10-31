const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/ONE_AIR_CARAC_V2.ino','utf8');
const script=source.match(/CONTROL_PAGE_JS\[\][\s\S]*?R"JS\(([\s\S]*?)\)JS";/)[1].replace(/<\/?script>/g,'');
const nodes={};
for(const id of ['connection','status','alertbar','feedback','offBtn','carac-release','direct-0','alert-0','direct-label-0','alert-label-0',...Array.from({length:4},(_,i)=>'macro-'+i),...Array.from({length:3},(_,i)=>'auto-state-'+(i+1))]){
 nodes[id]={dataset:{color:'#ff0000'},style:{},classList:{toggle(){}},setAttribute(){},textContent:'',hidden:false};
}
const context=vm.createContext({
 document:{body:{dataset:{}},hidden:false,getElementById:id=>nodes[id]||null,addEventListener(){}},
 window:{addEventListener(){}},setTimeout(){return 1;},clearTimeout(){},AbortController,
 fetch(){throw Error('Unexpected request');},console,
});
// Includes the real first render before any status has arrived.
vm.runInContext(script,context);
function render(extra={}){
 context.fixture={output_enabled:false,alert_running:false,alert_visible:false,alert_macro:-1,active_macro:-1,active_name:'',tc_mode:true,tc_ready:true,tc_rec:false,tc_stream:false,tc_paused:false,manual_priority:false,...extra};
 vm.runInContext('lastState=fixture;connected=true;commandBusy=false;renderStatus()',context);
}
render({output_enabled:true,active_macro:2,tc_stream:true});
assert.equal(nodes['auto-state-2'].textContent,'STREAM ON');
assert.equal(nodes['direct-0'].disabled,false);assert.equal(nodes['alert-0'].disabled,false);
assert.equal(nodes['carac-release'].hidden,true);
render({output_enabled:true,active_macro:0,manual_priority:true,tc_rec:true,tc_stream:true});
assert.equal(nodes['auto-state-3'].textContent,'REC + STREAM ON · priorite CARAC');
assert.equal(nodes['carac-release'].hidden,false);
render({tc_mode:false});assert.equal(nodes['auto-state-1'].textContent,'Suivi desactive');
render({tc_paused:true});assert.equal(nodes['auto-state-1'].textContent,'Suivi suspendu');
render({tc_ready:false});assert.equal(nodes['auto-state-1'].textContent,'Connexion TriCaster en attente');
vm.runInContext('connected=false;renderStatus()',context);
assert.equal(nodes['direct-0'].disabled,true);
assert.equal(nodes['auto-state-1'].textContent,'Connexion au boitier perdue');
console.log('PASS: actual console JS handles first render, missing automatic buttons, CARAC priority, release, pause and disconnection');
