#!/usr/bin/env python3
"""Diabet Dünyası Reels: scenes.json -> 1080x1920 MP4.
İstifadə: python3 -I reels.py scenes.json cixis.mp4 FONTS_DIR
FONTS_DIR: `npm pack @fontsource/noto-serif @fontsource/noto-sans` arxivlərinin açıldığı qovluq
(içində */package/files olur).
scenes.json: {"date":"8 NOYABR 2026","rubric":"HƏFTƏNİN YENİLİYİ","source":"...","scenes":[...]}
Səhnə növləri (hər biri ~3.5–5 san):
 {"type":"title","title":"...","accent":"başlıqda qırmızı söz(lər)","sub":"..."}
 {"type":"boxes","label":"...","items":[["96","nəfər"],["24","həftə"]],"text":"..."}   (2–3 qutu)
 {"type":"bars","label":"...","items":[["Qrup A",54,"54%"],["Qrup B",4,"4%"]],"text":"..."} (dəyər 0–100)
 {"type":"notes","label":"DİQQƏT","items":["...","..."],"closing":"Müalicənizi həkiminizlə məsləhətləşmədən dəyişməyin."}
Son səhnə (brend adı + mənbə + handle) avtomatik əlavə olunur.
Könüllü sahələr (başqa səhifələr üçün): "brand" (yuxarı sol və son səhnə başlığı, default «Diabet Dünyası qəzeti»),
 "endTitle" (son səhnənin iri başlığı, default «Diabet Dünyası»), "handle" (default «@diabet_dunyasi_news»).
 Məs.: {"brand":"Dr. Gündüz Əhmədov","endTitle":"Dr. Gündüz Əhmədov","handle":"@dr_endokrinoloq_gunduz_ahmedov"}
       {"brand":"Uşaq Endokrinologiyası Cəmiyyəti","endTitle":"Azərbaycan Uşaq Endokrinologiyası Cəmiyyəti","handle":"@usaqendokrincemiyyet"}
"""
import sys,json,base64,glob,html,os,subprocess,tempfile,shutil
spec=json.load(open(sys.argv[1],encoding='utf8')); out=os.path.abspath(sys.argv[2]); F=sys.argv[3]
E_=html.escape
BRAND=spec.get('brand','Diabet Dünyası qəzeti'); ENDT=spec.get('endTitle','Diabet Dünyası'); HANDLE=spec.get('handle','@diabet_dunyasi_news')
S=glob.glob(F+'/*serif*/package/files')[0]; N=glob.glob(F+'/*sans*/package/files')[0]
def ff(fam,d,base,w):
    o=''
    for sub in('latin','latin-ext'):
        b=base64.b64encode(open(f'{d}/{base}-{sub}-{w}-normal.woff2','rb').read()).decode()
        o+=f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b})}}\n"
    return o
css=ff('NSerif',S,'noto-serif',900)+ff('NSans',N,'noto-sans',400)+ff('NSans',N,'noto-sans',700)
def d(x): return f'style="--d:{x}s"'
parts=[];t=0
for s in spec['scenes']:
    ty=s['type']
    if ty=='title':
        ti=E_(s['title']); ac=s.get('accent')
        if ac and ac in s['title']: ti=ti.replace(E_(ac),f'<em>{E_(ac)}</em>')
        h=f'<div class=pill {d(.2)}>{E_(spec.get("rubric","HƏFTƏNİN YENİLİYİ"))}</div><h1 class=up {d(.5)}>{ti}</h1>'
        if s.get('sub'): h+=f'<p class=up {d(1.3)}>{E_(s["sub"])}</p>'
        dur=4.2
    elif ty=='boxes':
        h=f'<div class=k {d(.1)}>{E_(s["label"])}</div><div class=row>'+''.join(f'<div class="box up{" dim" if i>0 and s.get("dimRest") else ""}" {d(.3+.3*i)}><b>{E_(a)}</b><span>{E_(b)}</span></div>' for i,(a,b) in enumerate(s['items']))+'</div>'
        if s.get('text'): h+=f'<p class=up {d(.4+.3*len(s["items"]))}>{E_(s["text"])}</p>'
        dur=4.2
    elif ty=='bars':
        h=f'<div class=k {d(.1)}>{E_(s["label"])}</div>'
        for i,(lab,v,txt) in enumerate(s['items']):
            g=' g' if i>0 else ''
            h+=f'<div class=bar><span class=lab>{E_(lab)}</span><div class=tr><i class="fill{g}" style="--w:{max(0,min(100,float(v)))}%;--d:{.4+.4*i}s"></i></div><b class="num{g} up" {d(1.4+.2*i)}>{E_(txt)}</b></div>'
        if s.get('text'): h+=f'<p class=up {d(2.2)}>{E_(s["text"])}</p>'
        dur=5
    elif ty=='notes':
        h=f'<div class=k {d(.1)}>{E_(s.get("label","DİQQƏT"))}</div>'+''.join(f'<div class="note up" {d(.3+.7*i)}>{E_(x)}</div>' for i,x in enumerate(s['items']))
        h+=f'<h2 class=up {d(.4+.7*len(s["items"]))}>{E_(s.get("closing","Müalicənizi həkiminizlə məsləhətləşmədən dəyişməyin."))}</h2>'
        dur=4.6
    else: raise SystemExit('naməlum səhnə: '+ty)
    dur=float(s.get('duration',dur)); parts.append((t,t+dur,h)); t+=dur
