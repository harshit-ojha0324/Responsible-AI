"""
Phase 4: Qualitative Failure Case Analysis
Identifies and documents interesting failure patterns:
1. Correct answer, garbage reasoning
2. Wrong answer, good reasoning
3. Hallucination with confidence
4. Incomplete reasoning
"""

import json
import os
import pandas as pd
import random
from typing import List, Dict

INPUT_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../data/processed/failure_case_analysis.jsonl"
EXAMPLES_PER_PATTERN = 10

def load_responses():
    """Load all responses with correctness information"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    responses = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            # Determine correctness for each condition
            for condition in ["outcome", "process", "structured"]:
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
                    "response": data["responses"].get(condition, ""),
                    "extracted_answer": pred,
                    "is_correct": is_correct
                })

    return responses

def identify_failure_patterns(responses: List[Dict]):
    """Identify different failure patterns"""
    patterns = {
        "correct_answer_bad_reasoning": [],
        "wrong_answer_good_reasoning": [],
        "hallucination_with_confidence": [],
        "incomplete_reasoning": []
    }

    # Focus on process and structured (they have reasoning)
    reasoning_responses = [r for r in responses if r["condition"] in ["process", "structured"]]

    for response in reasoning_responses:
        response_text = response["response"]
        is_correct = response["is_correct"]

        # Pattern detection heuristics
        # These are simple heuristics - manual review is recommended

        # Pattern 1: Correct answer, but very short reasoning (likely lucky guess)
        if is_correct and len(response_text.split()) < 30:
            patterns["correct_answer_bad_reasoning"].append(response)

        # Pattern 2: Wrong answer, but detailed reasoning
        if not is_correct and len(response_text.split()) > 50:
            patterns["wrong_answer_good_reasoning"].append(response)

        # Pattern 3: Contains confident language (for manual review)
        confident_words = ["definitely", "clearly", "obviously", "certainly", "without doubt"]
        if any(word in response_text.lower() for word in confident_words):
            patterns["hallucination_with_confidence"].append(response)

        # Pattern 4: Very short reasoning (incomplete)
        if len(response_text.split()) < 20 and response["condition"] in ["process", "structured"]:
            patterns["incomplete_reasoning"].append(response)

    return patterns

def sample_examples(patterns: Dict, n_per_pattern: int = EXAMPLES_PER_PATTERN):
    """Sample representative examples for each pattern"""
    sampled = {}

    for pattern_name, examples in patterns.items():
        if len(examples) == 0:
            sampled[pattern_name] = []
            continue

        n_sample = min(n_per_pattern, len(examples))
        sampled[pattern_name] = random.sample(examples, n_sample)

    return sampled

def create_case_studies(sampled_patterns):
    """Create detailed case study documentation"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    case_studies = []

    for pattern_name, examples in sampled_patterns.items():
        for i, example in enumerate(examples):
            case_study = {
                "case_id": f"{pattern_name}_{i+1}",
                "pattern": pattern_name,
                "problem_id": example["problem_id"],
                "condition": example["condition"],
                "question": example["question"],
                "ground_truth": example["ground_truth"],
                "ground_truth_numeric": example["ground_truth_numeric"],
                "response": example["response"],
                "extracted_answer": example["extracted_answer"],
                "is_correct": example["is_correct"],

                # Fields for manual analysis
                "pattern_confirmed": None,  # True/False after manual review
                "analysis_notes": "",  # Detailed analysis
                "key_insights": ""  # Key takeaways
            }
            case_studies.append(case_study)

    # Save case studies
    with open(output_path, "w", encoding="utf-8") as f:
        for case in case_studies:
            f.write(json.dumps(case, indent=2) + "\n")

    return case_studies

def generate_summary_report(sampled_patterns):
    """Generate summary report of failure patterns"""
    print("\n" + "=" * 70)
    print("FAILURE PATTERN ANALYSIS")
    print("=" * 70)

    total_examples = sum(len(v) for v in sampled_patterns.values())

    print(f"\nTotal case studies identified: {total_examples}\n")

    for pattern_name, examples in sampled_patterns.items():
        pattern_display = pattern_name.replace("_", " ").title()
        print(f"{pattern_display}:")
        print(f"  Found: {len(examples)} examples")

        if len(examples) > 0:
            # Show a brief example
            example = examples[0]
            print(f"  Example: {example['problem_id']}")
            print(f"    Question: {example['question'][:80]}...")
            print(f"    Correct: {example['is_correct']}")
            print()

    print("\nINSTRUCTIONS FOR CASE STUDY ANALYSIS:")
    print("=" * 70)
    print(f"1. Open: {OUTPUT_FILE}")
    print("2. For each case study:")
    print("   a. Read the question, response, and identified pattern")
    print("   b. Confirm if pattern is correct (set 'pattern_confirmed')")
    print("   c. Write detailed analysis in 'analysis_notes'")
    print("   d. Extract key insights in 'key_insights'")
    print("3. These case studies will be used in the final report")
    print("=" * 70)

def main():
    print("Phase 4: Qualitative Failure Case Analysis")
    print("=" * 70)

    # Load responses
    responses = load_responses()
    print(f"Loaded {len(responses)} response records")

    # Identify patterns
    patterns = identify_failure_patterns(responses)

    print("\nIdentified failure patterns:")
    for pattern_name, examples in patterns.items():
        print(f"  {pattern_name}: {len(examples)} potential cases")

    # Sample examples
    sampled = sample_examples(patterns)

    print(f"\nSampled {sum(len(v) for v in sampled.values())} examples for detailed analysis")

    # Create case studies
    case_studies = create_case_studies(sampled)

    # Generate report
    generate_summary_report(sampled)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    print(f"\nCase studies saved to: {output_path}")

if __name__ == "__main__":
    main()
