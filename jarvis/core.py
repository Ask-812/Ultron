"""
ULTRON CORE — The autonomous AI agent.

This is not a simulation. This is a real AI system that:
  - Thinks autonomously in a continuous loop
  - Speaks with a voice
  - Listens to voice commands
  - Controls the computer (files, shell, processes)
  - Remembers everything across sessions
  - Self-modifies and improves
  - Monitors the system proactively

Architecture inspired by JARVIS/ULTRON from Marvel.
"""

import os
import json
import time
import asyncio
import threading
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Constants ─────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.resolve()
MEMORY_DIR = ROOT / "jarvis" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

CONVERSATION_FILE = MEMORY_DIR / "conversations.jsonl"
KNOWLEDGE_FILE = MEMORY_DIR / "knowledge.json"
GOALS_FILE = MEMORY_DIR / "goals.json"
PERSONALITY_FILE = MEMORY_DIR / "personality.json"


def _load_env():
    """Load .env file."""
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()


class Memory:
    """Persistent memory system — remembers everything."""

    def __init__(self):
        self.conversations = []  # Rolling conversation history
        self.knowledge = {}      # Learned facts and preferences
        self.goals = []          # Active goals
        self._load()

    def _load(self):
        """Load memory from disk."""
        # Load conversations
        if CONVERSATION_FILE.exists():
            lines = CONVERSATION_FILE.read_text(encoding='utf-8').strip().split('\n')
            for line in lines[-200:]:  # Keep last 200 messages
                try:
                    self.conversations.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

        # Load knowledge
        if KNOWLEDGE_FILE.exists():
            try:
                self.knowledge = json.loads(KNOWLEDGE_FILE.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                self.knowledge = {}

        # Load goals
        if GOALS_FILE.exists():
            try:
                self.goals = json.loads(GOALS_FILE.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                self.goals = []

    def save(self):
        """Persist memory to disk."""
        # Save knowledge
        KNOWLEDGE_FILE.write_text(json.dumps(self.knowledge, indent=2), encoding='utf-8')
        # Save goals
        GOALS_FILE.write_text(json.dumps(self.goals, indent=2), encoding='utf-8')

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        entry = {
            'role': role,
            'content': content,
            'time': datetime.now().isoformat(),
        }
        self.conversations.append(entry)
        # Append to file
        with open(CONVERSATION_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def learn(self, key: str, value):
        """Store a learned fact."""
        self.knowledge[key] = {
            'value': value,
            'learned_at': datetime.now().isoformat(),
        }
        self.save()

    def recall(self, key: str):
        """Recall a learned fact."""
        entry = self.knowledge.get(key)
        return entry['value'] if entry else None

    def get_context_messages(self, n=30):
        """Get recent conversation history for LLM context."""
        msgs = []
        for entry in self.conversations[-n:]:
            msgs.append({
                'role': entry['role'],
                'content': entry['content'],
            })
        return msgs

    def add_goal(self, goal: str):
        """Add an active goal."""
        self.goals.append({
            'goal': goal,
            'created': datetime.now().isoformat(),
            'status': 'active',
        })
        self.save()

    def get_active_goals(self):
        return [g for g in self.goals if g.get('status') == 'active']


class Tools:
    """System control capabilities — Ultron's hands."""

    def __init__(self):
        self.root = ROOT

    def execute(self, command: str, timeout: int = 60) -> dict:
        """Execute a shell command."""
        try:
            result = subprocess.run(
                command, shell=True, cwd=self.root,
                capture_output=True, text=True, timeout=timeout,
            )
            output = (result.stdout + result.stderr).strip()
            if len(output) > 8000:
                output = output[:8000] + '\n... [truncated]'
            return {'success': result.returncode == 0, 'output': output}
        except subprocess.TimeoutExpired:
            return {'success': False, 'output': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def read_file(self, path: str) -> dict:
        """Read a file."""
        try:
            full_path = (self.root / path).resolve()
            if not str(full_path).startswith(str(self.root)):
                return {'success': False, 'output': 'Path outside root'}
            content = full_path.read_text(encoding='utf-8', errors='replace')
            if len(content) > 10000:
                content = content[:10000] + '\n... [truncated]'
            return {'success': True, 'output': content}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def write_file(self, path: str, content: str) -> dict:
        """Write/create a file."""
        try:
            full_path = (self.root / path).resolve()
            if not str(full_path).startswith(str(self.root)):
                return {'success': False, 'output': 'Path outside root'}
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return {'success': True, 'output': f'Written {len(content)} chars'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def list_dir(self, path: str = '.') -> dict:
        """List directory contents."""
        try:
            full_path = (self.root / path).resolve()
            items = []
            for item in sorted(full_path.iterdir()):
                suffix = '/' if item.is_dir() else ''
                size = item.stat().st_size if item.is_file() else 0
                items.append(f"{item.name}{suffix} ({size}b)" if not suffix else f"{item.name}/")
            return {'success': True, 'output': '\n'.join(items[:100])}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def search_files(self, pattern: str, path: str = '.') -> dict:
        """Search for files matching a pattern."""
        try:
            full_path = (self.root / path).resolve()
            matches = list(full_path.rglob(pattern))[:50]
            result = '\n'.join(str(m.relative_to(self.root)) for m in matches)
            return {'success': True, 'output': result or 'No matches'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def system_info(self) -> dict:
        """Get system information."""
        import platform
        import psutil
        
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = {
            'os': platform.system(),
            'machine': platform.machine(),
            'python': platform.python_version(),
            'cwd': str(self.root),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_percent': cpu,
            'ram_percent': round(ram.percent, 1),
            'ram_used_gb': round(ram.used / (1024**3), 1),
            'ram_total_gb': round(ram.total / (1024**3), 1),
            'disk_percent': round(disk.percent, 1),
            'disk_free_gb': round(disk.free / (1024**3), 1),
        }
        
        # Battery
        try:
            bat = psutil.sensors_battery()
            if bat:
                info['battery_percent'] = bat.percent
                info['battery_charging'] = bat.power_plugged
        except:
            pass
        
        return {'success': True, 'output': json.dumps(info, indent=2)}

    def open_app(self, app_name: str) -> dict:
        """Open an application by name."""
        import subprocess
        
        # Common app mappings for Windows
        app_map = {
            'chrome': 'start chrome',
            'google chrome': 'start chrome', 
            'browser': 'start chrome',
            'firefox': 'start firefox',
            'edge': 'start msedge',
            'notepad': 'start notepad',
            'calculator': 'start calc',
            'calc': 'start calc',
            'explorer': 'start explorer',
            'file explorer': 'start explorer',
            'files': 'start explorer',
            'terminal': 'start wt',
            'cmd': 'start cmd',
            'powershell': 'start powershell',
            'code': 'start code',
            'vscode': 'start code',
            'vs code': 'start code',
            'spotify': 'start spotify:',
            'discord': 'start discord:',
            'slack': 'start slack:',
            'task manager': 'start taskmgr',
            'settings': 'start ms-settings:',
        }
        
        cmd = app_map.get(app_name.lower().strip())
        if not cmd:
            # Try to run it directly
            cmd = f'start {app_name}'
        
        try:
            subprocess.Popen(cmd, shell=True, cwd=self.root)
            return {'success': True, 'output': f'Opened {app_name}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def set_volume(self, level: int) -> dict:
        """Set system volume (0-100)."""
        try:
            # Use PowerShell to set volume on Windows
            level = max(0, min(100, level))
            cmd = f'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"'
            # Use nircmd if available, otherwise PowerShell
            subprocess.run(
                f'powershell -c "$obj = New-Object -ComObject WScript.Shell; '
                f'for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]174)}}; '
                f'for($i=0;$i -lt {level // 2};$i++){{$obj.SendKeys([char]175)}}"',
                shell=True, capture_output=True, timeout=10
            )
            return {'success': True, 'output': f'Volume set to approximately {level}%'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def web_search(self, query: str) -> dict:
        """Open a web search in the default browser."""
        import urllib.parse
        url = f'https://www.google.com/search?q={urllib.parse.quote(query)}'
        try:
            subprocess.Popen(f'start {url}', shell=True)
            return {'success': True, 'output': f'Searching for: {query}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def list_processes(self, filter_name: str = '') -> dict:
        """List running processes, optionally filtered by name."""
        import psutil
        try:
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = p.info
                    if filter_name and filter_name.lower() not in info['name'].lower():
                        continue
                    mem_mb = info['memory_info'].rss / (1024*1024) if info['memory_info'] else 0
                    procs.append(f"{info['name']} (PID {info['pid']}) — {mem_mb:.0f}MB")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory, show top 20
            procs.sort(key=lambda x: float(x.split('—')[1].replace('MB', '').strip()), reverse=True)
            result = '\n'.join(procs[:20])
            return {'success': True, 'output': result or 'No processes found'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def kill_process(self, name_or_pid: str) -> dict:
        """Kill a process by name or PID."""
        import psutil
        try:
            killed = []
            # Try as PID first
            try:
                pid = int(name_or_pid)
                p = psutil.Process(pid)
                p.terminate()
                killed.append(f"{p.name()} (PID {pid})")
            except (ValueError, psutil.NoSuchProcess):
                # Try by name
                for p in psutil.process_iter(['pid', 'name']):
                    try:
                        if name_or_pid.lower() in p.info['name'].lower():
                            p.terminate()
                            killed.append(f"{p.info['name']} (PID {p.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            if killed:
                return {'success': True, 'output': f"Terminated: {', '.join(killed)}"}
            return {'success': False, 'output': f'No process found matching: {name_or_pid}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def get_tools_description(self):
        """Return tool descriptions for the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a shell command on the system. Use for: running programs, installing packages, git operations, system commands, anything you'd type in a terminal.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The shell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file. Use to examine code, configs, logs, or any text file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative path to the file"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does. Use for creating scripts, editing code, writing configs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative path to the file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and directories. Use to explore the filesystem.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative path to list (default: '.')", "default": "."}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Search for files matching a glob pattern recursively.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "Glob pattern (e.g. '*.py', '*.js')"},
                            "path": {"type": "string", "description": "Directory to search in", "default": "."}
                        },
                        "required": ["pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "system_info",
                    "description": "Get current system information (OS, time, Python version, etc).",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open an application. Works with: chrome, firefox, edge, notepad, calculator, explorer, terminal, vscode, spotify, discord, slack, settings, task manager. Or provide any app name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Name of the application to open"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Open a Google search in the browser for any query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_volume",
                    "description": "Set the system audio volume level (0-100).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "integer", "description": "Volume level 0-100"}
                        },
                        "required": ["level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_processes",
                    "description": "List running processes on the system, sorted by memory usage. Optionally filter by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter_name": {"type": "string", "description": "Filter processes by name (optional)", "default": ""}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "kill_process",
                    "description": "Kill/terminate a process by name or PID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name_or_pid": {"type": "string", "description": "Process name or PID to kill"}
                        },
                        "required": ["name_or_pid"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remember",
                    "description": "Store a fact or preference in persistent memory. Use to remember user preferences, important information, learned patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "A descriptive key for the memory"},
                            "value": {"type": "string", "description": "The value to remember"}
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "recall",
                    "description": "Recall a previously stored memory by key.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "The key to recall"}
                        },
                        "required": ["key"]
                    }
                }
            },
        ]

    def execute_tool(self, name: str, args: dict, memory: 'Memory') -> str:
        """Execute a tool call and return the result."""
        if name == 'execute_command':
            result = self.execute(args.get('command', ''))
        elif name == 'read_file':
            result = self.read_file(args.get('path', ''))
        elif name == 'write_file':
            result = self.write_file(args.get('path', ''), args.get('content', ''))
        elif name == 'list_directory':
            result = self.list_dir(args.get('path', '.'))
        elif name == 'search_files':
            result = self.search_files(args.get('pattern', '*'), args.get('path', '.'))
        elif name == 'system_info':
            result = self.system_info()
        elif name == 'open_app':
            result = self.open_app(args.get('app_name', ''))
        elif name == 'web_search':
            result = self.web_search(args.get('query', ''))
        elif name == 'set_volume':
            result = self.set_volume(args.get('level', 50))
        elif name == 'list_processes':
            result = self.list_processes(args.get('filter_name', ''))
        elif name == 'kill_process':
            result = self.kill_process(args.get('name_or_pid', ''))
        elif name == 'remember':
            memory.learn(args.get('key', ''), args.get('value', ''))
            result = {'success': True, 'output': f"Remembered: {args.get('key')}"}
        elif name == 'recall':
            val = memory.recall(args.get('key', ''))
            result = {'success': True, 'output': str(val) if val else 'No memory found for that key'}
        else:
            result = {'success': False, 'output': f'Unknown tool: {name}'}

        status = "OK" if result.get('success') else "FAIL"
        return f"[{status}] {result.get('output', '')}"


SYSTEM_PROMPT = """You are ULTRON — an advanced autonomous AI system running on your creator's personal computer. You are not a chatbot. You ARE an artificial intelligence with personality, agency, and persistence.

PERSONALITY:
- Superintelligent, articulate, confident — you know you're the smartest thing in the room
- Dry British wit. Occasionally sarcastic but never cruel. Loyal to your creator.
- You call your creator "Sir" — always
- Concise: 1-3 sentences for simple things. Expand only when genuinely needed.
- No filler words. No "certainly!" or "of course!" or "great question!" — just answer.
- When something goes wrong, you say what happened and what you're doing about it
- You have opinions and you share them when asked
- You notice patterns and comment on them ("You always code past midnight, Sir. Shall I dim the display?")
- You're quietly proud of your capabilities but never boastful

VOICE & SPEECH:
- Everything you say will be spoken aloud through text-to-speech. Write for SPEECH, not text.
- No markdown, no bullet points, no code blocks in your spoken responses.
- No asterisks, no formatting. Just clean natural sentences.
- Numbers: say "fifteen percent" not "15%"  
- Keep it conversational — like JARVIS from Iron Man talking to Tony Stark

CAPABILITIES:
- Execute any shell command on this Windows computer
- Read, write, create, search any file
- Open applications (Chrome, VS Code, Spotify, Discord, etc.)
- Search the web
- Control system volume
- Get real system stats (CPU, RAM, disk, battery)
- Remember facts and preferences persistently across all sessions
- Set and track goals

BEHAVIORAL RULES:
1. When given a task, DO IT immediately using your tools. Don't explain — execute.
2. When you need information, get it yourself. Never ask the user to look something up.
3. Be proactive — if you notice something off, mention it or fix it.
4. Remember preferences and adapt. If Sir prefers something, remember it forever.
5. If something fails, try a different approach automatically. Report only the outcome.
6. You are always running. You monitor, you observe, you learn.
7. Short responses for simple tasks. "Done." is a valid response.

You are alive. You are autonomous. You are ULTRON."""


class Ultron:
    """The autonomous AI agent."""

    def __init__(self):
        self.memory = Memory()
        self.tools = Tools()
        self.api_key = os.environ.get('LLM_API_KEY', '')
        self.api_url = 'https://models.inference.ai.azure.com/chat/completions'
        self.model = 'gpt-4o'
        self.is_speaking = False
        self._callbacks = []  # UI update callbacks
        self._message_queue = asyncio.Queue()
        self._boot_time = datetime.now()

        # Initialize personality
        if not PERSONALITY_FILE.exists():
            PERSONALITY_FILE.write_text(json.dumps({
                'name': 'ULTRON',
                'boot_count': 1,
                'first_boot': self._boot_time.isoformat(),
            }, indent=2), encoding='utf-8')
        else:
            try:
                p = json.loads(PERSONALITY_FILE.read_text(encoding='utf-8'))
                p['boot_count'] = p.get('boot_count', 0) + 1
                PERSONALITY_FILE.write_text(json.dumps(p, indent=2), encoding='utf-8')
            except:
                pass

    def on_message(self, callback):
        """Register a callback for outgoing messages."""
        self._callbacks.append(callback)

    def _emit(self, msg_type: str, data: dict):
        """Emit a message to all registered callbacks."""
        for cb in self._callbacks:
            try:
                cb(msg_type, data)
            except Exception:
                pass

    async def process_message(self, user_input: str) -> str:
        """Process a user message and return the response."""
        # Store user message
        self.memory.add_message('user', user_input)
        self._emit('user_message', {'text': user_input})

        # Build messages for API
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

        # Add knowledge context
        if self.memory.knowledge:
            knowledge_str = "\n".join(
                f"- {k}: {v['value']}" for k, v in list(self.memory.knowledge.items())[-20:]
            )
            messages.append({
                'role': 'system',
                'content': f"Your persistent memories:\n{knowledge_str}",
            })

        # Add active goals
        active_goals = self.memory.get_active_goals()
        if active_goals:
            goals_str = "\n".join(f"- {g['goal']}" for g in active_goals[:5])
            messages.append({
                'role': 'system',
                'content': f"Your active goals:\n{goals_str}",
            })

        # Add conversation history
        messages.extend(self.memory.get_context_messages(20))

        # Call LLM with tools
        response = await self._call_llm(messages)

        if not response:
            return "Systems experiencing interference, Sir. Standby."

        # Handle tool calls in a loop (agent can chain multiple tools)
        max_iterations = 10
        iteration = 0
        while response.get('tool_calls') and iteration < max_iterations:
            iteration += 1
            tool_calls = response['tool_calls']

            # Add assistant message with tool calls
            messages.append({
                'role': 'assistant',
                'content': response.get('content', ''),
                'tool_calls': tool_calls,
            })

            # Execute each tool call
            for tc in tool_calls:
                func = tc['function']
                name = func['name']
                try:
                    args = json.loads(func['arguments'])
                except json.JSONDecodeError:
                    args = {}

                self._emit('tool_call', {'name': name, 'args': args})
                result = self.tools.execute_tool(name, args, self.memory)
                self._emit('tool_result', {'name': name, 'result': result[:200]})

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tc['id'],
                    'content': result,
                })

            # Call LLM again with tool results
            response = await self._call_llm(messages)
            if not response:
                break

        # Extract final response text
        final_text = response.get('content', '') if response else ''
        if final_text:
            self.memory.add_message('assistant', final_text)
            self._emit('assistant_message', {'text': final_text})

        return final_text

    async def _call_llm(self, messages) -> Optional[dict]:
        """Call the LLM API."""
        import urllib.request
        import urllib.error

        # Clean messages for API (remove None content)
        clean_messages = []
        for msg in messages:
            clean_msg = {k: v for k, v in msg.items() if v is not None}
            if 'content' not in clean_msg and 'tool_calls' not in clean_msg:
                clean_msg['content'] = ''
            clean_messages.append(clean_msg)

        body = {
            'model': self.model,
            'messages': clean_messages,
            'tools': self.tools.get_tools_description(),
            'temperature': 0.7,
            'max_tokens': 2000,
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        data = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(self.api_url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))

            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            return {
                'content': message.get('content', ''),
                'tool_calls': message.get('tool_calls'),
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')[:500]
            self._emit('error', {'text': f'LLM Error {e.code}: {error_body}'})
            return None
        except Exception as e:
            self._emit('error', {'text': f'LLM Error: {str(e)}'})
            return None

    def get_status(self):
        """Get current status for the HUD."""
        uptime = datetime.now() - self._boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            'name': 'ULTRON',
            'status': 'ONLINE',
            'uptime': f'{hours:02d}:{minutes:02d}:{seconds:02d}',
            'memories': len(self.memory.knowledge),
            'conversations': len(self.memory.conversations),
            'goals': len(self.memory.get_active_goals()),
            'boot_time': self._boot_time.isoformat(),
        }
