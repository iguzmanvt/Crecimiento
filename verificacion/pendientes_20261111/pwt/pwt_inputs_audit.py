from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,hashlib,struct,collections,math
import pandas as pd
root=Path(r'C:\Users\IsaacGuzman\AppData\Local\Temp\github-pwt-discrepancy-20261111');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def read_xlsx(path):
 with zipfile.ZipFile(path) as z:
  strs=[''.join(e.itertext()) for e in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)];wb=E.fromstring(z.read('xl/workbook.xml'));rs={e.get('Id'):e.get('Target').lstrip('/') for e in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};sheets={e.get('name'):rs[e.get('{'+ns['r']+'}id')] for e in wb.findall('s:sheets/s:sheet',ns)}
  part=sheets['Data'];part=part if part.startswith('xl/') else 'xl/'+part;headers={};rows={};excel_rows={}
  with z.open(part) as f:
   for _,row in E.iterparse(f,events=('end',)):
    if not row.tag.endswith('}row'):continue
    vals={}
    for c in row.findall('s:c',ns):
     col=''.join(x for x in c.get('r') if x.isalpha());v=c.find('s:v',ns)
     if v is None or v.text is None:val=None
     elif c.get('t')=='s':val=strs[int(v.text)] or None
     elif c.get('t')=='e':val='ERROR:'+v.text
     else:val=float(v.text)
     vals[col]=val
    if row.get('r')=='1':headers=vals
    else:
     d={headers[k]:v for k,v in vals.items()};key=(d['countrycode'],int(d['year']));rows[key]=d;excel_rows[key]=int(row.get('r'))
    row.clear()
  return {'data':rows,'excel_rows':excel_rows,'columns':{v:k for k,v in headers.items()},'sheets':sheets,'Data_xml_sha256':hashlib.sha256(z.read(part)).hexdigest()}
repo=read_xlsx(root/'repo_ejemplo_estados_unidos.xlsx');official=read_xlsx(root/'official_pwt100.xlsx')
dta=pd.read_stata(root/'official_pwt100.dta',convert_categoricals=True,preserve_dtypes=True)
dcols=list(dta.columns);drows={(str(r['countrycode']),int(r['year'])):{k:None if pd.isna(v) or v=='' else v for k,v in r.items()} for r in dta.to_dict(orient='records')}
def compare_all(a,b):
 keys=sorted(set(a)&set(b));cols=list(next(iter(a.values())));counts=collections.Counter();examples=[]
 for key in keys:
  for c in cols:
   x=a[key].get(c);y=b[key].get(c)
   if x!=y:
    counts[c]+=1
    if len(examples)<10:examples.append({'key':key,'column':c,'left':x,'right':y})
 return {'keys_left':len(a),'keys_right':len(b),'common_keys':len(keys),'rows_columns_compared':len(keys)*len(cols),'column_mismatches':dict(counts),'examples':examples,'all_equal':not counts and set(a)==set(b)}
installed=json.loads((root/'installed_pwt100_USA.json').read_text(encoding='utf8'));pr={(r['isocode'],r['year']):{k:(r[k] if k=='isocode' else int(r[k]) if k=='year' else float(r[k])) for k in ['isocode','year','rgdpna','rnna','pop','hc']} for r in installed['USA']}
vars=['rgdpna','rnna','pop','hc'];inputs={}
for name,rows in [('repo_excel',repo['data']),('official_excel',official['data']),('official_dta',drows)]:
 inputs[name]=[{'isocode':key[0],'year':key[1],**{k:format(rows[key][k],'.17g') for k in vars}} for key in sorted(rows) if key[0]=='USA']
inputs['installed_pwt100']=installed['USA']
profile=[]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
for key in sorted(pr):
 x=repo['data'][key]['rnna'];y=pr[key]['rnna'];profile.append({'year':key[1],'xlsx_cell':'V'+str(repo['excel_rows'][key]),'repo_rnna':x,'official_xlsx_rnna':official['data'][key]['rnna'],'official_dta_rnna':drows[key]['rnna'],'cran_rnna':y,'cran_minus_xlsx':y-x,'absolute_relative_difference':abs(y-x)/x,'xlsx_exact_float32':f32(x)==x,'cran_exact_float32':f32(y)==y,'xlsx_float32_bits':hex(bits(x)),'cran_float32_bits':hex(bits(y)),'float32_ulp_distance':abs(bits(y)-bits(x))})
summary={'pandas_version':pd.__version__,'DTA_value_labels_decoded':True,'blank_strings_normalized_to_missing':True,'repo_workbook_sheets':list(repo['sheets']),'official_workbook_sheets':list(official['sheets']),'repo_Data_XML_sha256':repo['Data_xml_sha256'],'official_Data_XML_sha256':official['Data_xml_sha256'],'repo_vs_official_xlsx_Data':compare_all(repo['data'],official['data']),'official_xlsx_vs_DTA_Data':compare_all(official['data'],drows),'dta_input_dtypes':{k:str(dta[k].dtype) for k in ['year']+vars},'rnna_profile_summary':{'years':len(profile),'mismatches':sum(x['cran_minus_xlsx']!=0 for x in profile),'max_abs_difference':max(abs(x['cran_minus_xlsx']) for x in profile),'max_relative_difference':max(x['absolute_relative_difference'] for x in profile),'ulp_counts':dict(collections.Counter(x['float32_ulp_distance'] for x in profile)),'all_xlsx_and_cran_values_exact_float32':all(x['xlsx_exact_float32'] and x['cran_exact_float32'] for x in profile)},'Rmd_executed':False,'formulas_recalculated':False}
(root/'numeric_input_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8',newline='\n');(root/'rnna_pairs_USA.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf8',newline='\n');(root/'USA_inputs_for_R.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf8',newline='\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
