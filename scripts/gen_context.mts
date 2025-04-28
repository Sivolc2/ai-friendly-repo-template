#!/usr/bin/env ts-node
/**
 * Generates /registry/project_registry.json  +  /registry/modules_index.md
 * Covers feature slices AND shared packages.
 *
 * Usage:  pnpm gen:context [backend|frontend]
 * If no package specified, generates for both backend and frontend
 */
import { readdirSync, readFileSync, writeFileSync, existsSync } from "fs";
import { join, relative, basename } from "path";

const [pkg] = process.argv.slice(2);
if (pkg && !["backend", "frontend"].includes(pkg)) {
  console.error("Usage: pnpm gen:context [backend|frontend]");
  process.exit(1);
}

const packages = pkg ? [pkg] : ["backend", "frontend"];

/* ---------- helpers ----------------------------------------------------- */
function listDirs(path: string) {
  return readdirSync(path, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}

function listFilesRecursive(dir: string, pkgRoot: string, out: string[] = []): string[] {
  if (!existsSync(dir)) return [];
  readdirSync(dir, { withFileTypes: true }).forEach(d => {
    const fp = join(dir, d.name);
    if (d.isDirectory()) listFilesRecursive(fp, pkgRoot, out);
    else out.push(relative(pkgRoot, fp));
  });
  return out;
}

function getIntent(readme: string): string {
  const m = readme.match(/<!-- INTENT:\s*([\s\S]*?)-->/);
  return m ? m[1].trim() : "No intent specified";
}

function getStability(readme: string): string {
  const m = readme.match(/Stability:\s*(\w+)/);
  return m ? m[1] : "Experimental";
}

function getOwner(readme: string): string {
  const m = readme.match(/Owned by:\s*([^\n]+)/);
  return m ? m[1].trim() : "Unassigned";
}

function readReadmeOrDefault(path: string, defaultIntent: string): string {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return `<!-- INTENT: ${defaultIntent}
Owned by: Unassigned
Stability: Experimental
-->

<!-- FILE INDEX: auto-generated -->

<!-- PUBLIC API: auto-generated -->`;
  }
}

/* ---------- process packages ------------------------------------------- */
const allRegistries = packages.map(pkg => {
  const PKG_ROOT = pkg === "backend"
    ? "packages/backend"
    : "packages/frontend/src";

  // Shared packages in correct order
  let sharedEntries: any[] = [];
  if (pkg === "backend") {
    ["core", "adapters"].forEach(dir => {
      const p = join(PKG_ROOT, dir);
      const readme = readReadmeOrDefault(join(p, `README_${basename(p)}.md`),
        dir === "core" 
          ? "Core backend services and utilities"
          : "External service integrations and adapters");
      sharedEntries.push({
        name: dir,
        path: p,
        intent: getIntent(readme),
        stability: getStability(readme),
        owner: getOwner(readme),
        files: listFilesRecursive(p, PKG_ROOT)
      });
    });
  } else {
    ["shared", "app"].forEach(dir => {
      const p = join(PKG_ROOT, dir);
      const readme = readReadmeOrDefault(join(p, `README_${basename(p)}.md`),
        dir === "shared"
          ? "Shared UI components and utilities"
          : "Core application components and layouts");
      sharedEntries.push({
        name: dir,
        path: p,
        intent: getIntent(readme),
        stability: getStability(readme),
        owner: getOwner(readme),
        files: listFilesRecursive(p, PKG_ROOT)
      });
    });
  }

  // Feature slices (modules)
  const sliceBase = pkg === "backend"
    ? join(PKG_ROOT, "modules")
    : join(PKG_ROOT, "features");
  const sliceNames = listDirs(sliceBase).filter(n => n !== "_template");
  const featureEntries = sliceNames.map(name => {
    const fp = join(sliceBase, name);
    const readme = readReadmeOrDefault(join(fp, `README_${basename(fp)}.md`), 
      `Feature module for ${name}`);
    return {
      name,
      path: fp,
      intent: getIntent(readme),
      stability: getStability(readme),
      owner: getOwner(readme),
      files: listFilesRecursive(fp, PKG_ROOT)
    };
  });

  return {
    package: pkg,
    generated: new Date().toISOString(),
    shared: sharedEntries,
    features: featureEntries
  };
});

/* ---------- assemble & write ------------------------------------------- */
const registryOut = {
  generated: new Date().toISOString(),
  packages: allRegistries
};

writeFileSync(
  join("registry", "project_registry.json"),
  JSON.stringify(registryOut, null, 2)
);

/* ---------- pretty Markdown index -------------------------------------- */
const mdBlocks = allRegistries.map(reg => {
  const blocks = [
    ...reg.shared.map(e => `## ${e.name} (Shared)
Intent: ${e.intent}
Owner: ${e.owner}
Stability: ${e.stability}

Files:
${e.files.map(f => `- ${f}`).join("\n")}
`),
    ...reg.features.map(e => `## ${e.name}
Intent: ${e.intent}
Owner: ${e.owner}
Stability: ${e.stability}

Files:
${e.files.map(f => `- ${f}`).join("\n")}
`)
  ];
  return `# Modules Index – ${reg.package}\n\n${blocks.join("\n")}`;
});

writeFileSync(
  join("registry", "modules_index.md"),
  mdBlocks.join("\n\n---\n\n")
);

console.log(`Registry & index updated for ${packages.join(", ")}`); 