# CELL 7 — Load held-out test set from your dataset

import csv

# IDs already used as in-context examples
EXAMPLE_IDS = {'108','41','63','87','88','107','104','100','98',
               '96','102','106','58','59','93','51','2','3','1','25'}

test_problems = []
with open('/content/geometry_problems.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if (row['problem_runs_on_Newclid_3.01'] == 'yes'
                and row['problem_id'] not in EXAMPLE_IDS
                and row['JGEX_problem_statement']
                and row['original_NL_problem_statement']):
            test_problems.append({
                'id': row['problem_id'],
                'nl': row['original_NL_problem_statement'].replace('\n', ' ').strip(),
                'jgex_reference': row['JGEX_problem_statement'].strip()
            })

print(f"Test set: {len(test_problems)} problems")

# CELL 8 — Run pipeline on test set and compare to ground truth

results = []
for i, prob in enumerate(test_problems):
    print(f"\n[{i+1}/{len(test_problems)}] ID {prob['id']}: {prob['nl'][:60]}...")
    jgex, rounds_taken, history = formalize(prob['nl'], EXAMPLES)

    results.append({
        'id': prob['id'],
        'nl_problem': prob['nl'],
        'jgex_reference': prob['jgex_reference'],
        'jgex_result': jgex,
        'rounds_taken': rounds_taken,
        'success': jgex is not None,
        'history': history
    })
    print(f"  → {'SUCCESS' if jgex else 'FAILED'} in {rounds_taken} round(s)")

# Save
with open('/content/pipeline_results_eval.json', 'w') as f:
    json.dump(results, f, indent=2)

# Summary
n = len(results)
successes = sum(r['success'] for r in results)
print(f"\n{'='*50}")
print(f"Summary: {successes}/{n} ({100*successes//n}%)")
for r_num in range(1, 6):
    at_round = sum(1 for r in results if r['success'] and r['rounds_taken'] == r_num)
    if at_round:
        print(f"  Solved at round {r_num}: {at_round}")