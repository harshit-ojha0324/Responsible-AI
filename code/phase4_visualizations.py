"""
Phase 4: Visualizations
Creates comprehensive visualizations including:
1. Accuracy comparison bar chart
2. Error type distribution (stacked bars)
3. Step correctness distribution (box plots)
4. Faithfulness vs. Accuracy scatter plot
5. Verification effort comparison
6. Correlation heatmap (all metrics)
"""

import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
FIGURE_DIR = "../results/figures"
DPI = 300  # High resolution for publication

# Color scheme
COLORS = {
    'outcome': '#FF6B6B',
    'process': '#4ECDC4',
    'structured': '#95E1D3'
}

def setup_plot_style():
    """Set up consistent plotting style"""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12

def load_all_data():
    """Load all necessary data"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Accuracy metrics
    with open(os.path.join(base_dir, "../results/accuracy_metrics.json"), "r") as f:
        accuracy = json.load(f)

    # Statistical analysis
    try:
        with open(os.path.join(base_dir, "../results/statistical_analysis.json"), "r") as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = None

    # Interpretability metrics
    try:
        with open(os.path.join(base_dir, "../results/interpretability_metrics.json"), "r") as f:
            interpretability = json.load(f)
    except FileNotFoundError:
        interpretability = None

    # Error analysis
    try:
        with open(os.path.join(base_dir, "../results/error_type_statistics.json"), "r") as f:
            errors = json.load(f)
    except FileNotFoundError:
        errors = None

    # Hallucination analysis
    try:
        with open(os.path.join(base_dir, "../results/hallucination_statistics.json"), "r") as f:
            hallucinations = json.load(f)
    except FileNotFoundError:
        hallucinations = None

    return accuracy, stats, interpretability, errors, hallucinations

def normalize_interpretability_records(detailed):
    """Normalize interpretability 'detailed' section to list of records with common keys"""
    records = {}

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
    else:
        for entry in detailed:
            rec = get_record(entry)
            rec.update(entry)

    return list(records.values())

def plot_accuracy_comparison(accuracy_data, output_dir):
    """Create accuracy comparison bar chart"""
    print("Creating accuracy comparison chart...")

    conditions = ["Outcome", "Process", "Structured"]
    accuracies = [
        accuracy_data.get("outcome_accuracy", 0) * 100,
        accuracy_data.get("process_accuracy", 0) * 100,
        accuracy_data.get("structured_accuracy", 0) * 100
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        conditions,
        accuracies,
        color=[COLORS['outcome'], COLORS['process'], COLORS['structured']],
        edgecolor='black',
        linewidth=1.5
    )

    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_ylabel('Accuracy (%)', fontsize=14)
    ax.set_xlabel('Condition', fontsize=14)
    ax.set_title('Final Answer Accuracy by Condition', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_accuracy_comparison.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 01_accuracy_comparison.png")

def plot_error_distribution(error_data, output_dir):
    """Create error type distribution stacked bar chart"""
    if error_data is None:
        print("Skipping error distribution (data not available)")
        return

    print("Creating error type distribution chart...")

    # Prepare data
    conditions = list(error_data.get("by_condition", {}).keys())

    if not conditions:
        print("  ⚠ No error data available yet")
        return

    error_types = set()
    for cond_data in error_data["by_condition"].values():
        error_types.update(cond_data.keys())

    error_types = sorted(list(error_types))

    # Build matrix
    data = []
    for error_type in error_types:
        row = [error_data["by_condition"].get(cond, {}).get(error_type, 0)
               for cond in conditions]
        data.append(row)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(conditions))
    width = 0.6

    bottom = np.zeros(len(conditions))
    colors_palette = sns.color_palette("Set2", len(error_types))

    for i, (error_type, values) in enumerate(zip(error_types, data)):
        ax.bar(x, values, width, label=error_type, bottom=bottom,
               color=colors_palette[i], edgecolor='black', linewidth=0.5)
        bottom += values

    ax.set_xlabel('Condition', fontsize=14)
    ax.set_ylabel('Number of Errors', fontsize=14)
    ax.set_title('Error Type Distribution by Condition', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in conditions])
    ax.legend(title='Error Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_error_distribution.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 02_error_distribution.png")

def plot_interpretability_metrics(interp_data, output_dir):
    """Create interpretability metrics comparison"""
    if interp_data is None or "summary" not in interp_data:
        print("Skipping interpretability plots (data not available)")
        return

    print("Creating interpretability metrics chart...")

    summary = interp_data["summary"]
    conditions = [c for c in ["process", "structured"] if c in summary]

    if not conditions:
        print("  ⚠ No interpretability data available yet")
        return

    metrics = ["step_correctness", "faithfulness", "clarity", "verification_effort", "coherence"]
    metric_labels = ["Step\nCorrectness", "Faithfulness", "Clarity", "Verification\nEffort", "Coherence"]

    # Extract data
    data = {cond: [] for cond in conditions}
    errors = {cond: [] for cond in conditions}

    for metric in metrics:
        for cond in conditions:
            if metric in summary[cond]:
                data[cond].append(summary[cond][metric]["mean"])
                errors[cond].append(summary[cond][metric]["std"])
            else:
                data[cond].append(0)
                errors[cond].append(0)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(metrics))
    width = 0.35

    for i, cond in enumerate(conditions):
        offset = width * (i - 0.5)
        ax.bar(x + offset, data[cond], width,
               label=cond.capitalize(),
               color=COLORS[cond],
               yerr=errors[cond],
               capsize=5,
               edgecolor='black',
               linewidth=1)

    ax.set_xlabel('Metric', fontsize=14)
    ax.set_ylabel('Score', fontsize=14)
    ax.set_title('Interpretability Metrics Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_interpretability_metrics.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 03_interpretability_metrics.png")

def plot_hallucination_rates(hall_data, output_dir):
    """Create hallucination rate comparison"""
    if hall_data is None:
        print("Skipping hallucination plot (data not available)")
        return

    print("Creating hallucination rates chart...")

    by_condition = hall_data.get("by_condition", {})

    if not by_condition:
        print("  ⚠ No hallucination data available yet")
        return

    conditions = sorted(by_condition.keys())
    rates = [by_condition[c]["rate"] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(
        [c.capitalize() for c in conditions],
        rates,
        color=[COLORS[c] for c in conditions],
        edgecolor='black',
        linewidth=1.5
    )

    # Add value labels
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_ylabel('Hallucination Rate (%)', fontsize=14)
    ax.set_xlabel('Condition', fontsize=14)
    ax.set_title('Hallucination Rate by Condition', fontsize=16, fontweight='bold')
    ax.set_ylim(0, max(rates) * 1.2 if rates else 100)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "04_hallucination_rates.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 04_hallucination_rates.png")

def plot_summary_comparison(accuracy, interp_data, output_dir):
    """Create comprehensive summary comparison"""
    print("Creating summary comparison chart...")

    conditions = ["outcome", "process", "structured"]
    metrics_data = {
        "Accuracy": [
            accuracy.get("outcome_accuracy", 0) * 100,
            accuracy.get("process_accuracy", 0) * 100,
            accuracy.get("structured_accuracy", 0) * 100
        ]
    }

    # Add interpretability metrics if available
    if interp_data and "summary" in interp_data:
        for metric_name, metric_key in [
            ("Step Correctness", "step_correctness"),
            ("Faithfulness", "faithfulness"),
            ("Clarity", "clarity")
        ]:
            values = []
            for cond in conditions:
                if cond == "outcome":
                    values.append(0)  # N/A
                elif cond in interp_data["summary"] and metric_key in interp_data["summary"][cond]:
                    # Normalize to 0-100 scale
                    mean_val = interp_data["summary"][cond][metric_key]["mean"]
                    # Step correctness and faithfulness are 0-2, clarity is 1-5
                    if metric_key in ["step_correctness", "faithfulness"]:
                        values.append(mean_val / 2 * 100)
                    else:  # clarity, etc are 1-5
                        values.append((mean_val - 1) / 4 * 100)
                else:
                    values.append(0)

            metrics_data[metric_name] = values

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(14, 7))

    metrics = list(metrics_data.keys())
    x = np.arange(len(conditions))
    width = 0.8 / len(metrics)

    for i, metric in enumerate(metrics):
        offset = width * (i - len(metrics)/2 + 0.5)
        ax.bar(x + offset, metrics_data[metric], width,
               label=metric,
               edgecolor='black',
               linewidth=0.5)

    ax.set_xlabel('Condition', fontsize=14)
    ax.set_ylabel('Score (normalized to 0-100)', fontsize=14)
    ax.set_title('Comprehensive Metrics Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in conditions])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "05_summary_comparison.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 05_summary_comparison.png")

def plot_correlation_heatmap(interp_data, accuracy, output_dir):
    """Create correlation heatmap for all metrics"""
    if interp_data is None or "detailed" not in interp_data:
        print("Skipping correlation heatmap (interpretability data not available)")
        return

    print("Creating correlation heatmap...")

    # Prepare data for correlations
    detailed_records = normalize_interpretability_records(interp_data["detailed"])

    # Filter for process and structured conditions
    process_structured = [item for item in detailed_records
                          if item.get("condition") in ["process", "structured"]]

    if not process_structured:
        print("  ⚠ No interpretability data available yet")
        return

    # Extract metrics for correlation analysis
    metrics_dict = {
        "Accuracy": [],
        "Step Correctness": [],
        "Faithfulness": [],
        "Clarity": [],
        "Verification Effort": [],
        "Coherence": []
    }

    for item in process_structured:
        # Check if this problem has accuracy data
        # For now, use 1 if correct, 0 if incorrect (binary)
        is_correct = item.get("is_correct", 0.5)  # Default to 0.5 if unknown
        metrics_dict["Accuracy"].append(is_correct)

        metrics_dict["Step Correctness"].append(item["step_correctness"])
        metrics_dict["Faithfulness"].append(item["faithfulness"])
        metrics_dict["Clarity"].append(item["clarity"])
        metrics_dict["Verification Effort"].append(item["verification_effort"])
        metrics_dict["Coherence"].append(item["coherence"])

    # Create DataFrame
    df = pd.DataFrame(metrics_dict)

    # Calculate correlation matrix
    corr_matrix = df.corr()

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, fmt='.2f', ax=ax)

    ax.set_title('Correlation Heatmap: All Metrics', fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "06_correlation_heatmap.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 06_correlation_heatmap.png")

def plot_faithfulness_vs_accuracy(interp_data, output_dir):
    """Create scatter plot of faithfulness vs accuracy"""
    if interp_data is None or "detailed" not in interp_data:
        print("Skipping faithfulness vs accuracy plot (interpretability data not available)")
        return

    print("Creating faithfulness vs accuracy scatter plot...")

    detailed_records = normalize_interpretability_records(interp_data["detailed"])

    # Filter for process and structured conditions
    process_structured = [item for item in detailed_records
                          if item.get("condition") in ["process", "structured"]]

    if not process_structured:
        print("  ⚠ No interpretability data available yet")
        return

    # Extract data by condition
    conditions_data = {"process": {"faithfulness": [], "correct": []},
                       "structured": {"faithfulness": [], "correct": []}}

    for item in process_structured:
        cond = item.get("condition")
        faithfulness = item.get("faithfulness")
        is_correct = item.get("is_correct", 0.5)  # 1 if correct, 0 if not

        conditions_data[cond]["faithfulness"].append(faithfulness)
        conditions_data[cond]["correct"].append(is_correct)

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 7))

    for cond in ["process", "structured"]:
        if conditions_data[cond]["faithfulness"]:
            x = conditions_data[cond]["faithfulness"]
            y = conditions_data[cond]["correct"]

            # Add jitter to y-axis for better visualization of binary outcomes
            y_jittered = [val + np.random.normal(0, 0.02) for val in y]

            ax.scatter(x, y_jittered,
                      label=cond.capitalize(),
                      color=COLORS[cond],
                      s=100, alpha=0.6, edgecolors='black', linewidth=1)

    ax.set_xlabel('Faithfulness Score (0-2)', fontsize=14)
    ax.set_ylabel('Correct Answer (0=No, 1=Yes)', fontsize=14)
    ax.set_title('Faithfulness vs. Answer Correctness', fontsize=16, fontweight='bold')
    ax.set_ylim(-0.2, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Incorrect', 'Correct'])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "07_faithfulness_vs_accuracy.png"), dpi=DPI, bbox_inches='tight')
    plt.close()

    print("  ✓ Saved: 07_faithfulness_vs_accuracy.png")

def main():
    print("Phase 4: Creating Visualizations")
    print("=" * 70)

    setup_plot_style()

    # Create output directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, FIGURE_DIR)
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    accuracy, stats, interpretability, errors, hallucinations = load_all_data()

    # Create plots
    plot_accuracy_comparison(accuracy, output_dir)
    plot_error_distribution(errors, output_dir)
    plot_interpretability_metrics(interpretability, output_dir)
    plot_hallucination_rates(hallucinations, output_dir)
    plot_summary_comparison(accuracy, interpretability, output_dir)
    plot_correlation_heatmap(interpretability, accuracy, output_dir)
    plot_faithfulness_vs_accuracy(interpretability, output_dir)

    print(f"\n✓ All visualizations saved to: {output_dir}")
    print("\nGenerated figures:")
    print("  01_accuracy_comparison.png")
    print("  02_error_distribution.png")
    print("  03_interpretability_metrics.png")
    print("  04_hallucination_rates.png")
    print("  05_summary_comparison.png")
    print("  06_correlation_heatmap.png")
    print("  07_faithfulness_vs_accuracy.png")

if __name__ == "__main__":
    main()
