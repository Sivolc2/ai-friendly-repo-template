# Gemini PRD Generator

This script automates the process of generating Product Requirements Documents (PRDs) using Google's Gemini API with context from your repository.

## Prerequisites

- Python 3.6+
- Google API key for Gemini
- `git dump` custom script in your PATH

## Installation

Make sure you have the required Python packages:

```bash
pip install requests
```

## Usage

```bash
python gemini_prd_generator.py --prompt "Create a PRD for feature X" --filename "feature_x_prd.md" --model "gemini-1.5-pro" --api-key "YOUR_API_KEY"
```

or with environment variable for API key:

```bash
export GOOGLE_API_KEY="your-api-key"
python gemini_prd_generator.py --prompt "Create a PRD for feature X" --filename "feature_x_prd.md"
```

### Arguments

- `--prompt`: The prompt to send to Gemini API (required)
- `--filename`: Name of the output file to be saved in docs/guides (required)
- `--api-key`: Google API key for Gemini (optional if GOOGLE_API_KEY environment variable is set)
- `--model`: Gemini model to use (optional, defaults to "gemini-2.5-pro-preview-03-25")

### Available Models

- `gemini-1.5-pro`: Gemini 1.5 Pro - Balanced performance model (recommended, most widely available, uses API version v1)
- `gemini-2.5-pro-preview-03-25`: Gemini 2.5 Pro Preview - Advanced reasoning and coding capabilities (limited availability, uses API version v1)
- `gemini-2.5-flash-preview-04-17`: Gemini 2.5 Flash Preview - Optimized for adaptive thinking and cost efficiency (limited availability, uses API version v1)

> **Note:** Model availability may change over time. The older `gemini-pro` model is no longer supported. The script automatically uses the correct API version for each model.

## Workflow

1. The script runs the `git dump` command to generate repository context
2. It sends this context along with your prompt to the Gemini API
3. The response is saved as a markdown file in the `docs/guides` directory

## Example Prompt Template

Here's a template for effective PRD generation:

```
Create a PRD for adding [feature]. The PRD should include:
1. Problem statement
2. Proposed solution
3. User stories
4. Technical requirements
5. Implementation approach
6. Success metrics
```

## Output

The generated PRD will be saved in the `docs/guides` directory with the filename you specified. 