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
</style></head><body>
<header><div><h1>XtreamOrchard</h1><small>Channel management • development preview</small></div><button id="connect">Connect</button></header>
<section class="panel"><p class="muted">Enter the local development API token. It is held in memory only and cleared on refresh. Do not use on an untrusted network.</p>
<div class="toolbar"><input id="token" type="password" placeholder="API bearer token" autocomplete="off"><button id="load">Load channels</button><button id="refresh">Refresh provider</button></div>
<p id="status"></p><p id="error" role="alert"></p></section>
<section class="panel"><div class="toolbar"><input id="search" type="search" placeholder="Search channels or categories"><button id="show">Show selected</button><button id="hide">Hide selected</button><button id="all">Select filtered</button><button id="none">Clear selection</button></div>
<p id="count" class="muted">Connect to load channels.</p><div id="channels"></div></section>
<script>
let token="",items=[],selected=new Set();
const $=id=>document.getElementById(id);
const status=message=>{$("status").textContent=message;$("error").textContent=""};
const error=message=>{$("error").textContent=message;$("status").textContent=""};
async function api(path,options={}){
 const response=await fetch(path.replace(/^\\//,""),{...options,headers:{"Authorization":"Bearer "+token,"Content-Type":"application/json",...(options.headers||{})}});
 if(!response.ok){
  let detail="";
  try {
   const payload=await response.json();
   if(typeof payload.detail==="string")detail=payload.detail;
  }catch(_){}
  throw Error("Request failed ("+response.status+")"+(detail?": "+detail:""));
 }
 return response.json();
}
function filtered(){const q=$("search").value.trim().toLowerCase();return items.filter(c=>(c.name+" "+c.category).toLowerCase().includes(q))}
function render(){
 const rows=filtered();$("count").textContent=items.length+" channels • "+items.filter(c=>c.visible).length+" visible • "+selected.size+" selected";
 const root=$("channels");root.replaceChildren();
 for(const channel of rows){
  const row=document.createElement("div");row.className="item";
  const check=document.createElement("input");check.type="checkbox";check.checked=selected.has(channel.id);
  check.addEventListener("change",()=>{check.checked?selected.add(channel.id):selected.delete(channel.id);render()});
  const label=document.createElement("label");label.textContent=channel.name;
  const category=document.createElement("span");category.textContent=channel.category+" • "+(channel.visible?"Visible":"Hidden");
  row.append(check,label,category);root.append(row);
 }
}
async function load(){token=$("token").value.trim();if(!token){error("Enter the API token");return}
 try{items=await api("/api/v1/channels");selected.clear();render();status("Catalog loaded")}catch(e){error(e.message)}}
async function setVisibility(visible){
 if(!selected.size)return;
 try{
  const ids=[...selected];
  const result=await api("/api/v1/channels/visibility",{method:"POST",body:JSON.stringify({ids,visible})});
  items=await api("/api/v1/channels");selected.clear();render();status(result.updated+" channels updated");
 }catch(e){error("Update interrupted: "+e.message+". Reload to verify changes.")}
}
$("load").onclick=load;$("connect").onclick=load;
$("show").onclick=()=>setVisibility(true);$("hide").onclick=()=>setVisibility(false);
$("search").oninput=render;$("all").onclick=()=>{filtered().forEach(c=>selected.add(c.id));render()};
$("none").onclick=()=>{selected.clear();render()};
$("refresh").onclick=async()=>{try{const result=await api("/api/v1/providers/xtream/refresh",{method:"POST"});items=await api("/api/v1/channels");selected.clear();render();status("Imported "+result.imported+" channels")}catch(e){error(e.message)}};
</script></body></html>"""


def register_console(app):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def console():
        return HTMLResponse(HTML, headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"})
