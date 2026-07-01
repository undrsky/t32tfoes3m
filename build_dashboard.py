import json,csv,os
BASE=os.path.dirname(os.path.abspath(__file__))
rows=list(csv.DictReader(open(os.path.join(BASE,"applications_tracker.csv"),encoding="utf-8")))
data=[{**r,"id":int(r["id"])} for r in rows]

DATA_JS = json.dumps(data)

html = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Application Tracker — Anna Kharzhevskaia</title>
<style>
:root{--bg:#f6f8fb;--card:#ffffff;--line:#e2e6ec;--txt:#1c2530;--mut:#5d6b7a;--acc:#2f6fd6;
--ready:#b5851f;--applied:#2f6fd6;--rej:#c0392b;--int:#2f9e4f;--offer:#8e44ad;--skip:#6b7280;--tmpl:#6b7280;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--txt);font-size:14px}
header{padding:18px 22px;border-bottom:1px solid var(--line)}
h1{margin:0 0 2px;font-size:20px}
.sub{color:var(--mut);font-size:13px}
.bar{display:flex;flex-wrap:wrap;gap:8px;padding:14px 22px;border-bottom:1px solid var(--line);align-items:center}
.bar input,.bar select{background:var(--card);border:1px solid var(--line);color:var(--txt);padding:8px 10px;border-radius:8px;font-size:13px}
.bar input[type=search]{min-width:240px;flex:1}
.stats{display:flex;flex-wrap:wrap;gap:8px;padding:14px 22px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;cursor:pointer;user-select:none}
.chip b{font-size:18px;display:block}
.chip span{color:var(--mut);font-size:12px}
.chip.active{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc) inset}
.wrap{padding:0 22px 40px;overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:880px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em;cursor:pointer;position:sticky;top:0;background:var(--bg)}
tr:hover td{background:#eef3f9}
.pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap}
.s-ready{background:rgba(217,164,65,.16);color:var(--ready)}
.s-applied{background:rgba(74,144,217,.16);color:var(--applied)}
.s-rejected{background:rgba(217,83,79,.16);color:var(--rej)}
.s-interview{background:rgba(92,184,92,.16);color:var(--int)}
.s-offer{background:rgba(155,89,182,.18);color:var(--offer)}
.s-skipped{background:rgba(127,136,150,.16);color:var(--skip)}
.s-template{background:rgba(90,97,114,.16);color:var(--tmpl)}
.co{font-weight:600}
.role{color:var(--mut);font-size:13px}
.dup{color:var(--rej);font-weight:700;cursor:help}
.muted{color:var(--mut);font-size:12px}
.foot{color:var(--mut);font-size:12px;padding:0 22px 30px}
a{color:var(--acc)}
</style></head><body>
<header>
<h1>Job Application Tracker</h1>
<div class="sub">Anna Kharzhevskaia · Program / Project / Product Manager · Seattle / Remote · <span id="updated"></span></div>
</header>
<div class="stats" id="stats"></div>
<div class="bar">
<input type="search" id="q" placeholder="Search company, role, notes…">
<select id="fStatus"><option value="">All statuses</option></select>
<select id="fType"><option value="">Apps + templates</option><option value="app">Applications only</option><option value="template">Templates only</option></select>
<label class="muted"><input type="checkbox" id="fDup"> Duplicates only</label>
</div>
<div class="wrap">
<table id="tbl"><thead><tr>
<th data-k="company">Company</th><th data-k="role">Role</th><th data-k="status">Status</th>
<th data-k="date_added">Added</th><th data-k="date_applied">Applied</th><th data-k="fit_score">Fit</th>
<th data-k="resume_file">Resume</th><th>Link</th><th data-k="outcome_next_step">Outcome / Next</th>
</tr></thead><tbody id="tb"></tbody></table>
</div>
<div class="foot">Source of truth is <b>applications_tracker.csv</b> in this folder. Ask Claude to add jobs, change a status, or log a rejection/interview and this view will be rebuilt.</div>
<script>
const DATA = __DATA__;
document.getElementById('updated').textContent = 'Updated ' + new Date().toLocaleDateString();
// flag duplicates by dedupe_key among apps
const counts={}; DATA.forEach(r=>{if(r.type==='app')counts[r.dedupe_key]=(counts[r.dedupe_key]||0)+1;});
DATA.forEach(r=> r._dup = r.type==='app' && counts[r.dedupe_key]>1);
function sCls(s){return 's-'+(s||'').toLowerCase().replace(/[^a-z]/g,'');}
const STATUSES=['Resume ready','Applied','Interview','Offer','Rejected','Skipped','Template'];
const selStatus=document.getElementById('fStatus');
STATUSES.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;selStatus.appendChild(o);});
let sortK='date_added', sortDir=-1, statusFilter='';
function fchars(){return {q:document.getElementById('q').value.toLowerCase(),
  st:selStatus.value, ty:document.getElementById('fType').value, dup:document.getElementById('fDup').checked};}
