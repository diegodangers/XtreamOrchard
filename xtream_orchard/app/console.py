"""Minimal self-contained channel manager; bearer token stays in browser memory."""
from fastapi.responses import HTMLResponse

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XtreamOrchard</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif;background:#10151d;color:#f4f6fa}
body{max-width:1080px;margin:0 auto;padding:22px}header,.toolbar,.item{display:flex;align-items:center;gap:12px;justify-content:space-between}
h1{font-size:26px;margin:0}small,.muted{color:#9caabc}button,input{font:inherit;border-radius:10px;padding:10px;border:1px solid #465267}
button{background:#294c76;color:white;cursor:pointer}button:disabled{opacity:.45}input{background:#1d2632;color:white}
.panel{background:#1b2531;padding:18px;border-radius:14px;margin:16px 0}.toolbar{flex-wrap:wrap;justify-content:flex-start}
.item{border-bottom:1px solid #35404f;padding:12px 0;justify-content:flex-start}
.item label{flex:1;cursor:pointer}.item input{width:20px;height:20px}.item span{color:#a8b8c9}
#error{color:#ff9999}#status{color:#b5d5a6}
.tree-group,.tree-subgroup{border:1px solid #35404f;border-radius:10px;padding:10px;margin:8px 0}
.tree-subgroup{margin-left:14px}.tree-group summary,.tree-subgroup summary{cursor:pointer;font-weight:600}
.group-actions{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:8px 0}
.group-actions button{padding:6px 10px;font-size:13px}
</style></head><body>
<header><div><h1>XtreamOrchard</h1><small>Channel management • development preview</small></div></header>
<section class="panel"><p class="muted">Enter the local development API token. It is held in memory only and cleared on refresh. Do not use on an untrusted network.</p>
<div class="toolbar"><input id="token" type="password" placeholder="API bearer token" autocomplete="off"><button id="load">Load channels</button><button id="refresh">Refresh provider</button></div>
<p id="status"></p><p id="error" role="alert"></p></section>
<section class="panel"><div class="toolbar"><input id="search" type="search" placeholder="Search channels or categories"><button id="show">Show selected</button><button id="hide">Hide selected</button><button id="all">Select filtered</button><button id="none">Clear selection</button></div>
<p id="count" class="muted">Connect to load channels.</p><div id="channels"></div></section>
<script>
let items=[],selected=new Set();
const $=id=>document.getElementById(id);
const status=message=>{$("status").textContent=message;$("error").textContent=""};
const error=message=>{$("error").textContent=message;$("status").textContent=""};
async function api(path,options={}){
 const response=await fetch(path.replace(/^\\//,""),{...options,headers:{"Content-Type":"application/json",...(options.headers||{})}});
 if(!response.ok){
  if(response.status===401)throw Error("Home Assistant ingress authentication failed. Open this app from Home Assistant.");
  let detail="";
  try {
   const payload=await response.json();
   if(typeof payload.detail==="string")detail=payload.detail;
  }catch(_){}
  throw Error("Request failed ("+response.status+")"+(detail?": "+detail:""));
 }
 return response.json();
}
function splitCategory(value){
 const raw=String(value||"").trim(),pos=raw.indexOf("|");
 return pos<0?["Other",raw||"Uncategorized"]:[raw.slice(0,pos).trim()||"Other",raw.slice(pos+1).trim()||"Uncategorized"];
}
function filtered(){const q=$("search").value.trim().toLowerCase();return items.filter(c=>(c.name+" "+c.category).toLowerCase().includes(q))}
function makeButton(text,callback){
 const b=document.createElement("button");b.type="button";b.textContent=text;b.onclick=callback;return b;
}
function makeToggle(label,rows){
 const wrap=document.createElement("div");wrap.className="group-actions";
 const visible=rows.filter(c=>c.visible).length;
 const state=document.createElement("span");state.className="muted";state.textContent=visible===0?"Blocked":visible===rows.length?"Allowed":"Mixed";
 wrap.append(state,makeButton("Allow all",()=>changeGroup(rows,true,label)),makeButton("Block all",()=>changeGroup(rows,false,label)));
 return wrap;
}
async function changeGroup(rows,visible,label){
 if(!rows.length)return;
 const changes=rows.filter(c=>Boolean(c.visible)!==visible);
 if(!changes.length){status("No changes needed");return}
 if(!confirm((visible?"Allow ":"Block ")+changes.length+" channels in "+label+"?"))return;
 try{
  // Backend accepts at most 5000 IDs per atomic request.
  for(let i=0;i<changes.length;i+=5000){
   await api("/api/v1/channels/visibility",{method:"POST",body:JSON.stringify({ids:changes.slice(i,i+5000).map(c=>c.id),visible})});
  }
  items=await api("/api/v1/channels");render();status((visible?"Allowed ":"Blocked ")+changes.length+" channels in "+label);
 }catch(e){error("Update interrupted: "+e.message+". Reload to verify changes.")}
}
function render(){
 const rows=filtered();
 $("count").textContent=items.length+" channels • "+items.filter(c=>c.visible).length+" visible • "+selected.size+" selected";
 const root=$("channels");root.replaceChildren();
 const groups=new Map();
 for(const c of rows){
  const [group,sub]=splitCategory(c.category);
  if(!groups.has(group))groups.set(group,new Map());
  const children=groups.get(group);
  if(!children.has(sub))children.set(sub,[]);
  children.get(sub).push(c);
 }
 for(const [group,subgroups] of [...groups].sort((a,b)=>a[0].localeCompare(b[0]))){
  const groupRows=[...subgroups.values()].flat();
  const outer=document.createElement("details");outer.className="tree-group";
  const summary=document.createElement("summary");summary.textContent=group+" ("+groupRows.length+")";
  outer.append(summary,makeToggle(group,groupRows));
  for(const [sub,channels] of [...subgroups].sort((a,b)=>a[0].localeCompare(b[0]))){
   const inner=document.createElement("details");inner.className="tree-subgroup";
   const head=document.createElement("summary");head.textContent=sub+" ("+channels.length+")";
   inner.append(head,makeToggle(group+" / "+sub,channels));
   // Only render channel rows when a subgroup is opened; cap visible rows
   // to keep large catalogs responsive on phones and Home Assistant.
   const channelRoot=document.createElement("div");
   const draw=()=>{
    channelRoot.replaceChildren();
    if(!inner.open)return;
    for(const channel of channels.slice(0,250)){
     const row=document.createElement("div");row.className="item";
     const check=document.createElement("input");check.type="checkbox";check.checked=selected.has(channel.id);
     check.addEventListener("change",()=>{check.checked?selected.add(channel.id):selected.delete(channel.id);$("count").textContent=items.length+" channels • "+items.filter(c=>c.visible).length+" visible • "+selected.size+" selected"});
     const label=document.createElement("label");label.textContent=channel.name;
     const state=document.createElement("span");state.textContent=channel.visible?"Allowed":"Blocked";
     row.append(check,label,state);channelRoot.append(row);
    }
    if(channels.length>250){const note=document.createElement("p");note.className="muted";note.textContent="Showing first 250 channels. Search to narrow results; group actions affect all "+channels.length+" channels.";channelRoot.append(note)}
   };
   inner.addEventListener("toggle",draw);inner.append(channelRoot);outer.append(inner);
  }
  root.append(outer);
 }
}
async function load(){
 try{items=await api("/api/v1/channels");selected.clear();render();status("Catalog loaded")}
 catch(e){error(e.message)}
}
async function setVisibility(visible){
 if(!selected.size)return;
 try{
  const ids=[...selected];
  const result=await api("/api/v1/channels/visibility",{method:"POST",body:JSON.stringify({ids,visible})});
  items=await api("/api/v1/channels");selected.clear();render();status(result.updated+" channels updated");
 }catch(e){error("Update interrupted: "+e.message+". Reload to verify changes.")}
}
$("load").onclick=load;
$("show").onclick=()=>setVisibility(true);$("hide").onclick=()=>setVisibility(false);
$("search").oninput=render;$("all").onclick=()=>{filtered().forEach(c=>selected.add(c.id));render()};
$("none").onclick=()=>{selected.clear();render()};
$("refresh").onclick=async()=>{try{const result=await api("/api/v1/providers/xtream/refresh",{method:"POST"});items=await api("/api/v1/channels");selected.clear();render();status("Imported "+result.imported+" channels")}catch(e){error(e.message)}};
load();\n</script></body></html>"""


def register_console(app):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def console():
        return HTMLResponse(HTML, headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"})
