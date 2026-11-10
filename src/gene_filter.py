"""Deterministic, auditable selection of candidate rows from gene tables."""
import copy
import math

OPS = {'lt', 'le', 'gt', 'ge', 'eq', 'ne', 'in'}
MISSING = {'', 'na', 'n/a', 'nan', 'null', '.'}

def _validate_conditions(table, rule, dataset_id):
    if not isinstance(rule, dict) or set(rule) - {'combine', 'conditions'}:
        raise ValueError(f'{dataset_id}: rule must contain only combine and conditions')
    combine = rule.get('combine', 'all')
    conditions = rule.get('conditions')
    if combine not in {'all', 'any'} or not isinstance(conditions, list) or not conditions:
        raise ValueError(f'{dataset_id}: supply combine=all/any and a nonempty conditions list')
    for c in conditions:
        if not isinstance(c, dict) or set(c) != {'column', 'op', 'value'}:
            raise ValueError(f'{dataset_id}: each condition needs column, op and value only')
        col, op, value = c['column'], c['op'], c['value']
        if col not in table['columns'] or col == table['gene_column']:
            raise ValueError(f'{dataset_id}: filter column {col!r} missing or is the gene identifier')
        if op not in OPS:
            raise ValueError(f'{dataset_id}: unsupported operator {op!r}')
        if op in {'lt','le','gt','ge'}:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{dataset_id}: numeric comparison requires a finite numeric threshold')
        elif op == 'in':
            if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
                raise ValueError(f'{dataset_id}: in requires a nonempty string array')
        elif not isinstance(value, (str, int, float)) or isinstance(value, bool) or (isinstance(value, float) and not math.isfinite(value)):
            raise ValueError(f'{dataset_id}: eq/ne requires a string or finite number')
    return combine, conditions

def _check(row, condition):
    text = row[condition['column']].strip()
    if text.lower() in MISSING:
        return False, 'missing'
    op, target = condition['op'], condition['value']
    if op in {'lt', 'le', 'gt', 'ge'} or (op in {'eq', 'ne'} and isinstance(target, (int, float))):
        try:
            value = float(text)
        except ValueError:
            return False, 'non_numeric'
        if not math.isfinite(value):
            return False, 'non_finite'
    else:
        value = text
    result = {'lt': lambda: value < target, 'le': lambda: value <= target,
              'gt': lambda: value > target, 'ge': lambda: value >= target,
              'eq': lambda: value == target, 'ne': lambda: value != target,
              'in': lambda: value in target}[op]()
    return result, 'matched' if result else 'not_matched'

def filter_inputs(payload, rules):
    """Filter every table explicitly and return new agent payload plus a complete audit.

    Rules map dataset IDs to AND/OR expressions. No gene-list membership filtering is performed.
    Missing/invalid values never pass a condition. No implicit threshold is chosen.
    """
    if not isinstance(rules, dict):
        raise ValueError('Filter rules must be a JSON object mapping dataset IDs to rules')
    result = copy.deepcopy(payload)
    if 'datasets' in result:
        datasets = result['datasets']
    elif result.get('table') is not None:
        datasets = [{'dataset_id': 'table_1', 'table_name': result.get('provenance', {}).get('table', {}).get('filename'), 'gene_table': result['table']}]
    else:
        raise ValueError('Filtering requires at least one CSV table')
    if not datasets:
        raise ValueError('Filtering requires at least one CSV table')
    ids = [d['dataset_id'] for d in datasets]
    if set(rules) != set(ids):
        raise ValueError(f'Filter rules must specify exactly these dataset IDs: {ids}')
    audit = []
    for dataset in datasets:
        ident, table = dataset['dataset_id'], dataset['gene_table']
        combine, conditions = _validate_conditions(table, rules[ident], ident)
        selected = []
        for row in table['rows']:
            checks = [_check(row, c) for c in conditions]
            retain = (all if combine == 'all' else any)(x[0] for x in checks)
            if retain:
                selected.append(row)
            audit.append({'dataset_id': ident, 'table_name': dataset.get('table_name'), 'source_row': row['source_row'], 'gene': row[table['gene_column']], 'selected': retain, 'condition_results': [{'column': c['column'], 'observed': row[c['column']], 'op': c['op'], 'value': c['value'], 'result': reason} for c, (_, reason) in zip(conditions, checks)]})
        table['rows'] = selected
        dataset['selection'] = {'rule': rules[ident], 'source_rows': sum(a['dataset_id'] == ident for a in audit), 'selected_rows': len(selected)}
    if 'datasets' not in result:
        result['table'] = datasets[0]['gene_table']
        result['selection'] = datasets[0]['selection']
    result['selection_summary'] = [d['selection'] | {'dataset_id': d['dataset_id']} for d in datasets]
    return result, audit
