"""
Phase 3: Sample Selection for Deep Annotation
Selects 50-70 problems for intensive annotation of interpretability metrics.
Stratified by correctness and condition.
"""

import json
import os
import pandas as pd
import random

INPUT_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../data/annotations/deep_annotation_sample.jsonl"
SAMPLE_SIZE = 60  # Target 60 problems (20 per condition)

def load_all_responses():
    """Load all responses with correctness information"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return []

    responses = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            # Calculate correctness for each condition
            correctness = {}
            for condition in ["outcome", "process", "structured"]:
                pred = data["extracted_answers"].get(condition)
                gt = data["ground_truth_numeric"]

                is_correct = False
                if pred is not None and gt is not None:
                    is_correct = abs(pred - gt) < 1e-6

                correctness[condition] = is_correct

            responses.append({
                "problem_id": data["problem_id"],
                "question": data["question"],
                "ground_truth": data["ground_truth"],
                "ground_truth_numeric": data["ground_truth_numeric"],
                "responses": data["responses"],
                "extracted_answers": data["extracted_answers"],
                "correctness": correctness
            })

    return responses

def stratified_sample(responses, target_size=SAMPLE_SIZE):
    """
    Perform stratified sampling to ensure good coverage.
    Stratify by:
    - Correctness (correct/incorrect for process condition)
    - Problem diversity
    """
    df = pd.DataFrame(responses)

    if len(df) == 0:
        print("No responses to sample from.")
        return []

    # Stratify by process correctness (primary metric)
    correct = df[df["correctness"].apply(lambda x: x.get("process", False))]
    incorrect = df[df["correctness"].apply(lambda x: not x.get("process", False))]

    # Sample roughly 50/50 correct/incorrect
    n_correct = min(target_size // 2, len(correct))
    n_incorrect = min(target_size // 2, len(incorrect))

    sampled = []

    if n_correct > 0:
        sampled.extend(correct.sample(n=n_correct, random_state=42).to_dict('records'))

    if n_incorrect > 0:
        sampled.extend(incorrect.sample(n=n_incorrect, random_state=42).to_dict('records'))

    return sampled

def create_annotation_template(sampled_problems):
    """Create template for deep annotation"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    # Create annotations directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Prepare annotation template
    annotation_template = []

    for problem in sampled_problems:
        # Focus on process and structured (they have reasoning to annotate)
        for condition in ["process", "structured"]:
            annotation_template.append({
                "problem_id": problem["problem_id"],
                "condition": condition,
                "question": problem["question"],
                "ground_truth": problem["ground_truth"],
                "ground_truth_numeric": problem["ground_truth_numeric"],
                "response": problem["responses"].get(condition, ""),
                "extracted_answer": problem["extracted_answers"].get(condition),
                "is_correct": problem["correctness"].get(condition, False),

                # Annotation fields (to be filled manually)
                "reasoning_steps": [],  # List of extracted reasoning steps
                "step_scores": [],  # Score for each step (0, 1, 2)
                "step_correctness_score": None,  # Mean of step scores

                "expert_steps": [],  # Expert solution steps (from ground truth)
                "alignment_scores": [],  # Alignment between model and expert steps
                "faithfulness_score": None,  # Mean alignment score

                "clarity_score": None,  # 1-5 Likert scale
                "verification_effort_score": None,  # 1-5 Likert scale
                "coherence_score": None,  # 1-5 Likert scale

                "notes": ""  # Additional notes
            })

    # Save template
    with open(output_path, "w", encoding="utf-8") as f:
        for item in annotation_template:
            f.write(json.dumps(item, indent=2) + "\n")

    print(f"Annotation template saved to: {output_path}")
    print(f"Total problems to annotate: {len(annotation_template)}")

    return annotation_template

def main():
    print("Phase 3: Sample Selection for Deep Annotation")
    print("=" * 70)

    responses = load_all_responses()
    print(f"Total responses loaded: {len(responses)}")

    sampled = stratified_sample(responses, SAMPLE_SIZE)
    print(f"Sampled {len(sampled)} problems for deep annotation")

    # Count correct/incorrect
    correct_count = sum(1 for p in sampled if p["correctness"].get("process", False))
    incorrect_count = len(sampled) - correct_count

    print(f"  - Correct (process): {correct_count}")
    print(f"  - Incorrect (process): {incorrect_count}")

    template = create_annotation_template(sampled)

    print("\nINSTRUCTIONS FOR DEEP ANNOTATION:")
    print("=" * 70)
    print(f"1. Open: {OUTPUT_FILE}")
    print("2. For each problem:")
    print("   a. Extract reasoning steps into 'reasoning_steps' list")
    print("   b. Score each step (0-2) in 'step_scores':")
    print("      0 = Incorrect/unjustified")
    print("      1 = Partially correct/incomplete")
    print("      2 = Correct and well-justified")
    print("   c. Extract expert steps from ground_truth into 'expert_steps'")
    print("   d. Score alignment between model & expert in 'alignment_scores' (0-2)")
    print("   e. Rate clarity, verification effort, coherence (1-5 Likert)")
    print("3. The script will automatically calculate mean scores")
    print("=" * 70)

if __name__ == "__main__":
    main()
