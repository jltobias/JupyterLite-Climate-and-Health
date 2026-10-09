// Original bounded STAC adapter. Architectural inspiration: jltobias/JupyterLite-STAC-Browser (MIT).
export const PROVIDERS={copernicus:{name:'Copernicus Data Space',search:'https://stac.dataspace.copernicus.eu/v1/search',collections:[['sentinel-2-l2a','Sentinel-2 L2A · surface reflectance']],license:'Copernicus Sentinel Data Legal Notice',licenseURL:'https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice'},dea:{name:'Digital Earth Africa',search:'https://explorer.digitalearth.africa/stac/search',collections:[['wofs_ls_summary_annual','WOfS · annual water observations'],['gm_s2_annual','GeoMAD · annual Sentinel-2']],license:'CC BY 4.0; product acknowledgements apply',licenseURL:'https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html'}};
export const PRODUCTS={
 'sentinel-2-l2a':{title:'Sentinel-2 L2A',note:'Surface reflectance scenes are not measurements of air temperature, disease, or facility exposure.',attribution:'Contains Copernicus Sentinel data; retain acquisition year and source identifiers.'},
 wofs_ls_summary_annual:{title:'Annual WOfS',note:'WOfS summarizes wet observations among clear Landsat observations. It is not flood probability, drinking-water quality, or a measured flood depth.',licenseURL:'https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html',attribution:'Digital Earth Africa Water Observations from Space; CC BY 4.0.'},
 gm_s2_annual:{title:'Annual Sentinel-2 GeoMAD',note:'GeoMAD combines Sentinel-2 geomedian surface reflectance with median absolute deviation statistics over the stated year. These summaries are not air temperature, flood frequency, water quality or health outcomes.',licenseURL:'https://docs.digitalearthafrica.org/en/latest/data_specs/GeoMAD_specs.html',attribution:'Digital Earth Africa GeoMAD; contains modified Copernicus Sentinel data. Retain acquisition year; CC BY 4.0.'}
};

// Validate before touching a displayed dataset: failed provider responses must
// never change exports while the screen still shows the previous evidence.
export function validateFeatures(features){
 if(!Array.isArray(features))throw new Error('Evidence features must be an array.');
 const position=p=>Array.isArray(p)&&p.length>=2&&p.every(Number.isFinite)&&p[0]>=-180&&p[0]<=180&&p[1]>=-90&&p[1]<=90;
 const line=(c,min)=>Array.isArray(c)&&c.length>=min&&c.every(position);
 const ring=c=>line(c,4)&&c[0].length===c.at(-1).length&&c[0].every((v,i)=>v===c.at(-1)[i]);
 const polygon=c=>Array.isArray(c)&&c.length>0&&c.every(ring);
 function geometry(g){
  if(g===null)return true; // Non-spatial records remain inspectable in the table.
  if(!g||typeof g!=='object')return false;
  const c=g.coordinates;
  switch(g.type){
   case 'Point':return position(c);
   case 'MultiPoint':return line(c,1);
   case 'LineString':return line(c,2);
   case 'MultiLineString':return Array.isArray(c)&&c.length>0&&c.every(l=>line(l,2));
   case 'Polygon':return polygon(c);
   case 'MultiPolygon':return Array.isArray(c)&&c.length>0&&c.every(polygon);
   case 'GeometryCollection':return Array.isArray(g.geometries)&&g.geometries.every(geometry);
   default:return false;
  }
 }
 for(const f of features){
  if(!f||f.type!=='Feature'||!['string','number'].includes(typeof f.id)||!geometry(f.geometry))throw new Error('A provider item has an invalid identifier or WGS84 geometry; that response was not loaded.');
 }
 return features;
}
export function safeURL(value){const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password)throw new Error('Only public HTTPS links are supported.');return u.href;}
export function bboxValue(value){const b=typeof value==='string'?value.split(',').map(x=>x.trim()):value;if(!Array.isArray(b)||b.length!==4||b.some(x=>x===''||x===null))throw new Error('Enter four coordinates: west, south, east, north.');const v=b.map(Number);if(v.some(x=>!Number.isFinite(x))||v[0]<-180||v[2]>180||v[1]<-90||v[3]>90||v[0]>=v[2]||v[1]>=v[3])throw new Error('Use a valid WGS84 bounding box with west < east and south < north. Split antimeridian areas.');if((v[2]-v[0])>5||(v[3]-v[1])>5)throw new Error('Keep this teaching query within 5° longitude and latitude.');return v;}
export function searchRequest({provider,collection,bbox,start,end}){const p=PROVIDERS[provider];if(!p||!p.collections.some(c=>c[0]===collection))throw new Error('Choose a supported provider and collection.');for(const d of [start,end]){if(!/^\d{4}-\d{2}-\d{2}$/.test(d)||!Number.isFinite(Date.parse(d))||new Date(d).toISOString().slice(0,10)!==d)throw new Error('Enter valid start and end dates.');}if(start>end)throw new Error('Start date must be on or before end date.');if((Date.parse(end)-Date.parse(start))/86400000>366)throw new Error('Limit this teaching query to one year.');const query={collections:[collection],bbox:bboxValue(bbox),datetime:`${start}T00:00:00Z/${end}T23:59:59Z`,limit:8};const url=new URL(p.search);url.search=new URLSearchParams({collections:collection,bbox:query.bbox.join(','),datetime:query.datetime,limit:'8'});return {url:url.href,method:'GET',query,provider};}
export async function fetchJSON(request,fetcher=fetch){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),20000);try{const response=await fetcher(request.url,{method:request.method||'GET',credentials:'omit',signal:controller.signal,headers:{Accept:'application/geo+json, application/json',...(request.body?{'Content-Type':'application/json'}:{})},...(request.body?{body:JSON.stringify(request.body)}:{})});if(!response.ok)throw new Error(`Provider returned HTTP ${response.status}.`);let data;try{data=await response.json();}catch{throw new Error('Provider returned non-JSON content. Try later or use a packaged example.');}if(data.type!=='FeatureCollection'||!Array.isArray(data.features))throw new Error('Provider did not return a STAC FeatureCollection.');return data;}catch(error){if(error.name==='AbortError')throw new Error('Request timed out after 20 seconds. Narrow the query or try a packaged example.');if(error instanceof TypeError)throw new Error('Unable to reach provider. Check network and browser CORS access; packaged examples remain available.');throw error;}finally{clearTimeout(timer);}}
export function nextRequest(document,previous){const link=(document.links||[]).find(l=>l.rel==='next');if(!link)return null;const url=safeURL(new URL(link.href,previous.url).href);if(new URL(url).origin!==new URL(PROVIDERS[previous.provider].search).origin)throw new Error('Provider pagination left the selected catalog origin.');const method=(link.method||'GET').toUpperCase();if(!['GET','POST'].includes(method))throw new Error('Unsupported pagination method.');return {url,method,provider:previous.provider,query:previous.query,...(method==='POST'?{body:link.merge?{...(previous.body||previous.query),...(link.body||{})}:(link.body||{})}:{})};}
export function uniqueFeatures(features){const seen=new Set();return features.filter(f=>{if(!f||f.type!=='Feature'||!['string','number'].includes(typeof f.id))return false;const k=`${f.collection||''}/${f.id}`;if(seen.has(k))return false;seen.add(k);return true;}).slice(0,24);}
