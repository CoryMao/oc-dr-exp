# OpenClaw Profile Audit

profile: pre-arxiv-c1-r1-off
timestamp_utc: 2026-06-04T12:01:17Z

## Version
OpenClaw 2026.5.28 (e932160)

## Config File
~/.openclaw-pre-arxiv-c1-r1-off/openclaw.json

## Config Validate
Config valid: ~/.openclaw-pre-arxiv-c1-r1-off/openclaw.json

## MCP List
No MCP servers configured in /Users/kaichengmao/.openclaw-pre-arxiv-c1-r1-off/openclaw.json. Add one with openclaw --profile pre-arxiv-c1-r1-off mcp set <name> '{"command":"uvx","args":["context7-mcp"]}'.

## MCP Show
MCP servers (/Users/kaichengmao/.openclaw-pre-arxiv-c1-r1-off/openclaw.json):
{}

## Skills Entries
{
  "apple-reminders": {
    "enabled": false
  },
  "bear-notes": {
    "enabled": false
  },
  "camsnap": {
    "enabled": false
  },
  "canvas": {
    "enabled": false
  },
  "diagram-maker": {
    "enabled": false
  },
  "discord": {
    "enabled": false
  },
  "eightctl": {
    "enabled": false
  },
  "gemini": {
    "enabled": false
  },
  "gh-issues": {
    "enabled": false
  },
  "gifgrep": {
    "enabled": false
  },
  "github": {
    "enabled": false
  },
  "weather": {
    "enabled": false
  },
  "voice-call": {
    "enabled": false
  },
  "video-frames": {
    "enabled": false
  },
  "wacli": {
    "enabled": false
  },
  "trello": {
    "enabled": false
  },
  "things-mac": {
    "enabled": false
  },
  "gog": {
    "enabled": false
  },
  "goplaces": {
    "enabled": false
  },
  "model-usage": {
    "enabled": false
  },
  "meme-maker": {
    "enabled": false
  },
  "imsg": {
    "enabled": false
  },
  "himalaya": {
    "enabled": false
  },
  "notion": {
    "enabled": false
  },
  "obsidian": {
    "enabled": false
  },
  "openai-whisper": {
    "enabled": false
  },
  "openai-whisper-api": {
    "enabled": false
  },
  "openhue": {
    "enabled": false
  },
  "oracle": {
    "enabled": false
  },
  "ordercli": {
    "enabled": false
  },
  "peekaboo": {
    "enabled": false
  },
  "sag": {
    "enabled": false
  },
  "sherpa-onnx-tts": {
    "enabled": false
  },
  "sonoscli": {
    "enabled": false
  },
  "songsee": {
    "enabled": false
  },
  "slack": {
    "enabled": false
  },
  "spike": {
    "enabled": false
  },
  "spotify-player": {
    "enabled": false
  },
  "xurl": {
    "enabled": false
  },
  "obsidian-vault-maintainer": {
    "enabled": false
  },
  "blucli": {
    "enabled": false
  },
  "blogwatcher": {
    "enabled": false
  },
  "1password": {
    "enabled": false
  },
  "clawhub": {
    "enabled": false
  },
  "coding-agent": {
    "enabled": false
  },
  "mcporter": {
    "enabled": false
  },
  "pdf": {
    "enabled": true
  },
  "self-improvement": {
    "enabled": false
  },
  "summarize": {
    "enabled": false
  },
  "skill-creator": {
    "enabled": false
  },
  "session-logs": {
    "enabled": false
  },
  "python-debugpy": {
    "enabled": false
  },
  "node-inspect-debugger": {
    "enabled": false
  },
  "node-connect": {
    "enabled": false
  },
  "nano-pdf": {
    "enabled": false
  },
  "apple-notes": {
    "enabled": false
  },
  "browser-automation": {
    "enabled": false
  },
  "qqbot-channel": {
    "enabled": false
  },
  "wiki-maintainer": {
    "enabled": false
  },
  "qqbot-remind": {
    "enabled": false
  },
  "qqbot-media": {
    "enabled": false
  },
  "taskflow": {
    "enabled": false
  },
  "taskflow-inbox-triage": {
    "enabled": false
  },
  "citation-standard": {
    "enabled": true
  }
}

