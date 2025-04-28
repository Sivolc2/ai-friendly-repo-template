#!/usr/bin/env ts-node
import { readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read registry
const registry = JSON.parse(
  readFileSync(join(__dirname, "..", "registry", "project_registry.json"), "utf-8")
);

// Generate edges
const edges = new Set<string>();

// Process each package
registry.packages.forEach((pkg: any) => {
  // Add package subgraph
  edges.add(`    subgraph ${pkg.package}`);
  
  // Output shared modules in order (core, adapters for backend; shared, app for frontend)
  pkg.shared.forEach((module: any) => {
    edges.add(`        ${pkg.package}_${module.name}[${module.name}]`);
    if (module.stability === "Stable") {
      edges.add(`        style ${pkg.package}_${module.name} fill:#90EE90`);
    } else if (module.stability === "Experimental") {
      edges.add(`        style ${pkg.package}_${module.name} fill:#FFB6C1`);
    }
  });

  // Output features (modules) after shared
  pkg.features.forEach((module: any) => {
    edges.add(`        ${pkg.package}_${module.name}[${module.name}]`);
    if (module.stability === "Stable") {
      edges.add(`        style ${pkg.package}_${module.name} fill:#90EE90`);
    } else if (module.stability === "Experimental") {
      edges.add(`        style ${pkg.package}_${module.name} fill:#FFB6C1`);
    }

    // Add dependencies to shared modules
    if (module.files.some((file: string) => file.includes("core"))) {
      edges.add(`        ${pkg.package}_${module.name} --> ${pkg.package}_core`);
    }
    if (module.files.some((file: string) => file.includes("adapters"))) {
      edges.add(`        ${pkg.package}_${module.name} --> ${pkg.package}_adapters`);
    }
    if (module.files.some((file: string) => file.includes("shared"))) {
      edges.add(`        ${pkg.package}_${module.name} --> ${pkg.package}_shared`);
    }
  });

  edges.add(`    end`);
});

// Generate Mermaid diagram dynamically
let backendNodes = '';
let frontendNodes = '';
let backendEdges = '';
let frontendEdges = '';

const backend = registry.packages.find((p: any) => p.package === 'backend');
const frontend = registry.packages.find((p: any) => p.package === 'frontend');

if (backend) {
  // Nodes
  backend.shared.forEach((mod: any) => {
    backendNodes += `        backend_${mod.name}[${mod.name}];\n        style backend_${mod.name} fill:${mod.stability === 'Stable' ? '#90EE90' : '#FFB6C1'},stroke:#333,color:#333;\n`;
  });
  backend.features.forEach((mod: any) => {
    backendNodes += `        backend_${mod.name}[${mod.name}];\n        style backend_${mod.name} fill:${mod.stability === 'Stable' ? '#90EE90' : '#FFB6C1'},stroke:#333,color:#333;\n`;
  });
  // Edges: core -> each feature
  backend.features.forEach((mod: any) => {
    backendEdges += `        backend_core --> backend_${mod.name};\n`;
  });
}
if (frontend) {
  // Nodes
  frontend.shared.forEach((mod: any) => {
    frontendNodes += `        frontend_${mod.name}[${mod.name}];\n        style frontend_${mod.name} fill:${mod.stability === 'Stable' ? '#90EE90' : '#FFB6C1'},stroke:#333,color:#333;\n`;
  });
  frontend.features.forEach((mod: any) => {
    frontendNodes += `        frontend_${mod.name}[${mod.name}];\n        style frontend_${mod.name} fill:${mod.stability === 'Stable' ? '#90EE90' : '#FFB6C1'},stroke:#333,color:#333;\n`;
  });
  // Edges: app -> shared, app -> each feature
  frontend.shared.forEach((mod: any) => {
    if (mod.name !== 'app') {
      frontendEdges += `        frontend_app --> frontend_${mod.name};\n`;
    }
  });
  frontend.features.forEach((mod: any) => {
    frontendEdges += `        frontend_app --> frontend_${mod.name};\n`;
  });
}

const graph = `# System Architecture Diagram

\`\`\`mermaid
graph TD;
    subgraph backend;
${backendNodes}    end;
    subgraph frontend;
${frontendNodes}    end;
    subgraph External;
        Storage[(Storage)];
    end;

    %% Cross-package dependencies
    backend_core --> Storage;
    backend_adapters --> Storage;

    %% Shared module dependencies
    backend_core --> backend_adapters;
${backendEdges}${frontendEdges}\`\`\`

## Legend
- 🟩 Green boxes represent stable modules
- 💗 Pink heart represents experimental modules (fill: #FFB6C1)
`;

// Write diagram
writeFileSync(
  join(__dirname, "..", "docs", "01_architecture_overview.md"),
  graph
);

console.log("System diagram updated successfully"); 