import sys
import unittest
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.research_inputs import load_inputs, load_multiple_inputs, load_multiple_paths, format_evidence
from src.main import AICoScientist

class ResearchInputsTests(unittest.TestCase):
    def test_rows_provenance_and_missing_values_preserved(self):
        data = b'gene,hazard_ratio,p_value,cohort\nABC,1.5,0.02,A\nXYZ,,NA,B\nABC,0.8,0.7,C\n'
        p = load_inputs(b'# context', 'context.md', data, 'genes.csv')
        self.assertEqual(len(p['table']['rows']), 3)
        self.assertEqual(p['table']['rows'][1]['hazard_ratio'], '')
        self.assertEqual(p['table']['rows'][2]['source_row'], 4)
        self.assertEqual(p['provenance']['table']['row_count'], 3)
        self.assertEqual(len(p['provenance']['table']['sha256']), 64)
        self.assertIn('prognostic association', format_evidence(p))

    def test_invalid_numeric_values_are_flagged(self):
        p = load_inputs(table_bytes=b'gene,HR,p_value\nX,-1,1.5\n', table_name='x.csv')
        self.assertEqual(len(p['warnings']), 2)
        self.assertEqual(p['table']['rows'][0]['HR'], '-1')

    def test_first_column_default_and_missing_identifiers_fail(self):
        with self.assertRaises(ValueError):
            load_inputs(table_bytes=b'gene,hr\n,2\n')
        p = load_inputs(table_bytes=b'gene,symbol\nX,Y\n', gene_column='gene')
        self.assertEqual(p['table']['gene_column'], 'gene')
        p = load_inputs(table_bytes=b'target_id,symbol\nX,Y\n')
        self.assertEqual(p['table']['gene_column'], 'target_id')
        self.assertEqual(load_inputs(table_bytes=b'target_id,symbol\nX,Y\n', gene_column='symbol')['table']['gene_column'], 'symbol')

    def test_multiple_model_statistics_checked(self):
        p = load_inputs(table_bytes=b'gene,hr_univariate,adjusted_p_model2,cox3_hr,cox3_p_value\nX,-1,1.2,0,1.1\n')
        self.assertEqual(len(p['warnings']), 4)

    def test_prompt_limit_rejects_without_truncation(self):
        with self.assertRaisesRegex(ValueError, 'no rows were silently removed'):
            load_inputs(context_bytes=b'x' * 180001)

    def test_context_reaches_each_workflow_stage(self):
        seen = []
        class Agent:
            def generate_hypotheses(self, goal, count):
                seen.append(('generation', goal)); return [{'hypothesis': 'When expression increases risk increases'}]
            def rank_hypotheses(self, goal, hypotheses):
                seen.append(('ranking', goal)); return hypotheses
            def review_hypothesis(self, hypothesis, goal):
                seen.append(('review', goal)); return {'critique': 'test'}
            def evolve_hypothesis(self, hypothesis, feedback, goal):
                seen.append(('evolution', goal)); return {'hypothesis': hypothesis}
            def evaluate_proximity(self, hypothesis, goal):
                seen.append(('proximity', goal)); return {'proximity_score': 1}
            def generate_report(self, goal, hypotheses, max_hypotheses):
                seen.append(('report', goal)); return {'hypotheses': hypotheses}
        agent = Agent()
        app = AICoScientist.__new__(AICoScientist)
        app.research_goal = 'To evaluate cancer biomarkers'
        app.logger = SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
        app.agent_factory = SimpleNamespace(get_agent=lambda *a, **kw: agent)
        app.config = {'model': 'test', 'temperature': 0.2}
        app.set_research_inputs(load_multiple_inputs(b'# MY_CONTEXT', 'ctx.md', [
            {'table_bytes': b'gene,hr\nGENE_X,1.5\n', 'table_name': 'a.csv', 'context_bytes': b'model A definition', 'context_name': 'a.md'},
            {'table_bytes': b'gene,p\nGENE_Y,0.01\n', 'table_name': 'b.csv', 'context_bytes': b'model B definition', 'context_name': 'b.md'},
        ]))
        app.generate_hypotheses(); app.rank_hypotheses(); app.refine_hypotheses(1); app.generate_research_report()
        self.assertEqual({stage for stage, _ in seen}, {'generation','ranking','review','evolution','proximity','report'})
        for _, goal in seen:
            self.assertIn('MY_CONTEXT', goal)
            self.assertIn('GENE_X', goal)
            self.assertIn('GENE_Y', goal)
            self.assertIn('model A definition', goal)
            self.assertIn('model B definition', goal)

    def test_multiline_csv_row_number(self):
        p = load_inputs(table_bytes=b'gene,note\nX,"line1\nline2"\nY,last\n')
        self.assertEqual([r['source_row'] for r in p['table']['rows']], [2, 4])

    def test_two_tables_keep_distinct_context_and_identifiers(self):
        specs = [
            {'table_bytes': b'gene,hr\nIL20RA,1.5\n', 'table_name': 'prognosis.csv', 'context_bytes': b'Overall survival; no treatment comparison', 'context_name': 'prognosis.md'},
            {'table_bytes': b'gene,interaction_hr\nIL20RA,0.7\n', 'table_name': 'response.csv', 'context_bytes': b'Progression-free survival treatment interaction', 'context_name': 'response.md'},
        ]
        p = load_multiple_inputs(b'Common study overview', 'global.md', specs)
        self.assertEqual([d['dataset_id'] for d in p['datasets']], ['table_1', 'table_2'])
        self.assertEqual(p['datasets'][0]['gene_table']['rows'][0]['hr'], '1.5')
        self.assertIn('Overall survival', p['datasets'][0]['markdown_context'])
        self.assertEqual(p['datasets'][1]['gene_table']['rows'][0]['interaction_hr'], '0.7')
        self.assertIn('treatment interaction', p['datasets'][1]['markdown_context'])
        self.assertEqual(p['provenance']['datasets'][1]['table']['filename'], 'response.csv')
        self.assertIn('do not apply one table definition', format_evidence(p))

    def test_context_only_gene_groups_reach_agents(self):
        context = b'Unfavorable: MMP9, GPC1. Favorable: IL2, TNF.'
        for p in (load_inputs(context_bytes=context), load_multiple_inputs(common_context_bytes=context)):
            prompt = format_evidence(p)
            for gene in ('MMP9', 'GPC1', 'IL2', 'TNF'):
                self.assertIn(gene, prompt)
            self.assertIn('favorable or unfavorable', prompt)
            self.assertIn('Do not treat these labels as independently validated', prompt)

    def test_missing_context_or_mismatched_paths_fail(self):
        with self.assertRaisesRegex(ValueError, 'both a CSV'):
            load_multiple_inputs(table_specs=[{'table_bytes': b'gene\nX\n'}])
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            load_multiple_paths(table_paths=['a.csv'], table_context_paths=[])

    def test_reserved_source_row_fails(self):
        with self.assertRaisesRegex(ValueError, 'reserved'):
            load_inputs(table_bytes=b'gene,source_row\nX,17\n')

if __name__ == '__main__':
    unittest.main()
