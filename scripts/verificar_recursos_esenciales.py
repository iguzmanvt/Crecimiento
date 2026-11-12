#!/usr/bin/env python3
"""Comprueba las vistas esenciales contra datos archivados y, opcionalmente, navegador sin red."""
from pathlib import Path
import argparse,csv,hashlib,json,math,struct,xml.etree.ElementTree as ET,datetime,importlib.util,sys
from urllib.parse import urlsplit
from urllib.request import url2pathname

def readcsv(p):
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):return math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-10)
def main():
 pa=argparse.ArgumentParser(description=__doc__);pa.add_argument("root",nargs="?",type=Path);pa.add_argument("--browser",action="store_true");pa.add_argument("--report",type=Path);a=pa.parse_args()
 repo=(a.root or Path(__file__).resolve().parents[1]).resolve();root=repo/"recursos_esenciales";cat=json.loads((root/"catalogo.json").read_text(encoding="utf8"));entries=cat["entries"]
 assert len(entries)==21 and len({e["slug"] for e in entries})==21
 for p,v in cat["inputs"].items():assert h(repo/p)==v["sha256"],p
 assert not (root/"originales/primary-energy-cons.csv").exists()
 assert not (root/"originales/per-capita-energy-use.csv").exists()
 spec=importlib.util.spec_from_file_location("ess_gen",repo/"scripts/generar_recursos_esenciales.py");g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 rawenergy={(r["Entity"],int(r["Year"])):r for r in readcsv(root/"originales/energy-use-per-capita-vs-gdp-per-capita.csv")}
 configs=json.loads((root/"metadatos/energy-use-per-capita-vs-gdp-per-capita.config.json").read_text(encoding="utf8"));factor=next(d["display"]["conversionFactor"] for d in configs["dimensions"] if d["variableId"]==1293798)
 assert factor==11.63
 byid={e["id"]:e for e in entries};rows={}
 for e in entries:
  for k in ("html","csv","json","png","svg"):
   if e.get(k):assert (repo/e[k]).is_file(),e[k]
  assert e["units"]==e["unit"] and e["period"] and e["source"] and e["equivalence"]
  if e["json"] is None:continue
  data=readcsv(repo/e["csv"]);rows[e["id"]]=data
  assert len(data)==e["observations"]
  keys=[(r["entity"],r["year"]) for r in data];assert len(keys)==len(set(keys)),e["id"]
  j=json.loads((repo/e["json"]).read_text(encoding="utf8"));assert j["data"]
  if j["data"][0]["type"]=="table":assert len(j["data"][0]["cells"]["values"][0])==len(data)
  elif "value" in data[0]:
   got=[]
   for t in j["data"]:
    vals=t["x"] if t["type"]=="bar" else t["y"]
    got.extend(v for v in vals if v is not None)
   assert sorted(float(r["value"]) for r in data)==sorted(got),e["id"]
  else:
   assert len(j["data"])==1
   assert [float(r["x"]) for r in data]==j["data"][0]["x"] and [float(r["y"]) for r in data]==j["data"][0]["y"],e["id"]
   assert len({r["year"] for r in data})==1
  p=repo/e["png"];png=p.read_bytes();assert png[:8]==b"\x89PNG\r\n\x1a\n";assert struct.unpack(">II",png[16:24])==(1200,700),p
  svg=ET.parse(repo/e["svg"]);assert svg.getroot().tag.endswith("svg"),e["id"]
  for node in svg.iter():
   for k,v in node.attrib.items():
    if k.endswith("href"):assert not v.startswith(("http:","https:","//")),e["id"]
 # Values in the graph CSV apply a chart-display multiplier. Undo it explicitly.
 for r in rows["energia_por_persona"]:
  raw=rawenergy[(r["entity"],int(r["year"]))]
  assert close(r["value"],float(raw["Energy use per capita"])/factor)
 for r in rows["energia_total"]:
  raw=rawenergy[(r["entity"],int(r["year"]))]
  assert close(r["energy_kg_oil_eq_per_capita"],float(raw["Energy use per capita"])/factor)
  assert close(r["population"],raw["Population"])
  assert close(r["value"],float(r["energy_kg_oil_eq_per_capita"])*float(r["population"])/1e9)
 indicator=json.loads((root/"metadatos/indicadores/1293798.data.json").read_text(encoding="utf8"))
 indmeta=json.loads((root/"metadatos/indicadores/1293798.json").read_text(encoding="utf8"))
 entity_names={e["id"]:e["name"] for e in indmeta["dimensions"]["entities"]["values"]}
 base_values={(entity_names[e],str(y)):v for e,y,v in zip(indicator["entities"],indicator["years"],indicator["values"])}
 for r in rows["energia_por_persona"]:assert close(r["value"],base_values[(r["entity"],r["year"])]),r
 for r in rows["energia_ingreso"]:
  raw=rawenergy[(r["entity"],int(r["year"]))]
  assert close(r["y"],float(raw["Energy use per capita"])/factor) and close(r["x"],raw["GDP per capita"])
 # Million-ton conversions checked against each original country-year.
 for ident,slug,col in [("co2_total","annual-co2-emissions-per-country","Annual CO₂ emissions"),("so2_paises","so-emissions-by-world-region-in-million-tonnes","Sulfur dioxide"),("so2_regiones","so-emissions-by-world-region-in-million-tonnes","Sulfur dioxide")]:
  raw={(r["Entity"],r["Year"]):r for r in readcsv(root/"originales"/(slug+".csv"))}
  for r in rows[ident]:assert close(r["value"],float(raw[(r["entity"],r["year"])][col])/1e6)
 # Source anomaly remains unaltered and explicitly flagged.
 caf=next(r for r in rows["longevidad_ingreso"] if r["code"]=="CAF")
 assert caf["year"]=="2022" and close(caf["y"],18.8177) and "18.8177" in byid["longevidad_ingreso"]["note"]
 historic=repo/byid["tasa_marginal_maxima_historica"]["png"]
 assert h(historic)==h(repo/"Clases_Crecimiento_Economico/Taxes/Taxes-Tax_Rates.png")
 # Generation deterministic for all specifications, data and pages.
 targets=[root/"catalogo.json",root/"index.html",root/"README.md",root/"recursos.css"]+[repo/e[k] for e in entries for k in ("html","json","csv") if e.get(k)]
 before={str(p):h(p) for p in targets};g.build(repo);assert before=={str(p):h(p) for p in targets}
 browsers=[]
 if a.browser:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   chrome=Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe");kwargs={"headless":True}
   if chrome.exists():kwargs["executable_path"]=str(chrome)
   browser=p.chromium.launch(**kwargs)
   for e in entries:
    page=browser.new_page(viewport={"width":1100,"height":850});external=[];missing=[];errors=[];failed=[]
    def route(req):
     parts=urlsplit(req.request.url)
     if parts.scheme=="file":
      path=Path(url2pathname(parts.path))
      if not path.exists():missing.append(str(path))
      req.continue_()
     else:external.append(req.request.url);req.abort()
    page.route("**/*",route);page.on("pageerror",lambda er:errors.append(str(er)));page.on("requestfailed",lambda req:failed.append(req.url))
    page.goto((repo/e["html"]).as_uri(),wait_until="load");page.wait_for_selector('html[data-ready="true"]',state="attached")
    if e["json"]:
     metrics=page.evaluate('()=>({traces:document.getElementById("chart").data.length,svg:document.querySelectorAll("#chart svg.main-svg").length})')
     assert metrics["traces"]==len(json.loads((repo/e["json"]).read_text(encoding="utf8"))["data"]) and metrics["svg"]>0,e["id"]
    else:assert page.locator("img.historical").evaluate("(im)=>im.complete&&im.naturalWidth>0")
    page.set_viewport_size({"width":1100,"height":440})
    page.goto((repo/e["html"]).as_uri()+"?embed=1",wait_until="load");page.wait_for_selector('html[data-ready="true"]',state="attached")
    assert page.locator(".metadata").evaluate("(e)=>getComputedStyle(e).display")=="none"
    if e["json"]:
     dims=page.locator("#chart").evaluate("(e)=>({box:e.getBoundingClientRect().height,plot:e._fullLayout.height})")
     assert dims["box"]==440 and dims["plot"]==440,(e["id"],dims)
    assert not external and not missing and not errors and not failed,(e["id"],external,missing,errors,failed)
    browsers.append({"id":e["id"],"offline":True,"standalone":True,"embedded_height":440,"external_requests":0,"missing_resources":0,"javascript_errors":0})
    page.close();print("BROWSER",e["id"],flush=True)
   browser.close()
 report={"verified_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"count":21,"generated_figures":20,"historical_png_exact":True,"png_and_svg_checked":20,"unique_country_years":True,"same_year_scatter":True,"unit_conversion_kwh_to_kg_verified":11.63,"base_indicator_observations_matched":len(rows["energia_por_persona"]),"energy_total_reconciled":len(rows["energia_total"]),"million_tonne_conversions_checked":True,"source_anomaly_caf_preserved_and_flagged":True,"deterministic_generation":True,"browser_tests":browsers,"scope":"Vistas propias de recursos_esenciales y sus datos. No valida libros completos ni autenticidad pixel a pixel de iframes históricos. Navegador Chrome en Windows, con solicitudes externas bloqueadas."}
 dest=a.report or repo/"verificacion/estable_20261112/recursos_esenciales.json";dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
 print(json.dumps({k:v for k,v in report.items() if k!="browser_tests"},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