## Skills List
Skills (3/59 ready)
┌──────────┬──────────────────────────┬─────────────────────────────────────────────────────────────┬──────────────────┐
│ Status   │ Skill                    │ Description                                                 │ Source           │
├──────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────────────┤
│ disabled │ 🔐 1password             │ Set up and use 1Password CLI for sign-in, desktop           │ openclaw-bundled │
│          │                          │ integration, and reading or injecting secrets.              │                  │
│ disabled │ 📝 apple-notes           │ Create, view, edit, delete, search, move, or export Apple   │ openclaw-bundled │
│          │                          │ Notes via the memo CLI on macOS.                            │                  │
│ disabled │ ⏰ apple-reminders       │ List, add, edit, complete, or delete Apple Reminders and    │ openclaw-bundled │
│          │                          │ reminder lists via remindctl.                               │                  │
│ disabled │ 🐻 bear-notes            │ Create, search, and manage Bear notes via grizzly CLI.      │ openclaw-bundled │
│ disabled │ 📰 blogwatcher           │ Monitor blogs and RSS/Atom feeds for updates using the      │ openclaw-bundled │
│          │                          │ blogwatcher CLI.                                            │                  │
│ disabled │ 🫐 blucli                │ BluOS CLI (blu) for discovery, playback, grouping, and      │ openclaw-bundled │
│          │                          │ volume.                                                     │                  │
│ disabled │ browser-automation       │ Use when controlling web pages with the OpenClaw browser    │ openclaw-extra   │
│          │                          │ tool, especially multi-step flows, login checks, tab        │                  │
│          │                          │ management, or recovery from stale refs/timeouts.           │                  │
│ disabled │ 📸 camsnap               │ Capture frames or clips from RTSP/ONVIF cameras.            │ openclaw-bundled │
│ disabled │ 🖼️ canvas                │ Present HTML on connected OpenClaw node canvases, navigate/ │ openclaw-bundled │
│          │                          │ eval/snapshot, and debug canvas host URLs.                  │                  │
│ ✓ ready  │ 📌 citation-standard     │ Enforce standardized citation position format in research   │ openclaw-managed │
│          │                          │ reports. Every claim must cite source tag + precise         │                  │
│          │                          │ structural location using a fixed grammar with closed       │                  │
│          │                          │ vocabularies.                                               │                  │
│ disabled │ clawhub                  │ Search, install, update, sync, or publish agent skills      │ openclaw-bundled │
│          │                          │ with the ClawHub CLI and registry.                          │                  │
│ disabled │ 🧩 coding-agent          │ Delegate coding work to Codex, Claude Code, or OpenCode as  │ openclaw-bundled │
│          │                          │ background workers; not simple edits or read-only code      │                  │
│          │                          │ lookup.                                                     │                  │
│ disabled │ 🧭 diagram-maker         │ Create SVG/HTML or Excalidraw diagrams for concepts,        │ openclaw-bundled │
│          │                          │ architecture, flows, and whiteboards.                       │                  │
│ disabled │ 🎮 discord               │ Discord message-tool ops: send/read/edit/delete, react,     │ openclaw-bundled │
│          │                          │ poll, pin, thread, search, presence, media/components.      │                  │
│ disabled │ 🛌 eightctl              │ Control Eight Sleep pods (status, temperature, alarms,      │ openclaw-bundled │
│          │                          │ schedules).                                                 │                  │
│ disabled │ ✨ gemini                │ Gemini CLI one-shot prompts, summaries, generation,         │ openclaw-bundled │
│          │                          │ skills, hooks, MCP, or Gemma routing.                       │                  │
│ disabled │ gh-issues                │ Fetch GitHub issues, select candidates, spawn background    │ openclaw-bundled │
│          │                          │ fix agents, open PRs, and optionally process PR review      │                  │
│          │                          │ comments.                                                   │                  │
│ disabled │ 🧲 gifgrep               │ Search GIF providers with CLI/TUI, download results, and    │ openclaw-bundled │
│          │                          │ extract stills/sheets.                                      │                  │
│ disabled │ 🐙 github                │ GitHub CLI for issues, PRs, CI/check logs, comments,        │ openclaw-bundled │
│          │                          │ reviews, releases, repos, and gh api queries.               │                  │
│ disabled │ 🎮 gog                   │ Google Workspace CLI for Gmail, Calendar, Drive, Contacts,  │ openclaw-bundled │
│          │                          │ Sheets, and Docs.                                           │                  │
│ disabled │ 📍 goplaces              │ Query Google Places for text search, place details,         │ openclaw-bundled │
│          │                          │ resolve, reviews, or scriptable JSON via goplaces.          │                  │
│ ✓ ready  │ healthcheck              │ Audit/harden OpenClaw hosts: SSH, firewall, updates,        │ openclaw-bundled │
│          │                          │ exposure, backups, disk encryption, gateway security.       │                  │
│ disabled │ 📧 himalaya              │ Himalaya CLI for IMAP/SMTP mail: list, read, search,        │ openclaw-bundled │
│          │                          │ compose, reply, forward, copy, move, delete.                │                  │
│ disabled │ 📨 imsg                  │ iMessage/SMS CLI for listing chats, history, and sending    │ openclaw-bundled │
│          │                          │ messages via Messages.app.                                  │                  │
│ disabled │ 📦 mcporter              │ List, configure, authenticate, call, and inspect MCP        │ openclaw-bundled │
│          │                          │ servers/tools with mcporter over HTTP or stdio.             │                  │
│ disabled │ 🖼️ meme-maker            │ Search meme templates, suggest formats, and generate local  │ openclaw-bundled │
│          │                          │ or hosted image memes.                                      │                  │
│ disabled │ 📊 model-usage           │ Summarize CodexBar local cost logs by model for Codex or    │ openclaw-bundled │
│          │                          │ Claude, including current or full breakdowns.               │                  │
│ disabled │ 📄 nano-pdf              │ Edit PDFs with natural-language instructions using the      │ openclaw-bundled │
│          │                          │ nano-pdf CLI.                                               │                  │
│ disabled │ node-connect             │ Diagnose OpenClaw Android, iOS, or macOS node pairing, QR/  │ openclaw-bundled │
│          │                          │ setup code, route, auth, and connection failures.           │                  │
│ disabled │ 🪲 node-inspect-debugger │ Debug Node.js with node inspect, --inspect, breakpoints,    │ openclaw-bundled │
│          │                          │ CDP, heap, and CPU profiles.                                │                  │
│ disabled │ 📝 notion                │ Notion CLI/API for pages, Markdown content, data sources,   │ openclaw-bundled │
│          │                          │ files, comments, search, Workers, and raw API calls.        │                  │
│ disabled │ 💎 obsidian              │ Work with Obsidian vaults using the official obsidian CLI:  │ openclaw-bundled │
│          │                          │ read/search/create/edit notes, tasks, links, properties,    │                  │
│          │                          │ plugins.                                                    │                  │
│ disabled │ 🎤 openai-whisper        │ Local speech-to-text with the Whisper CLI (no API key).     │ openclaw-bundled │
│ disabled │ 🌐 openai-whisper-api    │ OpenAI Audio Transcriptions API via curl; gpt-4o-           │ openclaw-bundled │
│          │                          │ transcribe, mini, diarize, or whisper-1.                    │                  │
│ disabled │ 💡 openhue               │ Control Philips Hue lights and scenes via the OpenHue CLI.  │ openclaw-bundled │
│ disabled │ 🧿 oracle                │ Oracle CLI second-model review/debug/refactor/design with   │ openclaw-bundled │
│          │                          │ selected files, dry-run token checks, API or browser        │                  │
│          │                          │ engine.                                                     │                  │
│ disabled │ 🛵 ordercli              │ Foodora-only CLI for checking past orders and active order  │ openclaw-bundled │
│          │                          │ status (Deliveroo WIP).                                     │                  │
│ disabled │ 👀 peekaboo              │ Capture and automate macOS UI with the Peekaboo CLI.        │ openclaw-bundled │
│ disabled │ python-debugpy           │ Debug Python with pdb, breakpoint(), post-mortem            │ openclaw-bundled │
│          │                          │ inspection, and debugpy remote attach.                      │                  │
│ disabled │ 🔊 sag                   │ ElevenLabs text-to-speech with mac-style say UX.            │ openclaw-bundled │
│ disabled │ 📜 session-logs          │ Search and analyze your own session logs (older/parent      │ openclaw-bundled │
│          │                          │ conversations) using jq.                                    │                  │
│ disabled │ 🔉 sherpa-onnx-tts       │ Local text-to-speech via sherpa-onnx (offline, no cloud)    │ openclaw-bundled │
│ disabled │ skill-creator            │ Create, edit, audit, tidy, validate, or restructure         │ openclaw-bundled │
│          │                          │ AgentSkills and SKILL.md files.                             │                  │
│ disabled │ 💬 slack                 │ Slack tool actions: send/read/edit/delete messages, react,  │ openclaw-bundled │
│          │                          │ pin/unpin, list pins/reactions/emoji, member info.          │                  │
│ disabled │ 🌊 songsee               │ Generate spectrograms and feature-panel visualizations      │ openclaw-bundled │
│          │                          │ from audio with the songsee CLI.                            │                  │
│ disabled │ 🔊 sonoscli              │ Control Sonos speakers (discover/status/play/volume/group). │ openclaw-bundled │
│ disabled │ 🧪 spike                 │ Run throwaway prototypes to validate feasibility, compare   │ openclaw-bundled │
│          │                          │ approaches, and report a verdict.                           │                  │
│ disabled │ 🎵 spotify-player        │ Terminal Spotify playback/search via spogo (preferred) or   │ openclaw-bundled │
│          │                          │ spotify_player.                                             │                  │
│ disabled │ 🧾 summarize             │ Summarize or transcribe URLs, YouTube/videos, podcasts,     │ openclaw-bundled │
│          │                          │ articles, transcripts, PDFs, and local files.               │                  │
│ disabled │ 🪝 taskflow              │ Coordinate multi-step detached tasks as one durable         │ openclaw-bundled │
│          │                          │ TaskFlow job with owner context, state, waits, and child    │                  │
│          │                          │ tasks.                                                      │                  │
│ disabled │ 📥 taskflow-inbox-triage │ Example TaskFlow pattern for inbox triage, intent routing,  │ openclaw-bundled │
│          │                          │ waiting on replies, and later summaries.                    │                  │
│ disabled │ ✅ things-mac            │ Add, update, list, search, or inspect Things 3 todos,       │ openclaw-bundled │
│          │                          │ inbox, today, projects, areas, and tags on macOS.           │                  │
│ ✓ ready  │ 🧵 tmux                  │ Control tmux sessions/panes for interactive CLIs: list,     │ openclaw-bundled │
│          │                          │ capture output, send keys, paste text, monitor prompts.     │                  │
│ disabled │ 📋 trello                │ Manage Trello boards, lists, and cards via the Trello REST  │ openclaw-bundled │
│          │                          │ API.                                                        │                  │
│ disabled │ 🎬 video-frames          │ Extract frames or short clips from videos using ffmpeg.     │ openclaw-bundled │
│ disabled │ 📞 voice-call            │ Start voice calls via the OpenClaw voice-call plugin.       │ openclaw-bundled │
│ disabled │ 📱 wacli                 │ Send third-party WhatsApp messages or sync/search WhatsApp  │ openclaw-bundled │
│          │                          │ history via wacli, not normal active chats.                 │                  │
│ disabled │ ☔ weather               │ Current weather and forecasts with wttr.in via curl for     │ openclaw-bundled │
│          │                          │ locations, rain, temperature, travel planning.              │                  │
│ disabled │ 🐦 xurl                  │ xurl CLI for authenticated X posts, replies, reads/search,  │ openclaw-bundled │
│          │                          │ DMs, media upload, followers, auth status, or raw v2 API    │                  │
│          │                          │ calls.                                                      │                  │
└──────────┴──────────────────────────┴─────────────────────────────────────────────────────────────┴──────────────────┘

Tip: use `openclaw skills search`, `openclaw skills install`, and `openclaw skills update` for ClawHub-backed skills.

## Skills Check
Skills Status Check
Agent: main

Total: 59
✓ Eligible: 3
✓ Visible to model: 3
✓ Available as command: 3
Disabled: 56
Blocked by allowlist: 0
Excluded by agent allowlist: 0
✗ Missing requirements: 0

What this means:
  Eligible: installed and requirements pass; the agent may still exclude it.
  Visible to model: the agent can see the skill instructions during normal chat.
  Available as command: people, scripts, or cron jobs can call the skill explicitly.

Ready and visible to model:
  📌 citation-standard
  healthcheck
  🧵 tmux

Tip: use `openclaw skills search`, `openclaw skills install`, and `openclaw skills update` for ClawHub-backed skills.
