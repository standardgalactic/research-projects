/**
 * StarGen — minimal JS codegen skeleton to emit Java files for StarGen.
 * Usage (conceptual): node StarGen.js
 * Writes example class content into ./generated/ (not used by Gradle build).
 */
const fs = require('fs');
const path = require('path');

function ensure(p){ fs.mkdirSync(p, { recursive: true }); }
function write(p, s){ ensure(path.dirname(p)); fs.writeFileSync(p, s); }

const genRoot = path.join(__dirname, 'generated', 'com', 'stargen');

function generateClass(name, body, pkg){
  return `package ${pkg};\n\npublic class ${name} {\n${body}\n}\n`;
}

(function main(){
  const p = path.join(genRoot, 'math', 'HelloGen.java');
  write(p, generateClass('HelloGen', '\tpublic String hello(){ return "Hello from StarGen"; }', 'com.stargen.math'));
  console.log('Generated example to', p);
})();
