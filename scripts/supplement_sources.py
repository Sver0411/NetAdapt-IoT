import concurrent.futures
import io
import json
from pathlib import Path
import requests
from pypdf import PdfReader

P=Path.home()/'.cache/netadapt-iot/literature'
DOIS={'P01':'10.3390/fi15070246','P04':'10.1007/s11042-023-14781-8','P05':'10.1109/ACCESS.2022.3192539','P06':'10.1016/j.comcom.2024.107924','P10':'10.1109/VTC2023-Spring57618.2023.10199705','R01':'10.1109/INFCOM.2012.6195689','R02':'10.1109/JSAC.2021.3065072','R03':'10.1109/TNET.2018.2873606','R04':'10.1109/INFOCOM.2018.8486307','R07':'10.1109/9.182479','R09':'10.1057/palgrave.jors.2600523','R11':'10.1145/2208917.2209336','R12':'10.1109/JIOT.2024.3496113'}
URLS={
'P04':'https://pmc.ncbi.nlm.nih.gov/articles/PMC9983533/',
'P06_preprint':'https://papers.ssrn.com/sol3/Delivery.cfm/4678905.pdf?abstractid=4678905',
'R01':'https://www.winlab.rutgers.edu/~ryates/Papers/KaulYatesGruteser12infocom.pdf',
'R02':'https://arxiv.org/pdf/2007.08564',
'R04':'https://www.mit.edu/~modiano/papers/C_C_134.pdf',
'R09':'https://www.statslab.cam.ac.uk/~frank/rate.pdf',
'R11':'https://queue.acm.org/detail.cfm?id=2209336',
'R13':'https://arxiv.org/html/2503.23658v1',
'R14':'https://arxiv.org/html/2605.13012v1',
}
def getdoi(kv):
 k,d=kv
 try:
  r=requests.get('https://api.crossref.org/works/'+d,timeout=35);r.raise_for_status()
  m=r.json()['message'];(P/f'{k}_verified.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
  return k,m.get('title'),m.get('author'),m.get('published')
 except Exception as e:return k,str(e)
def geturl(kv):
 k,u=kv
 try:
  r=requests.get(u,timeout=45);r.raise_for_status()
  if r.content.startswith(b'%PDF'):
   (P/f'{k}.pdf').write_bytes(r.content)
   t='\n\n'.join(f'--- PAGE {i+1} ---\n'+p.extract_text() for i,p in enumerate(PdfReader(io.BytesIO(r.content)).pages))
   (P/f'{k}.txt').write_text(t);return k,'PDF',len(t)
  (P/f'{k}.html').write_text(r.text);return k,'HTML',len(r.text),r.text[:70]
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(getdoi,DOIS.items()):print(r)
 for r in pool.map(geturl,URLS.items()):print(r)
