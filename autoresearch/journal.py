"""
Research Journal — persistent memory for the autonomous research loop.

Stores hypotheses, experiments, findings, and open questions as a
growing JSON file. The brain reads the journal to decide what to do next.
"""

import json
import os
from datetime import datetime
from pathlib import Path

JOURNAL_PATH = Path(__file__).parent.parent / 'history' / 'research_journal.json'


def _load():
    if JOURNAL_PATH.exists():
        with open(JOURNAL_PATH, 'r') as f:
            return json.load(f)
    return {
        'created': datetime.now().isoformat(),
        'cycle_count': 0,
        'hypotheses': [],
        'experiments': [],
        'findings': [],
        'open_questions': [],
        'knowledge': {},  # accumulated facts keyed by topic
    }


def _save(journal):
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL_PATH, 'w') as f:
        json.dump(journal, f, indent=2, default=str)


def load_journal():
    return _load()


def save_journal(journal):
    _save(journal)


def add_hypothesis(journal, hypothesis, source='brain'):
    """
    Add a hypothesis to test.

    hypothesis dict must have:
      - id:          unique string
      - statement:   what we think is true
      - test_plan:   how to test it (experiment spec)
      - priority:    float 0-1 (higher = more important)
      - status:      'untested' | 'testing' | 'supported' | 'refuted' | 'inconclusive'
    """
    hypothesis.setdefault('status', 'untested')
    hypothesis.setdefault('source', source)
    hypothesis.setdefault('created', datetime.now().isoformat())
    journal['hypotheses'].append(hypothesis)
    return journal


def add_experiment(journal, experiment):
    """
    Log a completed experiment.

    experiment dict should have:
      - hypothesis_id:  which hypothesis this tested
      - config:         parameters used
      - results:        aggregated results
      - timestamp:      when it ran
    """
    experiment.setdefault('timestamp', datetime.now().isoformat())
    journal['experiments'].append(experiment)
    return journal


def add_finding(journal, finding):
    """
    Record a discovered fact.

    finding dict:
      - statement:      plain-text description
      - evidence:       what experiment showed this
      - confidence:     float 0-1
      - tags:           list of topic tags
    """
    finding.setdefault('timestamp', datetime.now().isoformat())
    finding.setdefault('confidence', 0.5)
    journal['findings'].append(finding)
    return journal


def add_question(journal, question):
    """Add an open research question generated from findings."""
    journal['open_questions'].append({
        'question': question,
        'timestamp': datetime.now().isoformat(),
        'resolved': False,
    })
    return journal


def update_knowledge(journal, topic, facts):
    """Update accumulated knowledge on a topic.

    If both existing and new values are dicts, merge them.
    Otherwise, overwrite with the new value.
    """
    existing = journal['knowledge'].get(topic)
    if isinstance(existing, dict) and isinstance(facts, dict):
        existing.update(facts)
    else:
        journal['knowledge'][topic] = facts
    return journal


def get_untested_hypotheses(journal):
    return [h for h in journal['hypotheses'] if h['status'] == 'untested']


def get_findings_by_tag(journal, tag):
    return [f for f in journal['findings'] if tag in f.get('tags', [])]


def get_knowledge(journal, topic):
    return journal['knowledge'].get(topic, {})


def journal_summary(journal):
    """One-paragraph summary of journal state."""
    n_hyp = len(journal['hypotheses'])
    n_untested = len(get_untested_hypotheses(journal))
    n_exp = len(journal['experiments'])
    n_find = len(journal['findings'])
    n_q = len([q for q in journal['open_questions'] if not q.get('resolved')])
    cycles = journal.get('cycle_count', 0)
    return (
        f'Cycle {cycles}: {n_hyp} hypotheses ({n_untested} untested), '
        f'{n_exp} experiments, {n_find} findings, {n_q} open questions'
    )
