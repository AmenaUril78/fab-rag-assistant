#!/bin/bash
# Double-click this file in Finder to start the assistant.
# First time: right-click > Open (macOS asks once because it is a script).

cd "$(dirname "$0")" || exit 1
echo "Starting your RAG assistant..."

# 1) Start Ollama (free local AI model) if it is installed
if [ -d "/Applications/Ollama.app" ]; then
  open -ga Ollama
fi

# 2) Create the Python environment the first time
if [ ! -d ".venv" ]; then
  echo "First-time setup (takes a few minutes)..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 3) Get the latest version and libraries (quietly; fine if offline)
git pull --quiet 2>/dev/null
pip install --quiet --disable-pip-version-check -r requirements.txt

# 4) Use the local Ollama model if no settings file exists yet
if [ ! -f ".env" ]; then
  cat > .env <<'EOF'
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.2
EMBEDDING_PROVIDER=minilm
EOF
fi

# 5) Open the app in your browser (close this window to stop it)
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo "Leave this window open while you use it. Close it to stop the app."
python -m streamlit run app.py --server.headless false
