import unittest
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.research_inputs import load_multiple_inputs, format_evidence, ensure_prompt_size
from src.gene_filter import filter_inputs

class GeneFilterTests(unittest.TestCase):
    def setUp(self):
        self.specs = [
            {'table_bytes': b'gene,hr,fdr\nMMP9,1.7,0.01\nGPC1,1.2,0.3\nIL2,0.7,NA\n', 'table_name': 'prognosis.csv', 'context_bytes': b'OS high versus low', 'context_name': 'os.md'},
            {'table_bytes': b'gene,p\nTNF,0.01\nMMP9,0.5\n', 'table_name': 'response.csv', 'context_bytes': b'treatment interaction', 'context_name': 'response.md'},
        ]
        self.payload = load_multiple_inputs(table_specs=self.specs)
        self.rules = {'table_1': {'combine': 'all', 'conditions': [{'column':'hr','op':'gt','value':1}, {'column':'fdr','op':'lt','value':0.05}]}, 'table_2': {'conditions':[{'column':'p','op':'lt','value':0.05}]}}

    def test_independent_rules_select_not_context_matching(self):
        result, audit = filter_inputs(self.payload, self.rules)
        self.assertEqual([x['gene'] for x in result['datasets'][0]['gene_table']['rows']], ['MMP9'])
        self.assertEqual([x['gene'] for x in result['datasets'][1]['gene_table']['rows']], ['TNF'])
        self.assertEqual(len(audit), 5)
        self.assertEqual(audit[2]['condition_results'][1]['result'], 'missing')
        self.assertEqual(audit[1]['condition_results'][1]['observed'], '0.3')
        prompt = format_evidence(result)
        self.assertIn('MMP9', prompt); self.assertIn('TNF', prompt)
        self.assertNotIn('GPC1', prompt); self.assertNotIn('IL2', prompt)
        self.assertEqual(len(self.payload['datasets'][0]['gene_table']['rows']), 3)

    def test_invalid_or_missing_rule_never_falls_back(self):
        with self.assertRaisesRegex(ValueError, 'exactly'):
            filter_inputs(self.payload, {'table_1': self.rules['table_1']})
        bad = dict(self.rules, table_1={'conditions':[{'column':'gene','op':'eq','value':'MMP9'}]})
        with self.assertRaisesRegex(ValueError, 'gene identifier'):
            filter_inputs(self.payload, bad)
        bad = dict(self.rules, table_1={'conditions':[{'column':'hr','op':'gt','value':'1'}]})
        with self.assertRaisesRegex(ValueError, 'numeric'):
            filter_inputs(self.payload, bad)

    def test_or_and_non_numeric(self):
        self.rules['table_1']['combine'] = 'any'
        result, _ = filter_inputs(self.payload, self.rules)
        self.assertEqual([r['gene'] for r in result['datasets'][0]['gene_table']['rows']], ['MMP9','GPC1'])
        self.specs[0]['table_bytes'] = b'gene,hr,fdr\nX,oops,0.01\n'
        p = load_multiple_inputs(table_specs=self.specs)
        _, a = filter_inputs(p, self.rules)
        self.assertEqual(a[0]['condition_results'][0]['result'], 'non_numeric')

    def test_allow_large_input_only_after_filter(self):
        big = b'gene,hr,fdr\n' + b''.join(f'G{i},1,0.5\n'.encode() for i in range(10000)) + b'Winner,2,0.01\n'
        self.specs[0]['table_bytes'] = big
        p = load_multiple_inputs(table_specs=self.specs, validate_size=False)
        with self.assertRaises(ValueError): ensure_prompt_size(p)
        result, _ = filter_inputs(p, self.rules)
        ensure_prompt_size(result)
        self.assertEqual([r['gene'] for r in result['datasets'][0]['gene_table']['rows']], ['Winner'])

if __name__ == '__main__': unittest.main()
