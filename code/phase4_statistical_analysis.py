"""
Phase 4: Statistical Analysis
Performs comprehensive statistical analysis including:
1. Metric comparisons across conditions
2. Correlation analysis
3. Statistical significance testing
4. Effect size calculations
"""

import json
import os
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2, ttest_rel, pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns

# Input files
ACCURACY_FILE = "../results/accuracy_metrics.json"
INTERPRETABILITY_FILE = "../results/interpretability_metrics.json"
RESPONSES_FILE = "../data/processed/responses_with_answers.jsonl"
OUTPUT_FILE = "../results/statistical_analysis.json"

def load_data():
    """Load all necessary data files"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load accuracy metrics
    accuracy_path = os.path.join(base_dir, ACCURACY_FILE)
    with open(accuracy_path, "r") as f:
        accuracy = json.load(f)

    # Load interpretability metrics
    interp_path = os.path.join(base_dir, INTERPRETABILITY_FILE)
    try:
        with open(interp_path, "r") as f:
            interpretability = json.load(f)
    except FileNotFoundError:
        print("Interpretability metrics not found. Some analyses will be skipped.")
        interpretability = None

    # Load detailed responses
    responses_path = os.path.join(base_dir, RESPONSES_FILE)
    responses = []
    with open(responses_path, "r") as f:
        for line in f:
            responses.append(json.loads(line))

    return accuracy, interpretability, responses

def compare_accuracies(accuracy_data, responses):
    """Compare accuracy across conditions with statistical tests"""
    print("\n" + "=" * 70)
    print("ACCURACY COMPARISON")
    print("=" * 70)

    # Create comparison dataframe
    conditions = ["outcome", "process", "structured"]
    accuracies = [accuracy_data.get(f"{c}_accuracy", 0) for c in conditions]

    comparison_df = pd.DataFrame({
        "Condition": conditions,
        "Accuracy": accuracies
    })

    print("\nAccuracy by Condition:")
    for _, row in comparison_df.iterrows():
        print(f"  {row['Condition']:12s}: {row['Accuracy']:.2%}")

    # Statistical tests
    # Paired t-test for outcome vs process
    df = pd.DataFrame(responses)

    def is_correct(row, condition):
        pred = row["extracted_answers"].get(condition)
        gt = row["ground_truth_numeric"]
        if pred is None or gt is None:
            return False
        try:
            return abs(pred - gt) < 1e-6
        except:
            return False

    for cond in conditions:
        df[f"{cond}_correct"] = df.apply(lambda row: is_correct(row, cond), axis=1)

    # Paired t-test
    print("\n" + "-" * 70)
    print("Paired Statistical Tests:")
    print("-" * 70)

    # Outcome vs Process
    # Cast to integers to avoid numpy boolean subtraction errors
    t_stat, p_value = ttest_rel(
        df["outcome_correct"].astype(int),
        df["process_correct"].astype(int)
    )
    print(f"\nOutcome vs Process (Paired t-test):")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"  Result: Significant difference (p < 0.05)")
    else:
        print(f"  Result: No significant difference (p >= 0.05)")

    # Process vs Structured
    t_stat2, p_value2 = ttest_rel(
        df["process_correct"].astype(int),
        df["structured_correct"].astype(int)
    )
    print(f"\nProcess vs Structured (Paired t-test):")
    print(f"  t-statistic: {t_stat2:.4f}")
    print(f"  p-value: {p_value2:.4f}")
    if p_value2 < 0.05:
        print(f"  Result: Significant difference (p < 0.05)")
    else:
        print(f"  Result: No significant difference (p >= 0.05)")

    # Effect size (Cohen's d)
    def cohens_d(x, y):
        nx = len(x)
        ny = len(y)
        dof = nx + ny - 2
        return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)

    effect_size = cohens_d(df["outcome_correct"].astype(int), df["process_correct"].astype(int))
    print(f"\nEffect Size (Cohen's d, Outcome vs Process): {effect_size:.4f}")
    if abs(effect_size) < 0.2:
        print("  Interpretation: Small effect")
    elif abs(effect_size) < 0.5:
        print("  Interpretation: Medium effect")
    else:
        print("  Interpretation: Large effect")

    return {
        "comparison_table": comparison_df.to_dict('records'),
        "paired_tests": {
            "outcome_vs_process": {"t_stat": t_stat, "p_value": p_value},
            "process_vs_structured": {"t_stat": t_stat2, "p_value": p_value2}
        },
        "effect_size_outcome_vs_process": effect_size
    }

def correlation_analysis(responses, interpretability):
    """Analyze correlations between metrics"""
    print("\n" + "=" * 70)
    print("CORRELATION ANALYSIS")
    print("=" * 70)

    if interpretability is None or "detailed" not in interpretability:
        print("Skipping correlation analysis (interpretability data not available)")
        return None

    # Extract detailed interpretability data and normalize structure
    detailed = interpretability["detailed"]
    records = {}

    # Helper to get/create record
    def get_record(entry):
        key = (entry["problem_id"], entry["condition"])
        if key not in records:
            records[key] = {
                "problem_id": entry["problem_id"],
                "condition": entry["condition"]
            }
        return records[key]

    if isinstance(detailed, dict):
        for entry in detailed.get("step_correctness", []):
            rec = get_record(entry)
            rec["step_correctness"] = entry.get("step_correctness_score")

        for entry in detailed.get("faithfulness", []):
            rec = get_record(entry)
            rec["faithfulness"] = entry.get("faithfulness_score")

        for entry in detailed.get("auditability", []):
            rec = get_record(entry)
            rec["clarity"] = entry.get("clarity_score")
            rec["verification_effort"] = entry.get("verification_effort_score")
            rec["coherence"] = entry.get("coherence_score")

        detailed_records = list(records.values())
    else:
        # Already in list form
        detailed_records = [dict(item) for item in detailed]

    # Build accuracy lookup per problem/condition
    def is_correct(row, condition):
        pred = row["extracted_answers"].get(condition)
        gt = row["ground_truth_numeric"]
        if pred is None or gt is None:
            return False
        try:
            return abs(pred - gt) < 1e-6
        except Exception:
            return False

    accuracy_lookup = {}
    for row in responses:
        for cond in ["process", "structured"]:
            accuracy_lookup[(row["problem_id"], cond)] = is_correct(row, cond)

    # Filter for process and structured conditions and attach accuracy
    process_structured = []
    for item in detailed_records:
        if item.get("condition") in ["process", "structured"]:
            item = dict(item)
            item["is_correct"] = int(accuracy_lookup.get((item["problem_id"], item["condition"]), 0))
            process_structured.append(item)

    if not process_structured:
        print("No interpretability data available yet for correlation analysis.")
        return None

    # Build metrics dataframe
    metrics_data = {
        "Accuracy": [],
        "Step Correctness": [],
        "Faithfulness": [],
        "Clarity": [],
        "Verification Effort": [],
        "Coherence": []
    }

    for item in process_structured:
        # Get accuracy for this problem (1 if correct, 0 if incorrect)
        is_correct = item.get("is_correct", 0.5)
        metrics_data["Accuracy"].append(is_correct)

        # Get interpretability metrics
        metrics_data["Step Correctness"].append(item["step_correctness"])
        metrics_data["Faithfulness"].append(item["faithfulness"])
        metrics_data["Clarity"].append(item["clarity"])
        metrics_data["Verification Effort"].append(item["verification_effort"])
        metrics_data["Coherence"].append(item["coherence"])

    # Create DataFrame
    df = pd.DataFrame(metrics_data)

    # Calculate correlation matrix (Pearson)
    print("\nPearson Correlation Matrix:")
    print("-" * 70)
    corr_matrix = df.corr()

    # Print formatted correlation matrix
    metric_names = list(metrics_data.keys())
    print("\n{:20s}".format(""), end="")
    for name in metric_names:
        print(f"{name[:12]:>12s}", end="")
    print()
    print("-" * (20 + 12 * len(metric_names)))

    for i, name1 in enumerate(metric_names):
        print(f"{name1[:20]:20s}", end="")
        for j, name2 in enumerate(metric_names):
            corr_val = corr_matrix.iloc[i, j]
            print(f"{corr_val:>12.3f}", end="")
        print()

    # Calculate Spearman correlations as well (for robustness)
    print("\n\nSpearman Rank Correlation Matrix:")
    print("-" * 70)
    spearman_matrix = df.corr(method='spearman')

    print("\n{:20s}".format(""), end="")
    for name in metric_names:
        print(f"{name[:12]:>12s}", end="")
    print()
    print("-" * (20 + 12 * len(metric_names)))

    for i, name1 in enumerate(metric_names):
        print(f"{name1[:20]:20s}", end="")
        for j, name2 in enumerate(metric_names):
            corr_val = spearman_matrix.iloc[i, j]
            print(f"{corr_val:>12.3f}", end="")
        print()

    # Identify strongest correlations with accuracy
    print("\n\nKey Correlations with Accuracy:")
    print("-" * 70)
    accuracy_corrs = corr_matrix["Accuracy"].drop("Accuracy").sort_values(ascending=False)

    for metric, corr_val in accuracy_corrs.items():
        # Calculate p-value for significance
        _, p_value = pearsonr(metrics_data["Accuracy"], metrics_data[metric])
        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
        print(f"  {metric:20s}: r = {corr_val:>6.3f}, p = {p_value:.4f} {sig}")

    print("\n  Significance codes: *** p<0.001, ** p<0.01, * p<0.05")

    # Return structured results
    correlations = {
        "pearson": corr_matrix.to_dict(),
        "spearman": spearman_matrix.to_dict(),
        "accuracy_correlations": {
            metric: {
                "pearson_r": float(corr_val),
                "p_value": float(pearsonr(metrics_data["Accuracy"], metrics_data[metric])[1])
            }
            for metric, corr_val in accuracy_corrs.items()
        },
        "n_samples": len(process_structured)
    }

    return correlations

def generate_summary_statistics(accuracy, interpretability, responses):
    """Generate comprehensive summary statistics table"""
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS TABLE")
    print("=" * 70)

    summary = {
        "conditions": ["outcome", "process", "structured"],
        "metrics": {}
    }

    # Accuracy
    for cond in summary["conditions"]:
        summary["metrics"][cond] = {
            "accuracy": accuracy.get(f"{cond}_accuracy", 0)
        }

    # Add interpretability if available
    if interpretability and "summary" in interpretability:
        for cond in ["process", "structured"]:
            if cond in interpretability["summary"]:
                interp = interpretability["summary"][cond]
                summary["metrics"][cond].update({
                    "step_correctness": interp["step_correctness"]["mean"],
                    "faithfulness": interp["faithfulness"]["mean"],
                    "clarity": interp["clarity"]["mean"],
                    "verification_effort": interp["verification_effort"]["mean"],
                    "coherence": interp["coherence"]["mean"]
                })

    # Print table
    print("\n{:15s} {:>12s} {:>12s} {:>12s}".format(
        "Metric", "Outcome", "Process", "Structured"
    ))
    print("-" * 55)

    print("{:15s} {:>12.2%} {:>12.2%} {:>12.2%}".format(
        "Accuracy",
        summary["metrics"]["outcome"]["accuracy"],
        summary["metrics"]["process"]["accuracy"],
        summary["metrics"]["structured"]["accuracy"]
    ))

    if "step_correctness" in summary["metrics"]["process"]:
        print("{:15s} {:>12s} {:>12.2f} {:>12.2f}".format(
            "Step Correct.",
            "N/A",
            summary["metrics"]["process"]["step_correctness"],
            summary["metrics"]["structured"]["step_correctness"]
        ))

        print("{:15s} {:>12s} {:>12.2f} {:>12.2f}".format(
            "Faithfulness",
            "N/A",
            summary["metrics"]["process"]["faithfulness"],
            summary["metrics"]["structured"]["faithfulness"]
        ))

        print("{:15s} {:>12s} {:>12.2f} {:>12.2f}".format(
            "Clarity",
            "N/A",
            summary["metrics"]["process"]["clarity"],
            summary["metrics"]["structured"]["clarity"]
        ))

        print("{:15s} {:>12s} {:>12.2f} {:>12.2f}".format(
            "Verif. Effort",
            "N/A",
            summary["metrics"]["process"]["verification_effort"],
            summary["metrics"]["structured"]["verification_effort"]
        ))

        print("{:15s} {:>12s} {:>12.2f} {:>12.2f}".format(
            "Coherence",
            "N/A",
            summary["metrics"]["process"]["coherence"],
            summary["metrics"]["structured"]["coherence"]
        ))

    return summary

def main():
    print("Phase 4: Statistical Analysis")
    print("=" * 70)

    # Load data
    accuracy, interpretability, responses = load_data()

    # Perform analyses
    accuracy_comparison = compare_accuracies(accuracy, responses)
    correlations = correlation_analysis(responses, interpretability)
    summary = generate_summary_statistics(accuracy, interpretability, responses)

    # Save results
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    results = {
        "accuracy_comparison": accuracy_comparison,
        "correlations": correlations,
        "summary_statistics": summary
    }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nStatistical analysis saved to: {output_path}")

if __name__ == "__main__":
    main()
