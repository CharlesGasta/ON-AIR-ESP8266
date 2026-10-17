const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const context=await browser.newContext({viewport:{width:390,height:844}}),dir=path.resolve(__dirname,'../preview');
 const library=new Map();let physical=[],failSave=false,busy=false,previewOwner=null,previewDelay=0,failPreview=0,activePreviewRequests=0,maxPreviewRequests=0;
 await context.route('http://onair.test/**',async route=>{
  const u=new URL(route.request().url()),body=new URLSearchParams(route.request().postData()||'');
  if(u.pathname==='/api/library')return route.fulfill({json:Array.from(library,([id,item])=>({id,name:item.name}))});
  if(u.pathname==='/api/library/get'){const item=library.get(+u.searchParams.get('id'));return route.fulfill(item?{body:item.bytes,contentType:'application/octet-stream'}:{status:404,body:'Animation introuvable'});}
  if(u.pathname==='/api/library/save'){
   if(failSave)return route.fulfill({status:500,body:'Enregistrement impossible'});
   const name=body.get('name'),editing=body.has('id')?+body.get('id'):null;
   if(!name.trim())return route.fulfill({status:400,body:'Veuillez renseigner un nom pour l’animation.'});
   if(Array.from(library).some(([id,item])=>id!==editing&&item.name.toLowerCase()===name.toLowerCase()))return route.fulfill({status:409,body:'Ce nom est déjà utilisé.'});
   let id=editing??32;while(editing===null&&library.has(id))id++;
   library.set(id,{name,bytes:Buffer.from(body.get('data'),'hex')});return route.fulfill({json:{id}});
  }
  if(u.pathname==='/api/library/delete'){library.delete(+body.get('id'));return route.fulfill({body:'OK'});}
  if(u.pathname==='/api/library/preview'){
   if(busy)return route.fulfill({status:409,body:'Arrêtez le direct avant d’activer l’aperçu.'});
   activePreviewRequests++;maxPreviewRequests=Math.max(maxPreviewRequests,activePreviewRequests);
   if(previewDelay)await new Promise(r=>setTimeout(r,previewDelay));
   activePreviewRequests--;if(failPreview){failPreview--;return route.abort('failed');}
   previewOwner=body.get('token');physical.push({data:body.get('data'),cue:+body.get('cue'),play:body.get('play')});return route.fulfill({body:'OK'});
  }
  if(u.pathname==='/api/library/preview/ping')return route.fulfill(previewOwner===body.get('token')?{body:'OK'}:{status:409,body:'Aperçu interrompu'});
  if(u.pathname==='/api/library/preview/stop'){previewOwner=null;return route.fulfill({body:'OK'});}
  const file=u.pathname==='/style.css'?'style.css':'animation.html';return route.fulfill({path:path.join(dir,file),contentType:file.endsWith('css')?'text/css':'text/html; charset=utf-8'});
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());await page.goto('http://onair.test/animation');
 assert.equal(await page.locator('.led').count(),36);assert(!await page.locator('#physicalPreview').isChecked());assert.equal(await page.locator('#test,#off').count(),0);
 await page.click('#save');assert((await page.locator('#status').textContent()).includes('Veuillez renseigner'));assert.equal(library.size,0);
 await page.fill('#animationName','Aurore');await page.getByRole('button',{name:'Haut',exact:true}).click();await page.getByRole('button',{name:'Rouge',exact:true}).click();
 await page.click('#duplicate');await page.getByRole('button',{name:'Tout',exact:true}).click();await page.getByRole('button',{name:'Cyan',exact:true}).click();await page.selectOption('#transition','fade');await page.fill('#fade','2');await page.locator('#fade').dispatchEvent('change');await page.waitForTimeout(250);assert.equal(physical.length,0);
 await page.check('#physicalPreview');await page.waitForFunction(()=>document.getElementById('physicalPreview').checked);await page.waitForTimeout(300);assert(physical.length>0);const before=physical.length;for(let n=0;n<6;n++){await page.locator('#color').evaluate((e,n)=>{e.value=n%2?'#f10000':'#e00000';e.dispatchEvent(new Event('input'));},n);await page.waitForTimeout(35);}assert(physical.length>before,'continuous colour edits must stream before input stops');
 await page.getByRole('button',{name:'Blanc',exact:true}).click();await page.waitForTimeout(250);assert(physical.length>before);assert.equal(library.size,0,'preview must not save');
 await page.click('#play');await page.waitForTimeout(250);assert.equal(physical.at(-1).play,'1');await page.click('#play');await page.waitForTimeout(250);assert.equal(physical.at(-1).play,'0');
 await page.uncheck('#physicalPreview');await page.waitForTimeout(150);const stopped=physical.length;assert.equal(previewOwner,null);await page.getByRole('button',{name:'Cyan',exact:true}).click();await page.waitForTimeout(250);assert.equal(physical.length,stopped);
 await page.click('#save');await page.waitForFunction(()=>!dirty&&!saving);assert.equal(library.size,1);assert.equal(library.get(32).name,'Aurore');assert.equal(library.get(32).bytes[5],2);assert.equal(library.get(32).bytes.readUInt16LE(122),2000);assert.equal(await page.locator('.library-select[aria-pressed=true]').count(),1);
 await page.reload();await page.getByRole('button',{name:'Aurore',exact:true}).click();assert.equal(await page.inputValue('#animationName'),'Aurore');assert.equal(await page.locator('#cues button').count(),2);
 await page.click('#save');await page.waitForFunction(()=>!dirty&&!saving);assert.equal(library.size,1,'editing existing item does not duplicate');
 await page.click('#newAnimation');await page.fill('#animationName','aurore');await page.click('#save');assert((await page.locator('#status').textContent()).includes('déjà utilisé'));assert.equal(library.size,1);
 await page.fill('#animationName','Pulse');await page.getByRole('button',{name:'Violet',exact:true}).click();await page.click('#save');await page.waitForFunction(()=>!dirty&&!saving);assert.equal(library.size,2);
 failSave=true;await page.fill('#animationName','Pulse 2');await page.click('#save');await page.waitForFunction(()=>document.getElementById('status').textContent.includes('impossible'));assert.equal(library.get(33).name,'Pulse');failSave=false;
 previewDelay=1800;await page.check('#physicalPreview');await page.waitForTimeout(1200);assert(await page.locator('#physicalPreview').isChecked(),'slow activation must not be cancelled by an early heartbeat');
 for(let n=0;n<20;n++)await page.locator('#color').evaluate((e,n)=>{e.value=n%2?'#ee0000':'#001122';e.dispatchEvent(new Event('input'));},n);
 await page.waitForTimeout(3200);assert(await page.locator('#physicalPreview').isChecked());assert.equal(maxPreviewRequests,1,'preview requests must not overlap');assert.equal(physical.at(-1).data,await page.evaluate(()=>hexData()),'latest edit must reach device');previewDelay=0;
 failPreview=1;await page.getByRole('button',{name:'Blanc',exact:true}).click();await page.waitForTimeout(1200);assert(await page.locator('#physicalPreview').isChecked(),'single network failure must recover without clearing switch');
 await page.uncheck('#physicalPreview');await page.waitForTimeout(200);
 busy=true;await page.check('#physicalPreview');await page.waitForFunction(()=>!document.getElementById('physicalPreview').checked);assert((await page.locator('#status').textContent()).includes('Arrêtez'));busy=false;
 await page.getByRole('button',{name:'Aurore',exact:true}).click();assert.equal(await page.inputValue('#animationName'),'Aurore');
 const valid=Buffer.from(await page.evaluate(()=>Array.from(encode()))),bad=Buffer.from(valid);bad[12]^=1;
 await page.locator('#file').setInputFiles({name:'bad.onair',mimeType:'application/octet-stream',buffer:bad});await page.waitForFunction(()=>document.getElementById('status').textContent.includes('endommagé'));assert.equal(await page.locator('#cues button').count(),2);
 await page.locator('#file').setInputFiles({name:'good.onair',mimeType:'application/octet-stream',buffer:valid});await page.click('#save');await page.waitForFunction(()=>!dirty&&!saving);
 await page.getByRole('button',{name:'Supprimer Pulse',exact:true}).click();await page.waitForFunction(()=>document.querySelectorAll('.library-row').length===1);assert.equal(library.size,1);
 // Real pointer centers, including mobile spacing: deselection and reselection must hit the same LED.
 assert.equal(await page.locator('#palette button').count(),13);
 for(const width of [320,390,680]){
  await page.setViewportSize({width,height:900});await page.locator('#board').scrollIntoViewIfNeeded();
  for(let n=0;n<36;n++){const led=page.locator('.led').nth(n),before=await led.getAttribute('aria-pressed'),box=await led.boundingBox();await page.mouse.click(box.x+box.width/2,box.y+box.height/2);assert.notEqual(await led.getAttribute('aria-pressed'),before,'LED center '+n+' at '+width);await page.mouse.click(box.x+box.width/2,box.y+box.height/2);assert.equal(await led.getAttribute('aria-pressed'),before);}
 }
 await page.locator('#animationIntensity').evaluate(e=>{e.value='37';e.dispatchEvent(new Event('input'));});
 assert.equal(await page.evaluate(()=>decode(encode()).intensity),37,'intensity persists in exported binary');
 await page.selectOption('#cueKind','chase');await page.fill('#chaseStart','36');await page.fill('#chaseEnd','1');await page.fill('#effectSpeed','50');await page.locator('#effectSpeed').dispatchEvent('change');
 assert(await page.evaluate(()=>{const c=decode(encode())[current],a=cuePixels(c,0),b=cuePixels(c,1750);return c.start===35&&c.end===0&&c.speed===50&&a.slice(105).some(Boolean)&&b.slice(0,3).some(Boolean)&&b.slice(3).every(v=>v===0);}), 'reverse chenillard reaches requested endpoints');
 await page.getByRole('button',{name:'Aucune',exact:true}).click();await page.locator('.led').nth(0).click();await page.locator('.led').nth(35).click();await page.selectOption('#cueKind','strobe');await page.fill('#effectSpeed','20');await page.locator('#effectSpeed').dispatchEvent('change');
 assert(await page.evaluate(()=>{const c=decode(encode())[current];return c.kind==='strobe'&&c.speed===20&&c.mask.join(',')==='0,35'&&cuePixels(c,0).some(Boolean)&&cuePixels(c,20).every(v=>v===0);}), 'strobe mask and 20 ms interval roundtrip');
 await page.click('#bankOpen');await page.locator('#bankSaved .bank-row').filter({hasText:'Aurore'}).getByRole('button',{name:'Copier',exact:true}).click();assert.equal(await page.evaluate(()=>editingId),null);assert.equal(await page.inputValue('#animationName'),'Aurore copie');assert.equal(await page.locator('#cues button').count(),2);
 await page.click('#save');await page.waitForFunction(()=>!saving&&!dirty);assert.equal(library.size,2,'copy saves separately');
 await page.click('#bankOpen');await page.locator('#templateList .bank-row').first().getByRole('button',{name:'Utiliser'}).click();assert.equal(await page.locator('#cues button').count(),3);assert.equal(await page.evaluate(()=>editingId),null);assert.equal(await page.evaluate(()=>cuePixels(cues[1],0)[2]),255);
 await page.evaluate(()=>{cues=[solidCue([0,0,0])];cues[0].rgb.splice(16*3,3,255,0,0);draw();});
 assert(await page.evaluate(()=>{const ctx=document.getElementById('diffuser').getContext('2d');return ctx.getImageData(100,130,1,1).data[0]>ctx.getImageData(880,80,1,1).data[0]+40;}),'upper-left LED illuminates left letters more strongly');
 await page.evaluate(()=>{cues=templates[0][1]();current=0;refresh();});
 for(const width of [320,390,430,768]){await page.setViewportSize({width,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'overflow '+width);}
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>{localStorage.setItem('onair-theme','dark');document.documentElement.dataset.theme='dark';});await page.waitForTimeout(350);await page.screenshot({path:path.join(dir,'mobile-animation-editor.png'),fullPage:true});
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(dir,'EDITOR_VERIFICATION.json'),JSON.stringify({result:'PASS',checks:['single shared editor','mandatory unique names','create/load/update/delete named sequences','unsaved physical preview only when enabled','live cue/colour/playback changes','preview OFF stops and blocks further requests','broadcast refusal visible and toggle cleared','slow activation does not race heartbeat','coalesced serial requests deliver latest edit','transient failure keeps preview enabled','36 LED centers select and deselect at mobile and desktop widths','sequence intensity roundtrip','reverse chenillard endpoints','strobe 20 ms and selected mask roundtrip','bank recalls templates and copies saved animation separately','local LED diffusion in large ON AIR letters','preview never saves','cue timings and binary roundtrip','invalid import preserves data','failed save preserves library','mobile widths 320–768','no browser script errors']},null,2));await browser.close();console.log('PASS: named library, live preview switch, validation, editing, deletion, persistence and mobile UI');
})().catch(e=>{console.error(e);process.exit(1)});
