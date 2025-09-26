#!/bin/bash
# Get the root directory of the git repository
REPO_ROOT=$(git rev-parse --show-toplevel)
# Set output file name
OUTPUT_FILE="repo_contents.txt"

# Clear the file if it exists or create a new empty file
> "$OUTPUT_FILE"

# Define exclusion patterns
EXCLUDES=(
  # === Documentation & Non-Code Artifacts ===
  # General project documentation (often high-level or for human consumption)
  # READMEs within source directories are usually kept, but extensive `docs` folders might be skipped.
  "docs/**/*"
  "doc/**/*"
  "**/CHANGELOG.md"
  "**/CONTRIBUTING.md"
  "**/CODE_OF_CONDUCT.md"
  "**/LICENSE"
  "**/LICENSE.md"

  # === Configuration Files ===
  # IDE/editor specific configurations
  ".vscode/**/*"
  ".idea/**/*"
  ".cursor/**/*"
  "*.sublime-project"
  "*.sublime-workspace"

  # Tool-specific configurations (linters, formatters, CI, specific dev tools)
  # Keep if AI needs to understand or modify these toolings, skip if AI focuses on app logic.
  ".*.rc"             # .eslintrc, .babelrc, .prettierrc, etc.
  "*.config.js"       # jest.config.js, tailwind.config.js, etc. (be careful not to exclude app logic configs)
  "*.config.ts"       # vite.config.ts, playwright.config.ts, etc.
  "*.conf.yml"
  "*.conf.yaml"
  "*.ini"             # e.g., alembic.ini, tox.ini
  ".github/**/*"      # GitHub Actions workflows, issue templates, etc. (unless CI logic is the focus)
  ".gitlab-ci.yml"
  "Jenkinsfile"
  "Dockerfile"        # Unless AI needs to understand containerization
  "docker-compose.yml"

  # Monorepo/Build system configs
  "pnpm-workspace.yaml"
  "turbo.json"
  "lerna.json"
  "nx.json"

  # Example or default configurations
  "*.example"
  "*.sample"
  "*.defaults"

  # Environment variable files (NEVER include actual .env with secrets)
  ".env"
  ".env.*" # .env.local, .env.development, etc.
  "env.example"
  "env.defaults"

  # === Test Files & Artifacts ===
  "**/test/**/*"
  "**/tests/**/*"
  "**/__tests__/**/*"
  "**/*.test.*"       # *.test.js, *.test.ts, *.test.tsx, etc.
  "**/*.spec.*"       # *.spec.js, *.spec.ts, *.spec.tsx, etc.
  "**/fixtures/**/*"  # Test fixtures
  "**/testdata/**/*"
  "**/snapshots/**/*" # Jest snapshots
  "test-results/**/*"
  "coverage/**/*"
  "**/report/**/*"    # Test or coverage reports

  # === Build Outputs & Compiled Files ===
  "dist/**/*"
  "build/**/*"
  "out/**/*"
  "target/**/*"       # Common for Java/Rust
  ".next/**/*"        # Next.js build output
  "*.pyc"
  "*.pyo"
  "*.class"
  "*.o"
  "*.so"
  "*.dll"
  "*.exe"
  "__pycache__/**/*"

  # === Dependency & Package Management ===
  "node_modules/**/*"
  "bower_components/**/*"
  "vendor/**/*"       # Common for PHP/Ruby deps
  "**/venv/**/*"
  "**/.venv/**/*"
  "**/env/**/*"
  "**/.env/**/*"      # Python virtual environments (redundant with .env but good pattern)
  "package-lock.json"
  "yarn.lock"
  "pnpm-lock.yaml"
  "poetry.lock"
  "Pipfile.lock"
  "composer.lock"
  "Gemfile.lock"
  "Cargo.lock"        # Rust dependency lock file

  # === Version Control & Git ===
  ".git/**/*"
  ".svn/**/*"
  ".hg/**/*"
  ".gitattributes"
  # .gitignore (usually good to provide to AI to understand what's intentionally excluded)
  # .gitmodules (config for submodules, content of submodules might be relevant)

  # === OS-specific & Junk Files ===
  ".DS_Store"
  "Thumbs.db"

  # === Log Files ===
  "*.log"
  "logs/**/*"

  # === Database Migration Version Files ===
  # The scripts *generating* migrations or the ORM models are important,
  # but the individual version files are often less critical for understanding current state.
  "**/alembic/versions/**/*"
  "**/db/migrate/**/*"       # Ruby on Rails pattern
  "**/migrations/**/*"      # Django/other ORMs pattern

  # === Scripts & Tooling (if not core application logic) ===
  # This is context-dependent. If 'scripts' contains core business automation, keep it.
  # If it's mostly dev utilities, build scripts, linters, etc., it can be skipped.
  # "scripts/**/*"
  # "tools/**/*"

  # === Large Binary Assets & Design Files ===
  # Generally, AI works best with text.
  "*.png"
  "*.jpg"
  "*.jpeg"
  "*.gif"
  "*.bmp"
  "*.tiff"
  # "*.svg" # SVGs can sometimes be code-like or important for UI components
  "*.ico"
  "*.mp3"
  "*.wav"
  "*.mp4"
  "*.mov"
  "*.webm"
  "*.pdf" # Unless it's a spec document
  "*.zip"
  "*.tar"
  "*.gz"
  "*.rar"
  "*.jar"
  "*.war"
  "*.dmg"
  "*.iso"
  "*.fig"   # Figma files
  "*.sketch" # Sketch files
  "*.psd"   # Photoshop files
  "*.ai"    # Illustrator files
  "*.xd"    # Adobe XD files
  "*.xlsx"
  "*.xls"
  "*.docx"
  "*.doc"
  "*.pptx"
  "*.ppt"
  "*.stl"   # 3D model files
  "*.obj"   # 3D model files
  "*.fbx"   # 3D model files
  "*.glb"
  "*.gltf"
  "*.woff"
  "*.woff2"
  "*.ttf"
  "*.eot"
  "*.otf"

  # === Public/Static Assets (for frontends) ===
  # If the AI doesn't need to understand specific static assets served.
  "public/**/*"
  "static/**/*"
  # "assets/**/*" # Can be ambiguous; might contain important non-code assets or generated code.

  # === Demo/Example Code (if AI should focus on core product) ===
  "**/example/**/*"
  "**/examples/**/*"
  "**/demo/**/*"
  "**/demos/**/*"
  "**/samples/**/*"

  # === Generated Code/SDKs (if source is preferred or they are too verbose) ===
  # "**/generated/**/*" # Use with caution

  # === Specific tool output directories ===
  ".serverless/**/*"
  ".terraform/**/*"
  ".svelte-kit/**/*"
  ".astro/**/*"

  # === Rust-specific Files ===
  "*.rlib"            # Rust library files
  "*.rmeta"           # Rust metadata files
  "*.crate"           # Rust crate files
  "*.d"               # Dependency files generated by rustc
  "*.pdb"             # Debug symbol files (Windows)
  "*.dSYM/**/*"       # Debug symbol directories (macOS)
)

# Function to check if a file matches any exclude pattern
should_exclude() {
  local file="$1"
  for pattern in "${EXCLUDES[@]}"; do
    if [[ "$file" == $pattern ]]; then
      return 0  # Should exclude
    fi
  done
  return 1  # Should not exclude
}

# Get list of all committed files, excluding deleted ones
git ls-files | while read -r file; do
    if should_exclude "$file"; then
        continue
    fi

    # Check if file exists (not deleted)
    if [ -f "$REPO_ROOT/$file" ]; then
        # Add file name as header
        echo -e "\n\n===== $file =====\n" >> "$OUTPUT_FILE"

        # Append file contents
        cat "$REPO_ROOT/$file" >> "$OUTPUT_FILE"
    fi
done

echo "Repository contents dumped to $OUTPUT_FILE"
