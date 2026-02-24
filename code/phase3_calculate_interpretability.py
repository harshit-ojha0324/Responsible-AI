"""
Phase 3: Calculate Interpretability Metrics
Processes annotated data to calculate:
1. Step Correctness Score
2. Faithfulness / Expert Alignment Score
3. Human Auditability Scores (Clarity, Verification Effort, Coherence)
"""

import json
import os
import pandas as pd
import numpy as np
from typing import List, Dict

INPUT_FILE = "../data/annotations/deep_annotation_sample.jsonl"
OUTPUT_FILE = "../results/interpretability_metrics.json"

def load_annotations():
    """Load annotated data"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    if not os.path.exists(input_path):
        print(f"Annotation file not found: {input_path}")
        print("Please run phase3_sample_selection.py first and complete annotations.")
        return []

    annotations = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            annotations.append(json.loads(line))

    return annotations

def calculate_step_correctness(annotations: List[Dict]):
    """Calculate Step Correctness Score for each problem"""
    results = []

    for ann in annotations:
        step_scores = ann.get("step_scores", [])

        if not step_scores:
            # Not yet annotated
            continue

        # Calculate mean step correctness
        mean_score = np.mean(step_scores)

        results.append({
            "problem_id": ann["problem_id"],
            "condition": ann["condition"],
            "step_correctness_score": mean_score,
            "total_steps": len(step_scores),
            "correct_steps": sum(1 for s in step_scores if s == 2),
            "partial_steps": sum(1 for s in step_scores if s == 1),
            "incorrect_steps": sum(1 for s in step_scores if s == 0)
        })

    return results

def calculate_faithfulness(annotations: List[Dict]):
    """Calculate Faithfulness / Expert Alignment Score"""
    results = []

    for ann in annotations:
        alignment_scores = ann.get("alignment_scores", [])

        if not alignment_scores:
            # Not yet annotated
            continue

        # Calculate mean alignment
        mean_score = np.mean(alignment_scores)

        results.append({
            "problem_id": ann["problem_id"],
            "condition": ann["condition"],
            "faithfulness_score": mean_score,
            "total_alignments": len(alignment_scores),
            "perfect_alignments": sum(1 for s in alignment_scores if s == 2),
            "partial_alignments": sum(1 for s in alignment_scores if s == 1),
            "poor_alignments": sum(1 for s in alignment_scores if s == 0)
        })

    return results

def calculate_auditability(annotations: List[Dict]):
    """Calculate Human Auditability Scores"""
    results = []

    for ann in annotations:
        clarity = ann.get("clarity_score")
        verification = ann.get("verification_effort_score")
        coherence = ann.get("coherence_score")

        if clarity is None or verification is None or coherence is None:
            # Not yet annotated
            continue

        results.append({
            "problem_id": ann["problem_id"],
            "condition": ann["condition"],
            "clarity_score": clarity,
            "verification_effort_score": verification,
            "coherence_score": coherence
        })

    return results

def aggregate_metrics(step_correctness, faithfulness, auditability):
    """Aggregate metrics by condition"""
    # Combine all data
    df_step = pd.DataFrame(step_correctness)
    df_faith = pd.DataFrame(faithfulness)
    df_audit = pd.DataFrame(auditability)

    # Merge
    df = df_step.merge(df_faith, on=["problem_id", "condition"], how="outer")
    df = df.merge(df_audit, on=["problem_id", "condition"], how="outer")

    if len(df) == 0:
        print("No annotated data found. Please complete annotations first.")
        return None

    print("\n" + "=" * 70)
    print("INTERPRETABILITY METRICS SUMMARY")
    print("=" * 70)

    # Aggregate by condition
    summary = {}

    for condition in ["process", "structured"]:
        cond_df = df[df["condition"] == condition]

        if len(cond_df) == 0:
            continue

        summary[condition] = {
            "n_annotated": len(cond_df),
            "step_correctness": {
                "mean": cond_df["step_correctness_score"].mean(),
                "std": cond_df["step_correctness_score"].std(),
                "median": cond_df["step_correctness_score"].median()
            },
            "faithfulness": {
                "mean": cond_df["faithfulness_score"].mean(),
                "std": cond_df["faithfulness_score"].std(),
                "median": cond_df["faithfulness_score"].median()
            },
            "clarity": {
                "mean": cond_df["clarity_score"].mean(),
                "std": cond_df["clarity_score"].std(),
                "median": cond_df["clarity_score"].median()
            },
            "verification_effort": {
                "mean": cond_df["verification_effort_score"].mean(),
                "std": cond_df["verification_effort_score"].std(),
                "median": cond_df["verification_effort_score"].median()
            },
            "coherence": {
                "mean": cond_df["coherence_score"].mean(),
                "std": cond_df["coherence_score"].std(),
                "median": cond_df["coherence_score"].median()
            }
        }

        print(f"\n{condition.upper()}:")
        print(f"  N = {len(cond_df)} problems annotated")
        print(f"  Step Correctness:     {summary[condition]['step_correctness']['mean']:.2f} ± {summary[condition]['step_correctness']['std']:.2f}")
        print(f"  Faithfulness:         {summary[condition]['faithfulness']['mean']:.2f} ± {summary[condition]['faithfulness']['std']:.2f}")
        print(f"  Clarity:              {summary[condition]['clarity']['mean']:.2f} ± {summary[condition]['clarity']['std']:.2f}")
        print(f"  Verification Effort:  {summary[condition]['verification_effort']['mean']:.2f} ± {summary[condition]['verification_effort']['std']:.2f}")
        print(f"  Coherence:            {summary[condition]['coherence']['mean']:.2f} ± {summary[condition]['coherence']['std']:.2f}")

    return summary

def calculate_inter_rater_reliability(annotations1: List[Dict], annotations2: List[Dict]):
    """
    Calculate inter-rater reliability (Cohen's Kappa or ICC)
    Only applicable if you have multiple annotators.

    This is a placeholder - implement if you have 2+ annotators.
    """
    # TODO: Implement if multiple annotators available
    print("\nInter-rater reliability:")
    print("  Not calculated (single annotator)")
    print("  For multiple annotators, implement Cohen's Kappa or ICC here")

    return None

def main():
    print("Phase 3: Calculate Interpretability Metrics")
    print("=" * 70)

    annotations = load_annotations()
    print(f"Loaded {len(annotations)} annotation records")

    # Check if annotations are complete
    annotated_count = sum(1 for a in annotations if a.get("step_scores"))
    print(f"Completed annotations: {annotated_count}/{len(annotations)}")

    if annotated_count == 0:
        print("\nNo completed annotations found.")
        print("Please complete the annotation process first.")
        return

    # Calculate metrics
    step_correctness = calculate_step_correctness(annotations)
    faithfulness = calculate_faithfulness(annotations)
    auditability = calculate_auditability(annotations)

    # Aggregate
    summary = aggregate_metrics(step_correctness, faithfulness, auditability)

    if summary is None:
        return

    # Save results
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    results = {
        "summary": summary,
        "detailed": {
            "step_correctness": step_correctness,
            "faithfulness": faithfulness,
            "auditability": auditability
        }
    }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
