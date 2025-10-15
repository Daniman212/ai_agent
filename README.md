# Python CLI AI Agent

A lightweight, hackable command-line “AI agent” that chats, remembers context, inspects local files, and prints token usage. Built for fast iteration and learning.

## Motivation

I wanted a simple agent I could run from the terminal—no servers, no frameworks, no drama. It should:

- read config from environment variables (via `.env`)
- accept clean CLI args (without leaking flags like `--verbose` into prompts)
- keep lightweight conversation history
- expose small, composable tools (e.g., list files)
- print token counts so I know what I’m spending

This repo is the result: a tiny, readable codebase you can understand in an afternoon and extend in an evening.

## Quick Start

### Prerequisites
- **Python**: 3.11+ recommended  
- **API key** (pick one):
  - **Gemini (Google Generative AI)**: set `GOOGLE_API_KEY`  
  - *(Optional) OpenAI*: set `OPENAI_API_KEY` and choose `PROVIDER=openai`

### 1) Clone and set up the environment
```bash
git clone <your-repo-url>.git
cd <your-repo>
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# 2) Configure your .env
# Provider: gemini (default) or openai
PROVIDER=gemini

# For Gemini
GOOGLE_API_KEY=your_key_here

# For OpenAI (optional alternative)
# OPENAI_API_KEY=your_key_here

# Defaults you can tweak
MODEL=gemini-1.5-pro
HISTORY_PATH=.agent_history.json

# Usage

Global Help — discover commands & flags
python main.py --help
python main.py chat --help
python main.py files --help

Command: chat — converse with the model

Use this to send prompts and get responses, optionally persisting conversation history.

# Basic prompt
python main.py chat "Write a haiku about dual-cutting swords."

# Verbose mode (logs config & token counts; does NOT leak into the prompt)
python main.py chat "Explain BFS vs DFS." --verbose

# Pick a model at runtime
python main.py chat "Summarize today's tasks." --model gemini-1.5-pro

# Append to and use a persistent session history
python main.py chat "Continue our planning." --history

# Start a new topic without history
python main.py chat "Start a new topic." --no-history


Key behaviors

--history appends your message/response to a JSON file at HISTORY_PATH.

--verbose prints resolved config, token counts, and any tool calls to stderr only.

--model overrides the MODEL in .env for just this invocation.

--provider <gemini|openai> overrides provider for this run.

# Command: files — inspect local files & directories

Quickly list files with sizes and types for context.

# List files with sizes & types (implemented in functions/get_files_info.py)
python main.py files ./src

# Combine with verbose logging
python main.py files ./src --verbose

# Configuration notes

Provider & Model — Set in .env or override via flags.

.env loading — Environment is read at startup.

History — With --history, messages append to HISTORY_PATH (JSON).
Clear it with:

rm -f .agent_history.json

Project structure (for orientation)
.
├─ main.py                     # CLI entrypoint (argparse / command routing)
├─ functions/
│  └─ get_files_info.py       # Example tool: inspect files/dirs
├─ utils/
│  ├─ io.py                   # History store, JSON helpers
│  ├─ config.py               # Env/.env loading, provider/model resolution
│  └─ tokens.py               # Token accounting & reporting
├─ agents/
│  └─ loop.py                 # (Optional) agent loop / planning hooks
├─ requirements.txt
└─ .env.example               # Template for your .env

# Token accounting

After each run, the agent prints a compact summary (provider-dependent):

tokens: prompt=123, completion=45, total=168, cost≈$0.00X


Use --verbose for deeper diagnostics.

# Contributing

Contributions welcome! Please keep things small, legible, and testable.

Create a feature branch

git checkout -b feat/<short-name>


Code style

Use ruff + black (add to requirements-dev.txt if needed).

Prefer small, composable functions over large classes.

Add or extend tools

Place new tools in functions/ with a single, clear responsibility.

Include a docstring and at least one usage example in the module.

Testing

Add minimal tests or a runnable demo command.

If you change token or config handling, include a quick sanity test.

Pull requests

Title: concise & imperative (e.g., “Add markdown export tool”).

Description: what/why, notable decisions, and how to test.

Keep PRs under ~300 lines when possible.

Good first issues

Add --profile <name> to load .env.<profile> files.

Add a search tool (e.g., ripgrep wrapper) for local docs.

Add a JSONL transcript exporter for session histories.
