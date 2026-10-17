const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const assert=require('assert');
const dir=path.resolve(__dirname,'../preview');
const initial=()=>({output_enabled:false,alert_running:false,alert_visible:false,alert_macro:-1,led_hex:'#000000',led_intensity:0,active_macro:-1,active_name:''});
(async()=>{
 const browser=await chromium.launch({channel:process.env.BROWSER_CHANNEL||'chrome',headless:true});
 let state=initial(),offline=false,commands=[],requests=[],failSave=false,saves=[],saveActive=0,maxSaveActive=0,failUpdate=false;
 const context=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
 await context.route('http://onair.test/**',async route=>{
  const u=new URL(route.request().url()),p=u.pathname;requests.push(p);
  if(p==='/update'&&route.request().method()==='POST')return route.fulfill({body:failUpdate?'Update error: invalid firmware':'Update Success! Rebooting...',contentType:'text/html'});
  if(p.startsWith('/api/')){
   if(offline)return route.abort('failed');
   if(p==='/api/macroSave'){
    saveActive++;maxSaveActive=Math.max(maxSaveActive,saveActive);await new Promise(r=>setTimeout(r,120));saveActive--;
    if(failSave)return route.fulfill({status:500,body:'failed'});
    saves.push(Object.fromEntries(u.searchParams));
   }
   if(p==='/api/direct'){commands.push(p);const i=+u.searchParams.get('i');if(!state.alert_running&&(!state.output_enabled||state.active_macro===i)){state.output_enabled=!state.output_enabled;state.active_macro=i;state.active_name=['ONE FM','RADIO LAC','LFM','ROUGE'][i];}}
   if(p==='/api/alert'){commands.push(p);if(!state.output_enabled&&!state.alert_running){state.alert_running=true;state.alert_macro=+u.searchParams.get('i');state.active_macro=state.alert_macro;state.active_name=['ONE FM','RADIO LAC','LFM','ROUGE'][state.active_macro];}}
   if(p==='/api/off'){commands.push(p);state=initial();}
   if(p==='/api/wifiscan/result')return route.fulfill({json:{state:'ready',networks:[{ssid:'Studio 2.4 GHz',saved:false,secure:true,rssi:-50,channel:6}]}});
   return route.fulfill({json:state});
  }
  const file=p==='/style.css'?'style.css':p==='/settings'?'settings.html':p==='/macro'?'macro.html':p==='/firmware'?'firmware.html':p==='/logo'?`logo-${u.searchParams.get('i')}.jpg`:'index.html';
  await route.fulfill({path:path.join(dir,file),contentType:file.endsWith('css')?'text/css':file.endsWith('jpg')?'image/jpeg':'text/html; charset=utf-8'});
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://onair.test/');await page.waitForFunction(()=>document.getElementById('connection').dataset.state==='online');
 assert.equal(await page.locator('.card').count(),4);
 assert(await page.locator('#direct-0').isEnabled());assert(await page.locator('#alert-0').isEnabled());
 await page.waitForTimeout(350);
 await page.screenshot({path:path.join(dir,'mobile-console.png'),fullPage:true,animations:'disabled'});
 for(const width of [320,390,430,768,1440]){await page.setViewportSize({width,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow at ${width}`);}
 await page.setViewportSize({width:390,height:844});
 await page.click('#direct-0');await page.waitForFunction(()=>document.body.dataset.mode==='live');
 assert.equal(await page.locator('#direct-0').getAttribute('aria-pressed'),'true');assert(await page.locator('#direct-1').isDisabled());
 await page.waitForFunction(()=>!commandBusy);await page.waitForTimeout(350);
 assert.equal(await page.locator('#macro-0').getAttribute('data-active'),'true');
 assert.equal(await page.locator('#direct-0').evaluate(n=>getComputedStyle(n).opacity),'1');
 await page.screenshot({path:path.join(dir,'mobile-live.png'),fullPage:true,animations:'disabled'});
 await page.click('#direct-0');await page.waitForFunction(()=>document.body.dataset.mode==='idle');
 await page.click('#alert-1');await page.waitForFunction(()=>document.body.dataset.mode==='alert');assert(await page.locator('#direct-0').isDisabled());
 await page.click('#offBtn');await page.waitForFunction(()=>document.body.dataset.mode==='idle');assert.equal(state.active_macro,-1);
 offline=true;await page.waitForFunction(()=>document.body.dataset.mode==='unknown',{timeout:5000});assert(await page.locator('#direct-0').isDisabled());assert(await page.locator('#offBtn').isEnabled());
 await page.click('#offBtn');await page.waitForFunction(()=>document.getElementById('feedback').textContent.includes('non confirmée'));
 offline=false;await page.waitForFunction(()=>document.body.dataset.mode==='idle',{timeout:6000});
 await page.goto('http://onair.test/settings');assert.equal(await page.locator('#macros a').count(),4);
 await page.click('[data-theme-choice="dark"]');
 assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
 assert.equal(await page.locator('[data-theme-choice="dark"]').getAttribute('aria-pressed'),'true');
 await page.goto('http://onair.test/');assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
 await page.waitForFunction(()=>document.getElementById('connection').dataset.state==='online');await page.waitForTimeout(350);
 await page.screenshot({path:path.join(dir,'mobile-dark.png'),fullPage:true,animations:'disabled'});
 await page.goto('http://onair.test/settings');await page.reload();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
 await page.click('[data-theme-choice="light"]');assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
 assert.equal(await page.locator('#general').getAttribute('open'),null);
 await page.click('a[href="#network"]');assert(await page.locator('#network').evaluate(n=>n.open));
 await page.click('#scanWifiBtn');await page.waitForSelector('#wifiScanResults button');await page.click('#wifiScanResults button');assert.equal(await page.inputValue('#externalSSID'),'Studio 2.4 GHz');
 await page.goto('http://onair.test/settings#system');assert(await page.locator('#system').evaluate(n=>n.open));assert(await page.locator('a[href="/firmware"]').isVisible());
 await page.goto('http://onair.test/settings');await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(dir,'mobile-settings.png'),fullPage:true});
 await page.goto('http://onair.test/settings');assert(await page.locator('nav a[href="#animations"]').isVisible());await page.locator('nav a[href="#animations"]').click();assert.equal(await page.locator('#animations').getAttribute('href'),'/animation');assert.equal(await page.locator('#animations.save').count(),0);assert.equal(await page.locator('#animations').evaluate(e=>getComputedStyle(e).alignItems),'center');await page.locator('#animations').screenshot({path:path.join(dir,'editor-entry-dark.png')});await page.goto('http://onair.test/macro?i=0');assert.equal(await page.locator('#alertAnimation option').count(),16);assert.equal(await page.locator('#directMotion option').count(),12);assert.equal(await page.locator('#directIntensity').getAttribute('max'),'100');
 assert(await page.locator('.editor-link a').first().isVisible());assert.equal(await page.locator('.editor-link a').count(),2);await page.selectOption('#alertAnimation','32');await page.waitForFunction(()=>!savePromise);assert.equal(saves.at(-1).alertAnimation,'32');await page.selectOption('#directMotion','1');await page.selectOption('#motionCycle','6000');await page.waitForFunction(()=>!savePromise);assert.equal(saves.at(-1).directMotion,'1');assert.equal(saves.at(-1).motionCycle,'6000');
 await page.fill('#macroName','DAMIEN LIVE');await page.waitForTimeout(1000);assert(requests.includes('/api/macroSave'));
 await page.evaluate(()=>{document.getElementById('macroName').value='FIRST';saveNow();document.getElementById('macroName').value='LATEST';saveNow();});
 await page.waitForFunction(()=>!savePromise);assert.equal(saves.at(-1).name,'LATEST');assert.equal(maxSaveActive,1);
 failSave=true;const oldTests=requests.filter(p=>p==='/api/alertTest').length;
 await page.evaluate(()=>testAlert());assert.equal(requests.filter(p=>p==='/api/alertTest').length,oldTests);assert((await page.locator('#autosave').textContent()).includes('Non enregistré'));
 failSave=false;await page.evaluate(()=>saveNow());assert((await page.locator('#autosave').textContent()).includes('enregistrés'));
 await page.screenshot({path:path.join(dir,'mobile-macro.png'),fullPage:true});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'macro overflow');
 await page.goto('http://onair.test/firmware');
 assert(await page.locator('#returnConsole').isHidden());
 assert(await page.locator('#firmwareFile').isVisible());assert(await page.locator('#uploadBtn').isEnabled());
 await page.screenshot({path:path.join(dir,'mobile-firmware.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 const report={result:'PASS',viewportWidths:[320,390,430,768,1440],commands,checks:['4 emissions','confirmed live state and locks','direct toggle','alert and blackout','disconnect and recovery','light/dark persistence across pages and reload','10 built-in direct animations plus shared named library','14 built-in alert animations plus shared named library','network discovery and selection','settings anchors','OTA form (transfer recovery verified by check-ota-ui)','100% intensity','autosave serializes rapid changes','failed save blocks alert test','save retry','no horizontal overflow','no browser script errors']};
 fs.writeFileSync(path.join(dir,'ui-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