h=f'<h1 class="up red" style="--d:.2s;font-size:{100 if len(ENDT)<20 else 76}px">{E_(ENDT)}</h1><p class=up {d(.6)}>Mənbə: {E_(spec["source"])}</p><div class="handle up" {d(1)}>{E_(HANDLE)}</div>'
parts.append((t,t+3.4,h)); T=t+3.4
scenes=''.join(f'<section data-s="{a}" data-e="{b}">{x}</section>' for a,b,x in parts)
page=f'''<!doctype html><meta charset=utf8><style>{css}
*{{box-sizing:border-box}}body{{margin:0}}
.v{{width:1080px;height:1920px;background:#FBF8F2;color:#1A1A1A;font-family:NSans;position:relative;overflow:hidden}}
.top{{position:absolute;left:80px;right:80px;top:150px;display:flex;justify-content:space-between;align-items:baseline;border-bottom:4px solid #1A1A1A;padding-bottom:22px}}
.top i{{font:900 48px NSerif;color:#C8102E;font-style:normal}}.top u{{text-decoration:none;font-weight:700;font-size:30px;letter-spacing:.05em}}
section{{position:absolute;left:80px;right:80px;top:330px;bottom:300px;display:flex;flex-direction:column;justify-content:center;gap:44px;opacity:0}}
.pill{{align-self:flex-start;background:#C8102E;color:#fff;font-weight:700;font-size:36px;letter-spacing:.06em;padding:12px 36px;border-radius:999px}}
h1{{margin:0;font:900 100px/1.08 NSerif}}h1 em{{font-style:normal;color:#C8102E}}.red{{color:#C8102E}}
h2{{margin:0;font:900 64px/1.15 NSerif}}
p{{margin:0;font-size:46px;line-height:1.35;color:#2A2A2A}}
.k{{font-weight:700;font-size:40px;letter-spacing:.1em;color:#C8102E}}
.row{{display:flex;flex-direction:column;gap:28px}}
.box{{border:4px solid #1A1A1A;padding:26px 34px;display:flex;align-items:baseline;gap:28px;flex-wrap:wrap}}
.box b{{font:900 120px/1 NSerif;color:#C8102E}}.box span{{font-size:46px}}.box.dim b{{color:#5B524E}}
.bar{{display:grid;grid-template-columns:1fr auto;gap:14px 24px;align-items:center}}
.lab{{grid-column:1/3;font-size:42px;font-weight:700}}
.tr{{height:70px;background:#EDE6DC}}.fill{{display:block;height:100%;width:0;background:#C8102E}}.fill.g{{background:#5B524E}}
.num{{font:900 110px/1 NSerif;color:#C8102E;min-width:250px;text-align:right}}.num.g{{color:#5B524E}}
.note{{border-left:12px solid #C8102E;padding-left:30px;font-size:46px;line-height:1.35}}
.handle{{font-weight:700;font-size:64px}}
.foot{{position:absolute;left:80px;right:80px;bottom:150px;display:flex;justify-content:space-between;font-size:30px;color:#333;border-top:2px solid #1A1A1A;padding-top:18px}}.foot b{{color:#1A1A1A}}
.prog{{position:absolute;left:0;top:0;height:10px;background:#C8102E}}
</style><div class=v><div class=prog></div>
<div class=top><i>{E_(BRAND)}</i><u>{E_(spec["date"])}</u></div>
{scenes}
<div class=foot><span>Məlumat xarakterlidir</span><b>{E_(HANDLE)}</b></div></div>
<script>
const T={T};
function ease(x){{return 1-Math.pow(1-Math.min(Math.max(x,0),1),3)}}
window.T=T;
window.overflow=function(){{return [...document.querySelectorAll('section')].map(s=>{{s.style.opacity=1;const o=s.scrollHeight>s.clientHeight+2;s.style.opacity=0;return o}})}};
window.setT=function(t){{
 document.querySelector('.prog').style.width=(t/T*100)+'%';
 document.querySelectorAll('section').forEach(s=>{{
  const a=+s.dataset.s,e=+s.dataset.e,lt=t-a;
  let o=t<a||t>e?0:Math.min(1,lt/.35,(e-t)/.35); s.style.opacity=Math.max(0,o);
  s.querySelectorAll('[style*="--d"]').forEach(el=>{{
   const d=parseFloat(getComputedStyle(el).getPropertyValue('--d'))||0;
   if(el.classList.contains('fill')){{el.style.width='calc('+getComputedStyle(el).getPropertyValue('--w')+' * '+ease((lt-d)/1.0)+')';}}
   else{{const p=ease((lt-d)/.6);el.style.opacity=p;el.style.transform='translateY('+(40*(1-p))+'px)';}}
  }});
 }});
}};
</script>'''
w=tempfile.mkdtemp(); open(w+'/v.html','w',encoding='utf8').write(page)
js=os.path.join(os.path.dirname(os.path.abspath(__file__)),'rec.js')
subprocess.run(['node',js,w+'/v.html',w],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',w+'/fr/%04d.jpg','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-movflags','+faststart',out],check=True)
# yoxlama üçün kontakt vərəqi: hər səhnənin ortasından bir kadr
ts=[(a+b)/2+0.6 for a,b,_ in parts]
for i,x in enumerate(ts): subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(min(x,T-0.2)),'-i',out,'-frames:v','1','-vf','scale=360:-1',f'{w}/s{i}.jpg'],check=True)
sheet=out.rsplit('.',1)[0]+'-yoxlama.jpg'
subprocess.run(['ffmpeg','-y','-loglevel','error']+sum([['-i',f'{w}/s{i}.jpg'] for i in range(len(ts))],[])+['-filter_complex',f'hstack={len(ts)}',sheet],check=True)
print('OK',out,f'{T:.1f}s','yoxlama:',sheet)
shutil.rmtree(w)
