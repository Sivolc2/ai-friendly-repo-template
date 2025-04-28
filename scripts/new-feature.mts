#!/usr/bin/env ts-node
import { mkdirSync, copyFileSync, writeFileSync } from "fs";
import { join } from "path";

const [pkg, name] = process.argv.slice(2);
if (!pkg || !name) {
  console.error("Usage: pnpm new-feature <backend|frontend> <slice>");
  process.exit(1);
}

const base = pkg === "backend"
  ? "packages/backend/modules"
  : "packages/frontend/src/features";

const templateBase = pkg === "backend"
  ? "packages/backend/modules/_template"
  : "packages/frontend/src/features/_template";

// Create feature directory
const featurePath = join(base, name);
mkdirSync(featurePath, { recursive: true });

// Create README_{folder_name}.md
const readmeContent = `# ${name}

## Overview
<!-- Add a brief description of this feature's purpose and functionality -->

## Architecture
<!-- Describe the data flow and component structure -->

## Public API
<!-- List and describe public functions, classes, and interfaces -->

## Implementation Details
<!-- Add implementation notes, dependencies, and important considerations -->
`;

writeFileSync(join(featurePath, `README_${name}.md`), readmeContent);

// Create basic structure
if (pkg === "backend") {
  // Python backend structure
  const files = {
    "__init__.py": "from .service import Service\n\n__all__ = ['Service']\n",
    "service.py": "from dataclasses import dataclass\nfrom typing import Optional\n\n@dataclass\nclass Service:\n    \"\"\"Service class for ${name} feature.\"\"\"\n    # TODO: Implement service\n",
    "types.py": "from dataclasses import dataclass\nfrom typing import Optional\n\n# TODO: Define types\n"
  };
  
  Object.entries(files).forEach(([filename, content]) => {
    writeFileSync(join(featurePath, filename), content);
  });

  // Create tests directory
  const testsPath = join(featurePath, "tests");
  mkdirSync(testsPath, { recursive: true });
  
  const testFiles = {
    "__init__.py": "",
    "test_service.py": "import pytest\nfrom ..service import Service\n\n# TODO: Implement tests\n"
  };
  
  Object.entries(testFiles).forEach(([filename, content]) => {
    writeFileSync(join(testsPath, filename), content);
  });
} else {
  // Frontend structure
  mkdirSync(join(featurePath, "components"), { recursive: true });
  mkdirSync(join(featurePath, "hooks"), { recursive: true });
  
  const files = {
    "index.ts": "export * from './components';\nexport * from './hooks';\n",
    "types.ts": "// TODO: Define types\n"
  };
  
  Object.entries(files).forEach(([filename, content]) => {
    writeFileSync(join(featurePath, filename), content);
  });
}

console.log(`New feature slice created at ${featurePath}`); 