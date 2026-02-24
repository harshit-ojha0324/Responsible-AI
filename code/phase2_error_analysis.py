"""
Phase 2: Error Type Analysis
Analyzes incorrect responses and categorizes errors by type.

Error Taxonomy:
1. Arithmetic error: Calculation mistake (e.g., 3 × 5 = 11)
2. Conceptual error: Wrong approach or formula
3. Reading comprehension error: Misunderstood problem
4. Incomplete reasoning: Missing steps or logic gaps
5. Formatting/parsing error: Answer present but not extracted
"""

import json
import os
import pandas as pd
import random
from typing import Dict, List

INPUT_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../data/processed/error_analysis.jsonl"
SAMPLE_SIZE = 50  # Number of errors to manually analyze

def load_incorrect_responses():
    """Load all incorrect responses across all conditions"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return []

    incorrect_responses = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            # Check each condition
            for condition in ["outcome", "process", "structured"]:
                pred = data["extracted_answers"].get(condition)
                gt = data["ground_truth_numeric"]

                is_wrong = False
                if pred is None or gt is None:
                    is_wrong = True
                elif abs(pred - gt) >= 1e-6:
                    is_wrong = True

                if is_wrong:
                    incorrect_responses.append({
                        "problem_id": data["problem_id"],
                        "condition": condition,
                        "question": data["question"],
                        "ground_truth": data["ground_truth"],
                        "ground_truth_numeric": gt,
                        "response": data["responses"].get(condition, ""),
                        "extracted_answer": pred,
                        "error_type": None,  # To be manually annotated
                        "error_notes": ""     # Additional notes
                    })

    return incorrect_responses

def sample_errors_for_annotation(errors: List[Dict], sample_size: int = SAMPLE_SIZE):
    """Sample errors stratified by condition"""
    df = pd.DataFrame(errors)

    if len(df) == 0:
        print("No errors found to sample.")
        return []

    # Stratified sampling by condition
    sampled = []
    for condition in ["outcome", "process", "structured"]:
        cond_errors = df[df["condition"] == condition]
        n_sample = min(sample_size // 3, len(cond_errors))
        if n_sample > 0:
            sampled.extend(cond_errors.sample(n=n_sample, random_state=42).to_dict('records'))

    return sampled

def create_annotation_template():
    """Create annotation template for manual review"""
    errors = load_incorrect_responses()
    sampled = sample_errors_for_annotation(errors)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    print(f"Total incorrect responses: {len(errors)}")
    print(f"Sampled for annotation: {len(sampled)}")

    # Save sampled errors for manual annotation
    with open(output_path, "w", encoding="utf-8") as f:
        for error in sampled:
            f.write(json.dumps(error, indent=2) + "\n")

    print(f"\nAnnotation template saved to: {output_path}")
    print("\nINSTRUCTIONS FOR MANUAL ANNOTATION:")
    print("=" * 70)
    print("1. Open the file: {OUTPUT_FILE}")
    print("2. For each error, add the 'error_type' field with one of:")
    print("   - 'arithmetic': Calculation mistake")
    print("   - 'conceptual': Wrong approach or formula")
    print("   - 'comprehension': Misunderstood problem")
    print("   - 'incomplete': Missing steps or logic gaps")
    print("   - 'formatting': Answer present but not extracted properly")
    print("3. Optionally add notes in 'error_notes' field")
    print("4. Save the file when complete")
    print("=" * 70)

    # Generate error distribution statistics (will be empty until annotation)
    stats = generate_error_statistics(sampled)
    return stats

def generate_error_statistics(annotated_errors: List[Dict]):
    """Generate error type distribution statistics"""
    df = pd.DataFrame(annotated_errors)

    if "error_type" not in df.columns or df["error_type"].isna().all():
        print("\nNo annotations found yet. Please complete manual annotation first.")
        return None

    # Remove unannotated entries
    df = df[df["error_type"].notna()]

    if len(df) == 0:
        print("No annotated errors found.")
        return None

    print("\n" + "=" * 70)
    print("ERROR TYPE DISTRIBUTION")
    print("=" * 70)

    # Overall distribution
    print("\nOverall Error Distribution:")
    error_counts = df["error_type"].value_counts()
    for error_type, count in error_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {error_type}: {count} ({percentage:.1f}%)")

    # Distribution by condition
    print("\nError Distribution by Condition:")
    for condition in ["outcome", "process", "structured"]:
        cond_df = df[df["condition"] == condition]
        if len(cond_df) > 0:
            print(f"\n  {condition.upper()}:")
            cond_counts = cond_df["error_type"].value_counts()
            for error_type, count in cond_counts.items():
                percentage = (count / len(cond_df)) * 100
                print(f"    {error_type}: {count} ({percentage:.1f}%)")

    # Save statistics
    stats = {
        "total_annotated": len(df),
        "overall_distribution": error_counts.to_dict(),
        "by_condition": {}
    }

    for condition in ["outcome", "process", "structured"]:
        cond_df = df[df["condition"] == condition]
        if len(cond_df) > 0:
            stats["by_condition"][condition] = cond_df["error_type"].value_counts().to_dict()

    stats_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "../results/error_type_statistics.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nStatistics saved to: {stats_path}")
    return stats

if __name__ == "__main__":
    print("Phase 2: Error Type Analysis")
    print("=" * 70)
    create_annotation_template()
