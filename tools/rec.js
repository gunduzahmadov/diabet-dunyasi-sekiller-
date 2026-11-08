// Kadrları çəkir; daşan səhnə varsa xəta verir.
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [,,page,dir]=process.argv;const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+page);await p.evaluate(()=>document.fonts.ready);
const ov=await p.evaluate(()=>overflow());if(ov.some(x=>x)){console.error('DAŞMA: səhnələr',ov.map((x,i)=>x?i+1:null).filter(Boolean).join(','),'— mətni qısalt');await b.close();process.exit(2)}
const T=await p.evaluate(()=>window.T);fs.mkdirSync(dir+'/fr',{recursive:true});const fps=30;
for(let i=0;i<Math.round(fps*T);i++){await p.evaluate(t=>setT(t),i/fps);await p.screenshot({path:`${dir}/fr/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close()})()
