"""Retrieve bibliographic records and accessible article texts."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT = Path.home() / '.cache/netadapt-iot/literature'
TITLES = [
('P01', 'An Accurate Platform for Investigating TCP Performance in Wi-Fi Networks'),
('P02', 'Fine-grained QoS provisioning with micropayments in wireless networks'),
('P03', 'QoE provisioning system for VoIP and video streaming using software-defined networking and IOTA micropayment'),
('P04', 'An implementation and evaluation of MPTCP-based IoT router'),
('P05', 'Implementation of P4-Based Schedulers for Multipath Communication'),
('P06', 'FQ-SAT: A fuzzy Q-learning-based MPQUIC scheduler for data transmission optimization'),
('P07', 'MuLeS: A Multi-Client Learning-Based MPQUIC Scheduler'),
('P08', 'LoGra: An LSTM-DDPG Integrated MPQUIC Scheduler for Mobile Video Streaming'),
('P09', 'Evaluating MPQUIC schedulers in dynamic wireless networks with 2D and 3D mobility'),
('P10', 'Overlapping Channel Bonding Allocation for Dense WLANs under Imbalanced Traffic Demands'),
('R01', 'Real-time status: How often should one update?'),
('R02', 'Age of Information: An Introduction and Survey'),
('R03', 'Scheduling Policies for Minimizing Age of Information in Broadcast Wireless Networks'),
('R04', 'Optimizing Age of Information in Wireless Networks With Throughput Constraints'),
('R05', 'Scheduling Policies for Age Minimization in Wireless Networks With Unknown Channel State'),
('R06', 'A Theory of QoS for Wireless'),
('R07', 'Stability properties of constrained queueing systems and scheduling policies for maximum throughput in multihop radio networks'),
('R08', 'Efficient fair queueing using deficit round-robin'),
('R09', 'Rate control for communication networks: shadow prices, proportional fairness and stability'),
('R10', 'A generalized processor sharing approach to flow control in integrated services networks: the single-node case'),
('R11', 'Controlling Queue Delay'),
('R12', 'Scheduling With Soft Age-of-Information Deadlines'),
]
PDFS = {
'P01':'https://mdpi-res.com/d_attachment/futureinternet/futureinternet-15-00246/article_deploy/futureinternet-15-00246.pdf',
'P02':'https://www.jstage.jst.go.jp/article/nolta/14/1/14_50/_pdf',
'P03':'https://www.jstage.jst.go.jp/article/comex/12/12/12_2023COL0002/_pdf/-char/en',
'P04':'https://link.springer.com/content/pdf/10.1007/s11042-023-14781-8.pdf',
'R03':'https://www.mit.edu/~modiano/papers/CV_J_104.pdf',
'R04':'https://www.mit.edu/~kadota/PDFs/2018INFOCOM.pdf',
'R05':'https://arxiv.org/pdf/1805.06752',
'R06':'https://soihub.org/site/assets/files/4411/supplemental_communication_kumar_pr_theory-of-qos-infocom.pdf',
}

def fetch(item):
    key, title = item
    result = {'id':key,'query_title':title,'accessed':'2026-11-06'}
    try:
        r = requests.get('https://api.crossref.org/works',params={'query.title':title,'rows':2},timeout=45)
        r.raise_for_status()
        records = r.json()['message']['items']
        (ROOT/f'{key}_crossref.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
        m=records[0]
        result.update(title=m.get('title',[''])[0],authors='; '.join(' '.join([a.get('given',''),a.get('family','')]).strip() for a in m.get('author',[])),doi=m.get('DOI',''),venue=m.get('container-title',[''])[0],year=m.get('published',{}).get('date-parts',[[None]])[0][0],links=m.get('link',[]))
    except Exception as e: result['metadata_error']=str(e)
    if key in PDFS:
        try:
            r=requests.get(PDFS[key],timeout=60);r.raise_for_status()
            if not r.content.startswith(b'%PDF'): raise ValueError('response is not PDF')
            p=ROOT/f'{key}.pdf';p.write_bytes(r.content)
            reader=PdfReader(p)
            (ROOT/f'{key}.txt').write_text('\n\n'.join(f'--- PAGE {i+1} ---\n'+page.extract_text() for i,page in enumerate(reader.pages)))
            result.update(full_text_url=PDFS[key],pages=len(reader.pages),sha256=hashlib.sha256(r.content).hexdigest())
        except Exception as e:result['full_text_error']=str(e)
    return result

if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(fetch,TITLES))
    (ROOT/'metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    for r in results:print(r['id'],r.get('title'),r.get('doi'),r.get('year'),'FULL' if 'pages' in r else r.get('full_text_error','metadata only'))
