// Editable templates: copied into the library only when the user saves them.
function brandCue(colors,phase,hold=1400,fade=650,level=1){
 return {hold,fade,rgb:Array.from({length:36},(_,n)=>colors[(Math.floor(n/6)+phase)%colors.length].map(v=>Math.round(v*level))).flat()};
}
const caracColors=[[30,57,210],[0,180,111],[255,89,38]];
const regieColors=[[24,116,177],[255,126,34]];
templates.push(
 ['CARAC · signature tricolore',()=>[0,1,2].map(p=>brandCue(caracColors,p,1600,800,.8))],
 ['CARAC · respiration douce',()=>[brandCue(caracColors,0,600,1600,.65),brandCue(caracColors,0,600,1600,.08)]],
 ['CARAC · comete tricolore',()=>caracColors.map(color=>({...solidCue([0,0,0],3960),kind:'chase',start:0,end:35,speed:110,color}))],
 ['CARAC · ouverture coloree',()=>[0,1,2,3].map(p=>({hold:600,fade:500,rgb:Array.from({length:36},(_,n)=>{const x=n<12?(11-n)/11:n<17?0:n<31?(n-17)/13:1;return caracColors[Math.min(2,Math.floor(x*3))].map(v=>Math.round(v*(Math.abs(x-.5)<(p+1)/8?.8:.025)));}).flat()}))],
 ['TriCaster · bleu et orange',()=>[brandCue(regieColors,0,1800,900,.7),brandCue(regieColors,1,1800,900,.7)]],
 ['REC · pulsation sobre',()=>[solidCue([180,0,0],700,1300),solidCue([16,0,0],700,1300)]],
 ['STREAM · vague bleu orange',()=>[0,1,2,3].map(p=>brandCue(regieColors,p,1200,900,.25+p*.16))],
 ['REC + STREAM · double signature',()=>[0,1,2].map(p=>brandCue([[210,0,0],regieColors[0],regieColors[1]],p,1400,700,.75))],
 ['Veille · lueur bleue',()=>[solidCue([0,3,12],1000,2200),solidCue([0,1,3],1000,2200)]]
);