function render(){
  const f=fchars();
  let rows=DATA.filter(r=>{
    if(f.ty && r.type!==f.ty) return false;
    if(f.st && r.status!==f.st) return false;
    if(statusFilter && r.status!==statusFilter) return false;
    if(f.dup && !r._dup) return false;
    if(f.q){const blob=(r.company+' '+r.role+' '+r.decision_notes+' '+r.outcome_next_step+' '+r.req_id).toLowerCase();
      if(!blob.includes(f.q)) return false;}
    return true;});
  rows.sort((a,b)=>{const x=(a[sortK]||''),y=(b[sortK]||'');return x<y?-sortDir:x>y?sortDir:0;});
  const tb=document.getElementById('tb');tb.innerHTML='';
  rows.forEach(r=>{
    const tr=document.createElement('tr');
    const fn=r.resume_file?r.resume_file.split('/').pop():'';
    tr.innerHTML=`<td class="co">${r.company}${r._dup?' <span class="dup" title="Possible duplicate opening — same company+role tailored more than once">⚠︎</span>':''}</td>
      <td class="role">${r.role}${r.req_id?' <span class="muted">·'+r.req_id+'</span>':''}</td>
      <td><span class="pill ${sCls(r.status)}">${r.status}</span></td>
      <td class="muted">${r.date_added}</td><td class="muted">${r.date_applied||''}</td>
      <td>${r.fit_score||''}</td>
      <td class="muted" title="${r.resume_file}">${fn}</td>
      <td>${r.job_url?`<a href="${r.job_url}" target="_blank" rel="noopener">open</a>`:''}</td>
      <td class="muted">${r.outcome_next_step||''}</td>`;
    tb.appendChild(tr);});
  // stats
  const by={}; DATA.forEach(r=>by[r.status]=(by[r.status]||0)+1);
  const order=['Resume ready','Applied','Interview','Offer','Rejected','Skipped','Template'];
  const st=document.getElementById('stats');st.innerHTML='';
  const all=document.createElement('div');all.className='chip'+(statusFilter===''?' active':'');
  all.innerHTML=`<b>${DATA.length}</b><span>Total</span>`;all.onclick=()=>{statusFilter='';render();};st.appendChild(all);
  order.forEach(s=>{if(!by[s])return;const c=document.createElement('div');
    c.className='chip'+(statusFilter===s?' active':'');
    c.innerHTML=`<b>${by[s]}</b><span>${s}</span>`;c.onclick=()=>{statusFilter=statusFilter===s?'':s;render();};st.appendChild(c);});
  const d=Object.values(counts).filter(n=>n>1).length;
  if(d){const c=document.createElement('div');c.className='chip';c.style.borderColor='var(--rej)';
    c.innerHTML=`<b style="color:var(--rej)">${d}</b><span>Dup groups</span>`;
    c.onclick=()=>{document.getElementById('fDup').checked=true;render();};st.appendChild(c);}
}
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(!k)return;
  if(sortK===k)sortDir*=-1;else{sortK=k;sortDir=1;}render();});
['q','fType','fDup'].forEach(id=>document.getElementById(id).addEventListener('input',render));
selStatus.addEventListener('change',()=>{statusFilter='';render();});
render();
</script></body></html>'''

html = html.replace("__DATA__", DATA_JS)
open(os.path.join(BASE,"dashboard.html"),"w",encoding="utf-8").write(html)
print("dashboard.html written,", len(html), "bytes")
