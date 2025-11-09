
/* StarGen — Java code generator for RSVP 4X + 6DOF engine
 * Node 18+ recommended. Generates Java sources into ./src/main/java/
 *
 * Usage:
 *   node StarGen.js all            # generate all core files
 *   node StarGen.js world          # WorldState only
 *   node StarGen.js research       # Technology & TechTree
 *   node StarGen.js patch-loop     # ensure GameLoop fields/hooks exist
 */

const fs = require('fs');
const path = require('path');

// ---------------- Utilities ----------------
function ensureDir(p){ fs.mkdirSync(p, { recursive: true }); }
function writeFile(p, s){
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, s);
  console.log("Wrote", p);
}

function cap(s){ return s.charAt(0).toUpperCase() + s.slice(1); }

function javaFile(pkg, imports, classCode){
  const importBlock = (imports && imports.length)
    ? imports.map(i => `import ${i};`).join("\n") + "\n\n"
    : "";
  return `package ${pkg};\n\n${importBlock}${classCode}`;
}

function generateClass(name, body, extendsName = "", implementsName = ""){
  const ex = extendsName ? ` extends ${extendsName}` : "";
  const im = implementsName ? ` implements ${implementsName}` : "";
  return `public class ${name}${ex}${im} {\n${body}\n}\n`;
}

function field(mod, type, name, init=null){
  return `    ${mod} ${type} ${name}${init!==null?` = ${init}`:""};\n`;
}

function getter(type, name){
  return `    public ${type} get${cap(name)}(){ return ${name}; }\n`;
}

function method(mod, ret, name, params, body){
  const indented = body.split("\n").map(l => l ? "        " + l : "").join("\n");
  return `    ${mod} ${ret} ${name}(${params}){\n${indented}\n    }\n`;
}

// Paths
const SRC = path.join(__dirname, "src", "main", "java", "com", "stargen");
const PKG_WORLD = "com.stargen.engine.simulation";
const PKG_RESEARCH = "com.stargen.research";
const PKG_ENGINE = "com.stargen.engine";

// ---------------- WorldState.java ----------------
function genWorldState(){
  const fields = [
    field("private", "float", "phi"),
    field("private", "float", "entropy"),
    field("private", "float", "lambdaCoupling"),
    field("private", "float", "sigmaDot"),
    field("private", "float", "R"),
    field("private", "float", "productionRate", "0.15f"),
    field("private", "float", "dissipationRate", "0.08f"),
    field("private", "float", "noiseLevel", "0.02f"),
  ].join("");

  const constructor = method("public", "", "WorldState", "float phiInit, float sInit, float lambdaInit", `
this.phi = phiInit;
this.entropy = sInit;
this.lambdaCoupling = lambdaInit;
updateDerived();
  `);

  const updateDerived = method("private", "void", "updateDerived", "", `
this.R = phi - lambdaCoupling * entropy;
this.sigmaDot = Math.max(0f, (productionRate - dissipationRate) + noiseLevel);
  `);

  const tick = method("public", "void", "tick", "float dt", `
phi += productionRate * dt * Math.max(0.05f, R);
entropy += (sigmaDot + noiseLevel) * dt;
updateDerived();
if (R < 0.1f) {
    entropy += 0.08f * dt;
    phi *= (1.0f - 0.01f * dt);
}
phi = Math.max(0f, Math.min(phi, 20f));
entropy = Math.max(0f, Math.min(entropy, 12f));
  `);

  const adjustors = [
    method("public", "void", "adjustLambda", "float d", "this.lambdaCoupling = Math.max(0f, Math.min(1.5f, lambdaCoupling + d)); updateDerived();"),
    method("public", "void", "addPhi", "float d", "this.phi = Math.max(0f, phi + d); updateDerived();"),
    method("public", "void", "addEntropy", "float d", "this.entropy = Math.max(0f, entropy + d); updateDerived();"),
  ].join("\n");

  const getters = [
    getter("float", "phi"),
    getter("float", "entropy"),
    getter("float", "lambdaCoupling"),
    getter("float", "sigmaDot"),
    getter("float", "R"),
  ].join("");

  const cls = generateClass("WorldState", fields + "\n" + constructor + "\n" + updateDerived + "\n" + tick + "\n" + adjustors + "\n" + getters);
  const code = javaFile(PKG_WORLD, [], cls);
  writeFile(path.join(SRC, "engine", "simulation", "WorldState.java"), code);
}

// ---------------- Technology.java ----------------
function genTechnology(){
  const fields = [
    field("public final", "String", "name"),
    field("public final", "float", "dPhi"),
    field("public final", "float", "dS"),
    field("public final", "float", "dLambda"),
    field("public", "boolean", "unlocked", "false"),
  ].join("");

  const ctor = method("public", "", "Technology", "String name, float dPhi, float dS, float dLambda", `
this.name = name; this.dPhi = dPhi; this.dS = dS; this.dLambda = dLambda;
  `);

  const cls = generateClass("Technology", fields + "\n" + ctor);
  const code = javaFile(PKG_RESEARCH, [], cls);
  writeFile(path.join(SRC, "research", "Technology.java"), code);
}

