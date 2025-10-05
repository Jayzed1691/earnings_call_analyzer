# Quick Setup Guide

## 5-Minute Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('punkt')"
   ```

2. **Install and start Ollama**
   ```bash
   # Install from https://ollama.ai
   ollama serve  # In separate terminal
   ollama pull llama3.1:8b
   ```

3. **Set up dictionaries**
   ```bash
   python scripts/download_dictionaries.py --create-starter
   ```

4. **Verify installation**
   ```bash
   python cli.py check-setup
   ```

5. **Run test analysis**
   ```bash
   python cli.py analyze data/transcripts/sample_earnings_call.txt --summary
   ```

## Troubleshooting

**Import errors?**
- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt` again

**Ollama connection failed?**
- Ensure `ollama serve` is running in another terminal
- Check OLLAMA_HOST in .env matches the server address

**Missing dictionaries?**
- Run `python scripts/download_dictionaries.py --create-starter`

**Slow analysis?**
- Use `--no-llm` flag for 3x faster processing
- Switch to smaller model like `phi3`

## Common Commands

```bash
# Analyze with summary
python cli.py analyze transcript.txt -s

# Fast mode (no LLM)
python cli.py analyze transcript.txt --no-llm -s

# Validate transcript format
python cli.py validate transcript.txt

# Check system status
python cli.py check-setup

# View configuration
python cli.py info
```
