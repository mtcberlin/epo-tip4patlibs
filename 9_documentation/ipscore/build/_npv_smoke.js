
const fs=require("fs"), vm=require("vm");
function test(path){
  const html=fs.readFileSync(path,"utf8");
  const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
  function noop(){return undefined;}
  const elementsById=new Map();
  function makeEl(id){
    const el={className:"",style:{},innerHTML:"",checked:false,textContent:"",
      classList:{add:noop,remove:noop,toggle:noop,contains:()=>false},
      addEventListener:noop,appendChild:noop,querySelectorAll:()=>[],querySelector:()=>null};
    let v=""; Object.defineProperty(el,"value",{get(){return v;},set(x){v=x;}});
    return el;
  }
  function getElementById(id){ if(!elementsById.has(id)) elementsById.set(id, makeEl(id)); return elementsById.get(id); }
  const pagesDiv={appendChild:noop,innerHTML:""};
  const sandbox={
    document:{addEventListener:noop, getElementById:(id)=> id==="pages"?pagesDiv: id==="step-bar"?makeEl("step-bar"):getElementById(id),
      querySelector:()=>({checked:false,classList:{add:noop,remove:noop,toggle:noop}}), querySelectorAll:()=>[],
      createElement:()=>makeEl(Symbol("a"))},
    console, setTimeout:(fn)=>fn(), alert:()=>{}, Math,Object,Array,JSON,String,Number,Boolean,Date
  };
  sandbox.window=sandbox;
  vm.createContext(sandbox);
  vm.runInContext(script, sandbox, {filename:path, timeout:5000});
  sandbox.buildPages();
  sandbox.fillDemo();
  sandbox.updateResults();
  return JSON.stringify({npv:getElementById("res-npv-val").textContent,
    verdict:getElementById("res-verdict").innerHTML.slice(0,50)});
}
console.log(test(process.argv[2]));