// ---------------- TechTree.java ----------------

function genTechTree(){
  const imports = [
    "java.util.*",
    "com.stargen.engine.simulation.WorldState"
  ];

  // load data
  const dataPath = path.join(__dirname, "research.techs.json");
  let data = { techs: [] };
  if (fs.existsSync(dataPath)){
    data = JSON.parse(fs.readFileSync(dataPath, "utf-8"));
  }

  const fields = [
    field("private final", "List<Technology>", "techs", "new ArrayList<>()"),
    field("private final", "WorldState", "world"),
  ].join("");

  const ctorBodyLines = [
    "this.world = world;",
    "// Generated from research.techs.json"
  ];
  (data.techs || []).forEach(t => {
    const name = t.name.replace(/"/g, '\"');
    const dPhi = (typeof t.dPhi === "number") ? t.dPhi.toFixed(2) + "f" : "0f";
    const dS = (typeof t.dS === "number") ? t.dS.toFixed(2) + "f" : "0f";
    const dLambda = (typeof t.dLambda === "number") ? t.dLambda.toFixed(2) + "f" : "0f";
    ctorBodyLines.push(`techs.add(new Technology("${name}", ${dPhi}, ${dS}, ${dLambda}));`);
  });
  const ctor = method("public", "", "TechTree", "WorldState world", "\n" + ctorBodyLines.join("\n") + "\n");

  const unlock = method("public", "void", "unlock", "String name", `
for (Technology t : techs){
    if (t.name.equals(name) && !t.unlocked){
        t.unlocked = true;
        world.addPhi(t.dPhi);
        world.addEntropy(t.dS);
        world.adjustLambda(t.dLambda);
        System.out.println("🔧 Tech Unlocked: " + name);
        return;
    }
}
System.out.println("Tech not found or already unlocked: " + name);
  `);

  const list = method("public", "List<Technology>", "list", "", "return techs;");

  const cls = generateClass("TechTree", fields + "\n" + ctor + "\n" + unlock + "\n" + list);
  const code = javaFile(PKG_RESEARCH, imports, cls);
  writeFile(path.join(SRC, "research", "TechTree.java"), code);
}


// ---------------- Patch GameLoop.java ----------------
function patchGameLoop(){
  const p = path.join(SRC, "engine", "GameLoop.java");
  if (!fs.existsSync(p)){
    console.warn("GameLoop.java not found; skipping patch.");
    return;
  }
  let s = fs.readFileSync(p, 'utf-8');

  // Ensure imports
  if (!s.includes("com.stargen.engine.simulation.WorldState"))
    s = s.replace("import com.stargen.entities.weapons.Projectile;", 
                  "import com.stargen.entities.weapons.Projectile;\nimport com.stargen.engine.simulation.WorldState;");
  if (!s.includes("import com.stargen.research.TechTree"))
    s = s.replace("import com.stargen.graphics.HUDRenderer;", 
                  "import com.stargen.graphics.HUDRenderer;\nimport com.stargen.research.TechTree;");

  // Ensure fields
  if (!s.includes("private WorldState world;"))
    s = s.replace("private Renderer renderer;", "private Renderer renderer;\n    private WorldState world;");
  if (!s.includes("private TechTree techTree;"))
    s = s.replace("private WorldState world;", "private WorldState world;\n    private TechTree techTree;");

  // Ensure constructor wiring
  if (!s.includes("this.world = new WorldState(")){
    s = s.replace("public GameLoop(){", "public GameLoop(){\n        this.world = new WorldState(1.0f, 0.2f, 0.4f);");
  }
  if (!s.includes("this.techTree = new TechTree(world);")){
    s = s.replace("this.world = new WorldState(1.0f, 0.2f, 0.4f);", "this.world = new WorldState(1.0f, 0.2f, 0.4f);\n        this.techTree = new TechTree(world);");
  }

  // Ensure loop tick
  if (!s.includes("world.tick(dt);")){
    s = s.replace("// 1) World RSVP tick", "// 1) World RSVP tick\n            world.tick(dt);");
  }

  fs.writeFileSync(p, s);
  console.log("Patched", p);
}

// ---------------- CLI ----------------
const cmd = process.argv[2] || "all";
switch(cmd){
  case "world":
    genWorldState(); break;
  case "research":
    genTechnology(); genTechTree(); break;
  case "patch-loop":
    patchGameLoop(); break;
  case "all":
  default:
    genWorldState();
    genTechnology();
    genTechTree();
    patchGameLoop();
    break;
}
