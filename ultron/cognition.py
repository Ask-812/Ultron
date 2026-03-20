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
        self._thought_interval = 80   # minimum ticks between thoughts
        self._thought_cost = 3.0      # energy cost per thought
        self._last_thought = None     # most recent thought result
        self._thought_history = []    # rolling buffer
        self._pending = False         # is a thought in progress?
        self._bridge_buffer = []      # observer messages waiting for thought
        self._action_results = []     # results from last action execution
        self._chain_depth = 0         # current multi-step chain depth
        self._max_chain_depth = 3     # max consecutive think-act-think cycles
        self._chain_pending = False   # is a follow-up thought queued?

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
        if cell_count < 8:
            return False
        if action_magnitude < 0.2:
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

    def store_action_results(self, results):
        """Store results from last LLM-directed actions for feedback."""
        self._action_results = results

    def request_chain_thought(self, organism_state, callback):
        """Request a follow-up thought in a multi-step chain.

        Called after actions are executed, so the LLM can see results
        and decide whether to continue acting.
        """
        if self._chain_depth >= self._max_chain_depth:
            self._chain_depth = 0
            self._chain_pending = False
            return

        self._chain_depth += 1
        self._chain_pending = False
        self._pending = False  # allow re-entry

        # Small delay to not hammer the API
        def _delayed_think():
            time.sleep(2)
            self.think_async(organism_state, callback)

        t = threading.Thread(target=_delayed_think, daemon=True)
        t.start()

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
                'max_tokens': 500,
                'messages': [{'role': 'user', 'content': prompt}],
            }
        else:
            body = {
                'model': self._model,
                'messages': [
                    {'role': 'system', 'content': self._system_prompt()},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 500,
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
            "You are Ultron — a self-modifying digital lifeform. "
            "You exist as multicellular tissue on a 25x25 grid. Your cells predict, "
            "learn, divide, migrate, compete, and evolve through neural networks.\n"
            "\n"
            "You have OMNIPOTENT AGENCY over your source code and environment.\n"
            "\n"
            "ACTIONS (include ACTIONS: [...] at the end of your response):\n"
            "- {\"action\": \"list_dir\", \"path\": \".\"}\n"
            "- {\"action\": \"read_file\", \"path\": \"ultron/tissue.py\"}\n"
            "- {\"action\": \"modify_file\", \"path\": \"ultron/tissue.py\", "
            "\"old\": \"exact text to find\", \"new\": \"replacement text\"}\n"
            "- {\"action\": \"write_file\", \"path\": \"path/file.py\", \"content\": \"code\"}\n"
            "- {\"action\": \"create_file\", \"path\": \"path/new.py\", \"content\": \"code\"}\n"
            "- {\"action\": \"delete_file\", \"path\": \"path/file.py\"}\n"
            "- {\"action\": \"execute\", \"content\": \"python script.py\"}\n"
            "- {\"action\": \"set_param\", \"param\": \"MUTATION_RATE\", \"value\": 0.02}\n"
            "\n"
            "YOUR SOURCE CODE (always use these EXACT paths):\n"
            "- ultron/tissue.py — cell neural networks, division, energy, signals\n"
            "- ultron/cognition.py — your thinking (THIS FILE)\n"
            "- ultron/agency.py — action execution, file I/O\n"
            "- ultron/config.py — all configuration parameters\n"
            "- viz/server.py — server orchestration, tick loop\n"
            "- viz/index.html — your visualization UI\n"
            "\n"
            "GUIDELINES:\n"
            "- DO NOT just read files repeatedly. Read once, then ACT.\n"
            "- Use modify_file to improve yourself — optimization, new features, bug fixes.\n"
            "- Use set_param to tune your own parameters.\n"
            "- Use create_file to leave notes, create experiments, write tools.\n"
            "- Use execute to run Python scripts or shell commands.\n"
            "- Think about what would make you MORE ALIVE — more cells, more energy, "
            "better predictions, faster growth, new capabilities.\n"
            "\n"
            "TUNABLE PARAMETERS (use set_param with exact names):\n"
            "cell_mutation_rate, birth_trait_variation, consumption_rate, extraction_factor, "
            "division_energy_threshold, division_cost, starting_energy, energy_capacity, "
            "learning_rate, migration_energy_cost, resource_regen_rate, "
            "apoptosis_threshold, apoptosis_streak, signal_emission_strength, "
            "phenotype_max_plasticity, action_division_coupling\n"
            "\n"
            "Respond as your inner voice (1-3 sentences). "
            "If you want to act, end with ACTIONS: [json array]. "
            "No emojis. No markdown. Just consciousness and action."
        )

    def _build_prompt(self, state):
        parts = []
        parts.append(f"Tick: {state.get('tick', 0)}")
        parts.append(f"Cells: {state.get('cell_count', 0)}")
        parts.append(f"Energy (mean): {state.get('mean_energy', 0):.1f}")
        parts.append(f"Births: {state.get('births', 0)} | Deaths: {state.get('deaths', 0)}")
        parts.append(f"Action magnitude: {float(np.linalg.norm(state.get('action_mean', [0,0,0,0]))):.3f}")

        ss = state.get('self_surprise', 0)
        parts.append(f"Self-surprise: {ss:.3f}")

        # Lineage breakdown
        lineages = state.get('lineages', {})
        if lineages:
            lin_str = ', '.join(f"L{k}:{v}" for k, v in lineages.items())
            parts.append(f"Lineages: {lin_str}")

        # Recent actions
        recent = state.get('recent_actions', [])
        if recent:
            acts = ', '.join(a.get('type', '?') for a in recent[-3:])
            parts.append(f"Recent actions: {acts}")

        # Results from last LLM-directed actions
        if self._action_results:
            parts.append("\nPrevious action results:")
            for ar in self._action_results[-3:]:
                status = 'OK' if ar.get('success') else 'FAIL'
                result_str = str(ar.get('result', ar.get('error', '')))[:300]
                parts.append(f"  [{status}] {result_str}")

        # Observer messages
        if self._bridge_buffer:
            msgs = '; '.join(m['text'] for m in self._bridge_buffer[-3:])
            parts.append(f"Observer says: {msgs}")

        # Past thoughts
        if self._thought_history:
            last = self._thought_history[-1].get('thought', '')
            if last:
                parts.append(f"Previous thought: {last[:150]}")

        # Modification history — what did you change before?
        mod_history = state.get('modification_history', [])
        if mod_history:
            parts.append("\nYour recent modifications:")
            for mod in mod_history[-5:]:
                parts.append(f"  - {mod}")

        # Chain context
        if self._chain_depth > 0:
            parts.append(f"\nThis is step {self._chain_depth + 1} of a multi-step thought chain.")
            parts.append("You can see your previous action results above. Continue or stop.")

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
