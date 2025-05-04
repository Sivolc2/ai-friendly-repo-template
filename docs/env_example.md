# Environment Variables for Code Builder

Create a `.env` file in the `code_builder/` directory with your API keys and configuration. This file is automatically loaded by each aider agent when they start.

## Sample `.env` file

```bash
# Code Builder Environment Variables

# OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Anthropic API key (if using directly)
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI API key (if using directly) 
# OPENAI_API_KEY=sk-your-key-here

# DeepSeek API key (if using directly)
# DEEPSEEK_API_KEY=your-key-here

# Default model to use with aider
# Override the model specified in .aider.conf.yml
AIDER_MODEL=openrouter/anthropic/claude-3.5-sonnet

# Other optional environment variables
# AIDER_CHAT_HISTORY_FILE=.aider.chat.history.md
# AIDER_AUTO_COMMITS=false
```

## Common Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (if using directly) |
| `OPENAI_API_KEY` | Your OpenAI API key (if using directly) |
| `DEEPSEEK_API_KEY` | Your DeepSeek API key (if using directly) |
| `AIDER_MODEL` | Override the model specified in .aider.conf.yml |
| `AIDER_CHAT_HISTORY_FILE` | Path to the chat history file |
| `AIDER_AUTO_COMMITS` | Whether to automatically commit changes |

## Security Notes

- The `.env` file is excluded from git in the `.gitignore`
- Never commit your API keys to the repository
- You may want to use different environments per project 