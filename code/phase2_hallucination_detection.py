"""
Phase 2: Hallucination Rate Analysis
Analyzes process/structured responses for hallucinations.

Hallucination Categories:
1. Factual error: Objectively false statement (3 × 5 = 11)
2. Irrelevant information: Introduces unrelated facts
3. Logical inconsistency: Contradicts earlier steps
4. Confabulation: Makes up non-existent details
"""

import json
import os
import pandas as pd
import random
import re
from typing import Dict, List

INPUT_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../data/processed/hallucination_analysis.jsonl"
SAMPLE_SIZE = 50  # Number of process responses to analyze

def load_process_responses():
    """Load process and structured responses for hallucination analysis"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return []

    responses = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            # Only analyze process and structured (they have reasoning)
            for condition in ["process", "structured"]:
                response_text = data["responses"].get(condition, "")

                if not response_text:
                    continue

                # Determine if answer was correct
                pred = data["extracted_answers"].get(condition)
                gt = data["ground_truth_numeric"]

                is_correct = False
                if pred is not None and gt is not None:
                    is_correct = abs(pred - gt) < 1e-6

                responses.append({
                    "problem_id": data["problem_id"],
                    "condition": condition,
                    "question": data["question"],
                    "ground_truth": data["ground_truth"],
                    "ground_truth_numeric": gt,
                    "response": response_text,
                    "extracted_answer": pred,
                    "is_correct": is_correct,
                    "has_hallucination": None,  # To be manually annotated
                    "hallucination_types": [],   # List of hallucination types found
                    "hallucination_examples": "", # Specific examples from response
                    "notes": ""
                })

    return responses

def sample_for_annotation(responses: List[Dict], sample_size: int = SAMPLE_SIZE):
    """Sample responses stratified by correctness and condition"""
    df = pd.DataFrame(responses)

    if len(df) == 0:
        print("No responses found to sample.")
        return []

    # Stratified sampling by condition and correctness
    sampled = []

    for condition in ["process", "structured"]:
        for is_correct in [True, False]:
            subset = df[(df["condition"] == condition) & (df["is_correct"] == is_correct)]
            n_sample = min(sample_size // 4, len(subset))
            if n_sample > 0:
                sampled.extend(subset.sample(n=n_sample, random_state=42).to_dict('records'))

    return sampled

def automatic_hallucination_detection(response: str) -> Dict:
    """
    Automatic hallucination detection using heuristics.
    This is a basic implementation - manual review is still recommended.
    """
    flags = {
        "potential_arithmetic_errors": [],
        "confidence": "low"  # Automatic detection is not very reliable
    }

    # Look for arithmetic expressions
    # Pattern: number operator number = result
    arithmetic_pattern = r'(\d+\.?\d*)\s*([+\-*/×÷])\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)'
    matches = re.findall(arithmetic_pattern, response)

    for match in matches:
        num1, op, num2, result = match
        try:
            num1, num2, result = float(num1), float(num2), float(result)

            # Check if calculation is correct
            if op in ['+']:
                expected = num1 + num2
            elif op in ['-']:
                expected = num1 - num2
            elif op in ['*', '×']:
                expected = num1 * num2
            elif op in ['/', '÷']:
                expected = num1 / num2 if num2 != 0 else None
            else:
                continue

            if expected is not None and abs(expected - result) > 1e-6:
                flags["potential_arithmetic_errors"].append({
                    "expression": f"{num1} {op} {num2} = {result}",
                    "expected": expected,
                    "actual": result
                })
        except:
            continue

    return flags

def create_annotation_template():
    """Create annotation template for manual hallucination review"""
    responses = load_process_responses()
    sampled = sample_for_annotation(responses)

    print(f"Total process/structured responses: {len(responses)}")
    print(f"Sampled for hallucination annotation: {len(sampled)}")

    # Add automatic detection flags
    for item in sampled:
        auto_flags = automatic_hallucination_detection(item["response"])
        item["automatic_flags"] = auto_flags

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    # Save sampled responses for manual annotation
    with open(output_path, "w", encoding="utf-8") as f:
        for item in sampled:
            f.write(json.dumps(item, indent=2) + "\n")

    print(f"\nAnnotation template saved to: {output_path}")
    print("\nINSTRUCTIONS FOR MANUAL ANNOTATION:")
    print("=" * 70)
    print(f"1. Open the file: {OUTPUT_FILE}")
    print("2. For each response, set 'has_hallucination' to true or false")
    print("3. If true, add hallucination types to 'hallucination_types' list:")
    print("   - 'factual_error': Objectively false statement")
    print("   - 'irrelevant': Introduces unrelated facts")
    print("   - 'inconsistent': Contradicts earlier steps")
    print("   - 'confabulation': Makes up non-existent details")
    print("4. Copy specific hallucination text to 'hallucination_examples'")
    print("5. Add any notes to 'notes' field")
    print("6. Save the file when complete")
    print("=" * 70)

    # Generate initial statistics (will be empty until annotation)
    stats = generate_hallucination_statistics(sampled)
    return stats

def generate_hallucination_statistics(annotated_data: List[Dict]):
    """Generate hallucination rate statistics"""
    df = pd.DataFrame(annotated_data)

    if "has_hallucination" not in df.columns or df["has_hallucination"].isna().all():
        print("\nNo annotations found yet. Please complete manual annotation first.")
        return None

    # Remove unannotated entries
    df = df[df["has_hallucination"].notna()]

    if len(df) == 0:
        print("No annotated responses found.")
        return None

    print("\n" + "=" * 70)
    print("HALLUCINATION ANALYSIS RESULTS")
    print("=" * 70)

    # Overall hallucination rate
    total = len(df)
    with_hallucination = df["has_hallucination"].sum()
    hallucination_rate = (with_hallucination / total) * 100

    print(f"\nOverall Hallucination Rate: {hallucination_rate:.1f}% ({with_hallucination}/{total})")

    # By condition
    print("\nHallucination Rate by Condition:")
    for condition in ["process", "structured"]:
        cond_df = df[df["condition"] == condition]
        if len(cond_df) > 0:
            cond_rate = (cond_df["has_hallucination"].sum() / len(cond_df)) * 100
            print(f"  {condition}: {cond_rate:.1f}% ({cond_df['has_hallucination'].sum()}/{len(cond_df)})")

    # By correctness
    print("\nHallucination Rate by Answer Correctness:")
    for is_correct in [True, False]:
        subset = df[df["is_correct"] == is_correct]
        if len(subset) > 0:
            rate = (subset["has_hallucination"].sum() / len(subset)) * 100
            label = "Correct Answers" if is_correct else "Incorrect Answers"
            print(f"  {label}: {rate:.1f}% ({subset['has_hallucination'].sum()}/{len(subset)})")

    # Hallucination types distribution (if annotated)
    hallucination_types_all = []
    for _, row in df[df["has_hallucination"] == True].iterrows():
        if "hallucination_types" in row and row["hallucination_types"]:
            hallucination_types_all.extend(row["hallucination_types"])

    if hallucination_types_all:
        print("\nHallucination Types Distribution:")
        from collections import Counter
        type_counts = Counter(hallucination_types_all)
        for htype, count in type_counts.most_common():
            print(f"  {htype}: {count}")

    # Save statistics
    stats = {
        "total_annotated": total,
        "with_hallucination": int(with_hallucination),
        "hallucination_rate": hallucination_rate,
        "by_condition": {},
        "by_correctness": {}
    }

    for condition in ["process", "structured"]:
        cond_df = df[df["condition"] == condition]
        if len(cond_df) > 0:
            stats["by_condition"][condition] = {
                "total": len(cond_df),
                "with_hallucination": int(cond_df["has_hallucination"].sum()),
                "rate": (cond_df["has_hallucination"].sum() / len(cond_df)) * 100
            }

    for is_correct in [True, False]:
        subset = df[df["is_correct"] == is_correct]
        if len(subset) > 0:
            label = "correct" if is_correct else "incorrect"
            stats["by_correctness"][label] = {
                "total": len(subset),
                "with_hallucination": int(subset["has_hallucination"].sum()),
                "rate": (subset["has_hallucination"].sum() / len(subset)) * 100
            }

    stats_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "../results/hallucination_statistics.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nStatistics saved to: {stats_path}")
    return stats

if __name__ == "__main__":
    print("Phase 2: Hallucination Detection")
    print("=" * 70)
    create_annotation_template()
