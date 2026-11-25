"""The orchestrator-first rule must appear wherever a host could pick a skill."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import routing_eval  # noqa: E402

ENTRY = 'delivery-orchestrator'
ORIENTATION = 'using-the-harness'
SKILLS = sorted(path.parent.name for path in (ROOT / 'skills').glob('*/SKILL.md'))


def read(name):
    return (ROOT / 'skills' / name / 'SKILL.md').read_text()


class OrchestratorEntryTests(unittest.TestCase):
    def test_entry_skill_declares_itself_the_default(self):
        text = read(ENTRY)
        self.assertIn('Default entry point for every delivery ask', text.split('\n---\n')[0])
        for heading in ('## Bring the role in', '## Read first', '## Who asks, and which roles answer', '## The quality sequence'):
            self.assertIn(heading, text)
        for record in ('ROADMAP.md', 'STATUS.md', 'CHANGELOG.md', 'HITL/OPERATOR/'):
            self.assertIn(record, text.split('## Read first')[1].split('\n## ')[0])

    def test_orientation_routes_through_the_entry_and_keeps_no_specialist_table(self):
        text = read(ORIENTATION)
        self.assertIn(f'Every delivery ask enters through `{ENTRY}`', text)
        routing = text.split('## Skill routing')[1].split('\n## ')[0]
        self.assertNotIn('\n| ', routing)
        self.assertIn('**One exception.**', routing)
        self.assertNotIn('Three exceptions', routing)

    def test_every_specialist_names_its_entry_and_its_proof(self):
        for name in SKILLS:
            if name in (ENTRY, ORIENTATION):
                continue
            with self.subTest(skill=name):
                text = read(name)
                self.assertIn(f'A role that {ENTRY} brings in.', text.split('\n---\n')[0])
                section = text.split('## Entry and proof')[1]
                self.assertIn(f'- **Entry:** `{ENTRY}` brings this role in. Enter here directly only '
                              'for a bounded read-only question.', section)
                self.assertRegex(section, r'- \*\*Proof:\*\* \S')

    def test_hook_pointer_names_the_entry(self):
        hook = (ROOT / 'hooks/session-start').read_text()
        self.assertEqual(hook.count(f'Enter every delivery ask through {ENTRY}'), 2)

    def test_session_commands_enter_through_orchestrator(self):
        for cmd in ('get-it-done', 'sitrep', 'wrap-it-up'):
            with self.subTest(command=cmd):
                text = (ROOT / 'commands' / f'{cmd}.md').read_text()
                self.assertIn(f'`{ENTRY}`', text)
                self.assertIn(f'`{cmd}`', text)
                self.assertLess(text.index(f'`{ENTRY}`'), text.index(f'`{cmd}`'))

    def test_readme_and_skills_index_agree_on_skill_count(self):
        count = len(SKILLS)
        skills_readme = (ROOT / 'skills/README.md').read_text()
        root_readme = (ROOT / 'README.md').read_text()
        self.assertIn(f'## The {count} Skills', skills_readme)
        self.assertIn(f'({count} in all)', root_readme)
        self.assertIn(f'The library contains {count} skills.', root_readme)
        self.assertIn(f'{count} tracked capabilities', root_readme)

    def test_routing_prompt_set_is_well_formed(self):
        spec = json.loads((ROOT / 'evals/routing/prompts.json').read_text())
        self.assertEqual(spec['entry'], ENTRY)
        self.assertGreaterEqual(len({case['persona'] for case in spec['prompts']}), 6)
        for case in spec['prompts']:
            self.assertIn(case['role'], SKILLS)

    def test_scoring_counts_the_first_skill_after_orientation(self):
        case = {'id': 'x', 'persona': 'p', 'role': 'sitrep', 'direct_ok': False}
        run = lambda loaded, ending='success': {'loaded': loaded, 'failed': [], 'ending': ending}
        hit = routing_eval.score(case, run([ORIENTATION, ENTRY, 'sitrep']), ENTRY)
        self.assertTrue(hit['orchestrator_first'] and hit['role_reached'])
        direct = routing_eval.score(case, run(['sitrep']), ENTRY)
        self.assertFalse(direct['orchestrator_first'] or direct['direct_specialist'])
        self.assertTrue(routing_eval.score(dict(case, direct_ok=True), run(['sitrep']), ENTRY)['direct_specialist'])
        only_orientation = routing_eval.score(case, run([ORIENTATION]), ENTRY)
        self.assertTrue(only_orientation['no_skill_after_orientation'])
        self.assertFalse(only_orientation['no_skill_at_all'])
        self.assertTrue(routing_eval.score(case, run([]), ENTRY)['no_skill_at_all'])

    def test_failed_loads_and_abnormal_endings_score_nothing(self):
        case = {'id': 'x', 'persona': 'p', 'role': 'sitrep', 'direct_ok': False}
        stream = '\n'.join(json.dumps(event) for event in [
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'a', 'name': 'Skill', 'input': {'skill': f'devex-charter:{ENTRY}'}}]}},
            {'type': 'user', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': 'a', 'is_error': True}]}},
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'b', 'name': 'Skill', 'input': {'skill': 'devex-charter:sitrep'}}]}},
            {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'b'}]}},
            {'type': 'result', 'subtype': 'success'},
        ])
        parsed = routing_eval.parse_stream(stream)
        self.assertEqual((parsed['loaded'], parsed['failed']), (['sitrep'], [ENTRY]))
        self.assertFalse(routing_eval.score(case, parsed, ENTRY)['orchestrator_first'])
        crashed = routing_eval.score(case, {'loaded': [ENTRY, 'sitrep'], 'failed': [], 'ending': None}, ENTRY)
        self.assertFalse(crashed['valid'] or crashed['orchestrator_first'] or crashed['role_reached'])

    def test_codex_loads_are_read_from_successful_skill_file_reads(self):
        def item(command, code, *read):
            return json.dumps({'type': 'item.completed', 'item': {
                'type': 'command_execution', 'command': command, 'exit_code': code,
                'aggregated_output': ''.join(f'---\nname: {name}\ndescription: x\n---\n' for name in read)}})
        stream = '\n'.join([
            item(f"cat .agents/skills/{ORIENTATION}/SKILL.md .agents/skills/{ENTRY}/SKILL.md missing.md", 1,
                 ORIENTATION, ENTRY),
            item('cat .agents/skills/sitrep/SKILL.md', 1),
            item('cat .agents/skills/not-a-skill/SKILL.md README.md', 0),
            json.dumps({'type': 'turn.completed'}),
        ])
        parsed = routing_eval.parse_codex_stream(stream, set(SKILLS))
        self.assertEqual(parsed, {'loaded': [ORIENTATION, ENTRY], 'failed': ['sitrep'], 'ending': 'success'})
        self.assertIsNone(routing_eval.parse_codex_stream(item('ls', 0), set(SKILLS))['ending'])


if __name__ == '__main__':
    unittest.main()
