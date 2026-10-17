const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true}),dir=path.resolve(__dirname,'../preview');
 const context=await browser.newContext({viewport:{width:390,height:844}});let scenario='success',posts=0,boot='old',digest='',expected='',lastSession='',polls=0;
 await context.route('http://onair.test/**',async route=>{
  const u=new URL(route.request().url());
  if(u.pathname==='/api/firmware/status'){
   if(u.searchParams.has('verify_size'))assert.equal(+u.searchParams.get('flash_mode'),firmware[2]);polls++;return route.fulfill({json:{boot,version:'3.4.1 OTA 36LED 100PCT',state:'idle',session:lastSession,verified_md5:u.searchParams.has('verify_size')?digest:''}});
  }
  if(u.pathname==='/update'){
   posts++;expected=u.searchParams.get('md5');lastSession=u.searchParams.get('session');
   assert.equal(+u.searchParams.get('size'),512);assert.equal(expected,crypto.createHash('md5').update(firmware).digest('hex'));
   if(scenario==='reject')return route.fulfill({status:400,json:{ok:false,error:'Empreinte MD5 incorrecte'}});
   if(scenario==='wrong'){boot='new';digest='0'.repeat(32);return route.abort('failed');}
   if(scenario==='unknown')return route.abort('failed');
   boot='new';digest=expected;if(scenario==='lost-ack')return route.abort('failed');
   return route.fulfill({json:{ok:true,md5:expected}});
  }
  const file=u.pathname==='/style.css'?'style.css':'firmware.html';return route.fulfill({path:path.join(dir,file),contentType:file.endsWith('css')?'text/css':'text/html; charset=utf-8'});
 });
 const firmware=Buffer.alloc(512);firmware[0]=0xe9;for(let n=1;n<firmware.length;n++)firmware[n]=n&255;
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 async function prepare(value){scenario=value;boot='old';digest='';lastSession='';await page.goto('http://onair.test/firmware');await page.locator('#firmwareFile').setInputFiles({name:'ON_AIR_ESP8266_OTA.bin',mimeType:'application/octet-stream',buffer:firmware});}
 await prepare('reject');
 for(const bytes of [Buffer.alloc(0),Buffer.from('abc'),crypto.randomBytes(63),crypto.randomBytes(64),crypto.randomBytes(65),crypto.randomBytes(522320)]){
  const actual=await page.evaluate(a=>firmwareMD5(Uint8Array.from(a)),Array.from(bytes));assert.equal(actual,crypto.createHash('md5').update(bytes).digest('hex'));
 }
 await page.click('#uploadBtn');await page.waitForFunction(()=>document.getElementById('uploadState').textContent.includes('refusée'));assert(await page.locator('#uploadBtn').isEnabled());assert(await page.locator('#returnConsole').isHidden());
 await prepare('success');await page.click('#uploadBtn');await page.waitForSelector('#returnConsole:visible');assert((await page.locator('#uploadState').textContent()).includes('installée et vérifiée'));
 await prepare('lost-ack');const before=posts;await page.click('#uploadBtn');await page.waitForSelector('#returnConsole:visible');assert.equal(posts,before+1,'lost ACK must verify without uploading twice');
 await prepare('wrong');await page.click('#uploadBtn');await page.waitForFunction(()=>document.getElementById('uploadState').textContent.includes('n’est pas installé'));assert(await page.locator('#returnConsole').isHidden());assert(await page.locator('#verifyAgain').isVisible());
 await prepare('unknown');await page.clock.install();await page.click('#uploadBtn');await page.waitForFunction(()=>verification!==null);await page.clock.fastForward(80000);await page.waitForFunction(()=>document.getElementById('uploadState').textContent.includes('non confirmée'));assert(await page.locator('#verifyAgain').isVisible());
 const noRetry=posts;boot='new';digest=expected;await page.click('#verifyAgain');await page.clock.runFor(1700);await page.waitForSelector('#returnConsole:visible');assert.equal(posts,noRetry);
 await page.screenshot({path:path.join(dir,'mobile-firmware-verified.png'),fullPage:true});assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(dir,'OTA_UI_VERIFICATION.json'),JSON.stringify({result:'PASS',checks:['MD5 empty/abc/block-boundary/random and complete firmware vectors','size and MD5 in upload','explicit rejection is not success','success only after new boot plus installed flash digest','lost ACK recovered without retransmit','wrong installed firmware refused','unknown outcome stays unconfirmed','manual verify does not re-upload','no script errors']},null,2));await browser.close();console.log('PASS: OTA integrity, reboot verification, lost ACK recovery and no automatic retry');
})().catch(e=>{console.error(e);process.exit(1)});
