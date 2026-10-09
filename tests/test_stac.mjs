import test from 'node:test';
import assert from 'node:assert/strict';
import {bboxValue,searchRequest,safeURL,nextRequest,uniqueFeatures,fetchJSON,validateFeatures,PRODUCTS} from '../web/stac/protocol.mjs';

const query={provider:'copernicus',collection:'sentinel-2-l2a',bbox:'72.63,18.88,73.13,19.28',start:'2024-04-01',end:'2024-04-30'};
test('bounded WGS84 requests reject invalid extents and dates',()=>{
  assert.deepEqual(bboxValue(query.bbox),[72.63,18.88,73.13,19.28]);
  for(const bbox of ['0,0,10,10','0,0,0,1','0,,1,1','0,NaN,1,1','180,0,-180,1','0,-91,1,0'])assert.throws(()=>bboxValue(bbox));
  for(const dates of [{start:'2024-02-30'}, {end:'2023-01-01'},{end:'2026-01-01'}])assert.throws(()=>searchRequest({...query,...dates}));
  assert.throws(()=>searchRequest({...query,collection:'unapproved'}));
  const r=searchRequest(query);assert.equal(new URL(r.url).searchParams.get('limit'),'8');assert.deepEqual(r.query.bbox,[72.63,18.88,73.13,19.28]);
});
test('pagination retains query and validates origins/methods',()=>{
  const r=searchRequest(query);
  const next=nextRequest({links:[{rel:'next',href:'/v1/search',method:'POST',merge:true,body:{token:'page2'}}]},r);
  assert.equal(next.body.token,'page2');assert.deepEqual(next.body.bbox,r.query.bbox);assert.equal(next.query,r.query);
  assert.throws(()=>nextRequest({links:[{rel:'next',href:'https://example.com/search'}]},r));
  assert.throws(()=>nextRequest({links:[{rel:'next',href:r.url,method:'DELETE'}]},r));
  for(const url of ['javascript:alert(1)','http://example.org/','https://user:secret@example.org/'])assert.throws(()=>safeURL(url));
});
test('duplicates and cap are applied to complete collection/item identifiers',()=>{
  const features=Array.from({length:30},(_,id)=>({type:'Feature',id,collection:'a'}));
  assert.equal(uniqueFeatures([...features,...features]).length,24);
  assert.equal(uniqueFeatures([{type:'Feature',id:'x',collection:'a'},{type:'Feature',id:'x',collection:'b'}]).length,2);
});
test('invalid remote geometry is rejected before display state changes',()=>{
 const feature=geometry=>({type:'Feature',id:'one',properties:{},geometry});
 for(const geometry of [{type:'Polygon',coordinates:[[['bad',19]]]}, {type:'Point',coordinates:[0,91]}, {type:'Unknown',coordinates:[]}, undefined])assert.throws(()=>validateFeatures([feature(geometry)]));
 assert.equal(validateFeatures([feature(null),feature({type:'Polygon',coordinates:[[[0,0],[1,0],[1,1],[0,0]]]})]).length,2);
 assert.match(PRODUCTS.gm_s2_annual.note,/geomedian/);
 assert.match(PRODUCTS.gm_s2_annual.licenseURL,/GeoMAD/);
 assert.match(PRODUCTS.wofs_ls_summary_annual.note,/clear Landsat/);
});
test('HTTP, HTML, malformed collections and CORS failures stay explicit',async()=>{
  const request=searchRequest(query);
  await assert.rejects(fetchJSON(request,async()=>({ok:false,status:429})),/429/);
  await assert.rejects(fetchJSON(request,async()=>({ok:true,json:async()=>{throw Error('HTML');}})),/non-JSON/);
  await assert.rejects(fetchJSON(request,async()=>({ok:true,json:async()=>({features:[]})})),/FeatureCollection/);
  await assert.rejects(fetchJSON(request,async()=>{throw TypeError('CORS');}),/CORS/);
  const result=await fetchJSON(request,async(url,options)=>{assert.equal(options.credentials,'omit');return {ok:true,json:async()=>({type:'FeatureCollection',features:[]})};});
  assert.deepEqual(result.features,[]);
});
