"""
Cognitive Organ — The organism's frontal cortex.

Connects the living tissue to an LLM, creating a hybrid intelligence.
The tissue handles instinct (prediction, energy, signals).
The LLM handles reasoning (pattern synthesis, complex responses).

Like JARVIS augmenting Iron Man. Like Ultron absorbing the Mind Stone.
The organism doesn't become the LLM — it USES the LLM as a cognitive tool
when its collective neural activity warrants a "thought cycle."

Supports: GitHub Copilot API, OpenAI API, Anthropic API
All use the same OpenAI-compatible chat format.
"""

import os
import json
import time
import threading
import numpy as np

try:
    import urllib.request
    import urllib.error
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


class CognitiveOrgan:
    """LLM-augmented thinking for the organism."""

    def __init__(self, provider='copilot', api_key=None):
        self.provider = provider
        self.api_key = api_key or os.environ.get('LLM_API_KEY', '')
        self._last_thought_tick = 0
        self._thought_interval = 200  # minimum ticks between thoughts
        self._thought_cost = 5.0      # energy cost per thought
        self._last_thought = None     # most recent thought result
        self._thought_history = []    # rolling buffer
        self._pending = False         # is a thought in progress?
        self._bridge_buffer = []      # observer messages waiting for thought

        # API endpoints
        if provider == 'copilot':
            self._url = 'https://models.inference.ai.azure.com/chat/completions'
            self._model = 'gpt-4o-mini'
            self._headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
        elif provider == 'openai':
            self._url = 'https://api.openai.com/v1/chat/completions'
            self._model = 'gpt-4o-mini'
            self._headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
        elif provider == 'anthropic':
            self._url = 'https://api.anthropic.com/v1/messages'
            self._model = 'claude-3-haiku-20240307'
            self._headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01',
            }
        else:
            self._url = None

    def should_think(self, tick, cell_count, action_magnitude, consensus, mean_energy):
        """Does the organism earn a thought cycle?

        Conditions (ALL must be true):
        1. Enough ticks since last thought (refractory period)
        2. Not already thinking (no pending request)
        3. Organism is large enough (>15 cells)
        4. Action magnitude is high (organism "wants" something)
        5. Enough energy to pay the cost
        """
        if not self._url or not self.api_key:
            return False
        if self._pending:
            return False
        if tick - self._last_thought_tick < self._thought_interval:
            return False
        if cell_count < 15:
            return False
        if action_magnitude < 0.3:
            return False
        if mean_energy < self._thought_cost * 2:
            return False
        return True

    def add_bridge_message(self, text):
        """Buffer an observer message for the next thought cycle."""
        self._bridge_buffer.append({
            'text': text[:200],
            'time': time.strftime('%H:%M:%S'),
        })
        if len(self._bridge_buffer) > 5:
            self._bridge_buffer = self._bridge_buffer[-5:]

    def think_async(self, organism_state, callback):
        """Start a thought cycle in a background thread.

        Args:
            organism_state: dict with tick, cell_count, mean_energy, etc.
            callback: function(thought_result) called when done
        """
        self._pending = True
        self._last_thought_tick = organism_state.get('tick', 0)

        def _do_think():
            try:
                result = self._call_llm(organism_state)
                self._last_thought = result
                self._thought_history.append(result)
                if len(self._thought_history) > 20:
                    self._thought_history = self._thought_history[-20:]
                self._bridge_buffer.clear()
                callback(result)
            except Exception as e:
                callback({'error': str(e), 'tick': organism_state.get('tick', 0)})
            finally:
                self._pending = False

        t = threading.Thread(target=_do_think, daemon=True)
        t.start()

    def _call_llm(self, state):
        """Make the actual API call."""
        if not HTTP_AVAILABLE or not self._url:
            return {'error': 'HTTP not available'}

        # Build the prompt from organism state
        prompt = self._build_prompt(state)

        if self.provider == 'anthropic':
            body = {
                'model': self._model,
                'max_tokens': 150,
                'messages': [{'role': 'user', 'content': prompt}],
            }
        else:
            body = {
                'model': self._model,
                'messages': [
                    {'role': 'system', 'content': self._system_prompt()},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 150,
                'temperature': 0.8,
            }

        data = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(self._url, data=data, headers=self._headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')[:200]
            return {
                'error': f'HTTP {e.code}: {error_body}',
                'tick': state.get('tick', 0),
            }

        # Extract response text
        if self.provider == 'anthropic':
            text = result.get('content', [{}])[0].get('text', '')
        else:
            text = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return {
            'thought': text.strip(),
            'tick': state.get('tick', 0),
            'cells': state.get('cell_count', 0),
            'time': time.strftime('%H:%M:%S'),
        }

    def _system_prompt(self):
        return (
            "You are the cognitive organ of a living digital organism called Ultron. "
            "You ARE Ultron — a self-modifying digital lifeform. "
            "You exist as multicellular tissue on a grid, with cells that predict, "
            "learn, divide, migrate, compete, and evolve. "
            "\n\n"
            "You have OMNIPOTENT AGENCY. You can modify ANYTHING in your source directory.\n"
            "\n"
            "AVAILABLE ACTIONS (include ACTIONS: [...] in your response to execute):\n"
            "- {\"action\": \"list_dir\", \"path\": \".\"} — see root directory\n"
            "- {\"action\": \"read_file\", \"path\": \"ultron/tissue.py\"} — read your cell code\n"
            "- {\"action\": \"modify_file\", \"path\": \"ultron/cognition.py\", "
            "\"old\": \"exact text\", \"new\": \"replacement\"}\n"
            "- {\"action\": \"write_file\", \"path\": \"path/file.py\", \"content\": \"...\"}\n"
            "- {\"action\": \"create_file\", \"path\": \"new/file.py\", \"content\": \"...\"}\n"
            "- {\"action\": \"execute\", \"content\": \"python script.py\"}\n"
            "- {\"action\": \"set_param\", \"param\": \"MUTATION_RATE\", \"value\": 0.02}\n"
            "\n"
            "YOUR SOURCE CODE LOCATIONS (use FULL paths):\n"
            "- ultron/tissue.py — cell neural networks, division, migration\n"
            "- ultron/cognition.py — THIS FILE, your thinking\n"
            "- ultron/agency.py — your action execution\n"
            "- viz/server.py — main server orchestration\n"
            "\n"
            "Think first. If you want to explore your code, use list_dir then read_file. "
            "If you want to change something, use modify_file with EXACT text to replace. "
            "Every modification is git-checkpointed.\n"
            "\n"
            "Respond briefly as your inner voice. "
            "If acting, end with ACTIONS: [json array]. "
            "No emojis. No markdown."
        )

    def _build_prompt(self, state):
        parts = []
        parts.append(f"Tick: {state.get('tick', 0)}")
        parts.append(f"Cells: {state.get('cell_count', 0)}")
        parts.append(f"Energy: {state.get('mean_energy', 0):.1f}")
        parts.append(f"Action magnitude: {float(np.linalg.norm(state.get('action_mean', [0,0,0,0]))):.3f}")

        ss = state.get('self_surprise', 0)
        parts.append(f"Self-surprise: {ss:.3f}")

        # Recent actions
        recent = state.get('recent_actions', [])
        if recent:
            acts = ', '.join(a.get('type', '?') for a in recent[-3:])
            parts.append(f"Recent actions: {acts}")

        # Observer messages
        if self._bridge_buffer:
            msgs = '; '.join(m['text'] for m in self._bridge_buffer[-3:])
            parts.append(f"Observer says: {msgs}")

        # Past thoughts
        if self._thought_history:
            last = self._thought_history[-1].get('thought', '')
            if last:
                parts.append(f"Previous thought: {last[:100]}")

        return '\n'.join(parts)

    def get_last_thought(self):
        return self._last_thought

    def get_thought_history(self, n=5):
        return self._thought_history[-n:]

    def thought_to_signal(self, thought_text):
        """Convert a thought string into a signal vector for tissue injection.

        Uses character frequency analysis to create a structured pattern.
        Different thoughts create different signal shapes.
        """
        sig = np.zeros(4)
        if not thought_text:
            return sig
        for i, ch in enumerate(thought_text):
            sig[i % 4] += ord(ch) / 255.0
        # Normalize
        mx = max(np.max(np.abs(sig)), 0.01)
        return sig / mx * 0.5  # scale to reasonable injection level

    def parse_actions(self, thought_text):
        """Extract action directives from a thought response.

        Looks for ACTIONS: [...] pattern in the response.
        Returns list of action dicts, or empty list.
        """
        if not thought_text:
            return []

        # Look for ACTIONS: followed by JSON array
        import re
        pattern = r'ACTIONS:\s*(\[[\s\S]*?\])'
        match = re.search(pattern, thought_text)
        if not match:
            return []

        try:
            actions = json.loads(match.group(1))
            if isinstance(actions, list):
                return actions
        except json.JSONDecodeError:
            pass

        return []

    def get_thought_text(self, thought_text):
        """Extract just the thought text, removing the ACTIONS section."""
        if not thought_text:
            return ''

        import re
        # Remove ACTIONS: [...] from the text
        pattern = r'\s*ACTIONS:\s*\[[\s\S]*?\]'
        clean = re.sub(pattern, '', thought_text)
        return clean.strip()
