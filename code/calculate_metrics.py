import json
import os
import pandas as pd
import numpy as np
from scipy.stats import chi2

INPUT_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../results/accuracy_metrics.json"

def calculate_metrics():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
            
    df = pd.DataFrame(data)
    
    if len(df) == 0:
        print("No data found.")
        return

    # Helper to check correctness (allowing small float tolerance)
    def is_correct(row, condition):
        pred = row["extracted_answers"].get(condition)
        gt = row["ground_truth_numeric"]
        
        if pred is None or gt is None:
            return False
        
        try:
            return abs(pred - gt) < 1e-6
        except:
            return False

    conditions = ["outcome", "process", "structured"]
    results = {}
    
    # Calculate Accuracy
    for cond in conditions:
        df[f"{cond}_correct"] = df.apply(lambda row: is_correct(row, cond), axis=1)
        acc = df[f"{cond}_correct"].mean()
        results[f"{cond}_accuracy"] = acc
        print(f"Accuracy ({cond}): {acc:.2%}")

    # Statistical Significance (McNemar's Test)
    # Compare Process vs Outcome
    # Contingency table:
    # [[Both Correct, Process Correct Only],
    #  [Outcome Correct Only, Both Wrong]]
    
    both_correct = len(df[(df["process_correct"]) & (df["outcome_correct"])])
    process_only = len(df[(df["process_correct"]) & (~df["outcome_correct"])])
    outcome_only = len(df[(~df["process_correct"]) & (df["outcome_correct"])])
    both_wrong = len(df[(~df["process_correct"]) & (~df["outcome_correct"])])
    
    contingency = [[both_correct, process_only], [outcome_only, both_wrong]]
    
    # McNemar requires the "disagreement" cells mainly: b and c
    # The `mcnemar` function takes the table.
    
    try:
        # Note: scipy mcnemar expects [[a, b], [c, d]] ? Wait, standard is:
        #         Model 2 +   Model 2 -
        # Model 1 +    a          b
        # Model 1 -    c          d
        # Here Model 1 = Outcome, Model 2 = Process?
        # Let's be precise.
        # Yes, standard contingency for McNemar:
        # b = Model 1 Positive & Model 2 Negative
        # c = Model 1 Negative & Model 2 Positive
        # The test checks if b == c roughly.
        
        # My contingency:
        # [0][0] = Both Correct (Yes, Yes)
        # [0][1] = Process Correct Only (Process=Yes, Outcome=No) -> This is c if Row=Outcome
        # Wait, let's build it explicitly as:
        #          Process Correct  Process Wrong
        # Outcome Correct    A             B
        # Outcome Wrong      C             D
        
        A = len(df[(df["outcome_correct"]) & (df["process_correct"])])
        B = len(df[(df["outcome_correct"]) & (~df["process_correct"])])
        C = len(df[(~df["outcome_correct"]) & (df["process_correct"])])
        D = len(df[(~df["outcome_correct"]) & (~df["process_correct"])])
        
        table = [[A, B], [C, D]]
        # Manual McNemar calculation
        # b = Process Correct (Outcome Wrong) -> Top Right in [[A, B], [C, D]]? 
        # Wait, my table was [[A, B], [C, D]].
        # A = Both Correct
        # B = Outcome Correct & Process Wrong
        # C = Outcome Wrong & Process Correct
        # D = Both Wrong
        # McNemar statistic is (|B - C| - 0.5)^2 / (B + C) (with continuity correction) or (B-C)^2/(B+C)
        # We need to test if B and C differ significantly.
        
        b = B
        c = C
        if b + c > 0:
            stat = ((abs(b - c) - 0.5) ** 2) / (b + c)
            p = chi2.sf(stat, 1)
            results["mcnemar_outcome_vs_process_pvalue"] = p
            print(f"McNemar p-value (Outcome vs Process): {p:.4f}")
        else:
            results["mcnemar_outcome_vs_process_pvalue"] = 1.0
            print("McNemar p-value: 1.0 (No disagreement)")
        
    except Exception as e:
        print(f"Could not calc McNemar: {e}")

    # Save results
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved metrics to {output_path}")

if __name__ == "__main__":
    calculate_metrics()
