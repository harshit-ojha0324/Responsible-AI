"""
Master Script: Run All Phases
Executes all phases of the analysis pipeline in sequence.
"""

import os
import sys

def print_header(phase_name):
    """Print phase header"""
    print("\n" + "=" * 70)
    print(f"  {phase_name}")
    print("=" * 70 + "\n")

def run_phase(script_name, phase_description):
    """Run a single phase script"""
    print_header(phase_description)

    script_path = os.path.join(os.path.dirname(__file__), script_name)

    if not os.path.exists(script_path):
        print(f"⚠️  Script not found: {script_name}")
        return False

    # Execute script
    import subprocess
    result = subprocess.run([sys.executable, script_path], capture_output=False)

    if result.returncode != 0:
        print(f"\n❌ Error in {script_name}")
        return False

    print(f"\n✓ {phase_description} completed successfully")
    return True

def main():
    print("\n" + "=" * 70)
    print("  PROCESS vs. OUTCOME SUPERVISION - COMPLETE ANALYSIS PIPELINE")
    print("=" * 70)

    phases = [
        # Phase 1 - Already completed by user
        # ("prepare_dataset.py", "Phase 1.1: Dataset Preparation"),
        # ("generate_responses.py", "Phase 1.2: Generate Model Responses"),
        # ("extract_answers.py", "Phase 1.3: Extract and Normalize Answers"),
        # ("calculate_metrics.py", "Phase 1.4: Calculate Basic Accuracy"),

        # Phase 2: Error Analysis and Hallucination Detection
        ("phase2_error_analysis.py", "Phase 2.1: Error Type Analysis"),
        ("phase2_hallucination_detection.py", "Phase 2.2: Hallucination Detection"),

        # Phase 3: Interpretability Metrics
        ("phase3_sample_selection.py", "Phase 3.1: Select Samples for Deep Annotation"),
        # Manual annotation step here - script will pause
        # ("phase3_calculate_interpretability.py", "Phase 3.2: Calculate Interpretability Metrics"),

        # Phase 4: Statistical Analysis and Visualizations
        ("phase4_statistical_analysis.py", "Phase 4.1: Statistical Analysis"),
        ("phase4_visualizations.py", "Phase 4.2: Create Visualizations"),
        ("phase4_qualitative_analysis.py", "Phase 4.3: Qualitative Failure Analysis"),

        # Phase 5: Report Generation
        ("phase5_report_generator.py", "Phase 5: Generate Final Report"),
    ]

    print("\nThis script will run the following phases:\n")
    for i, (script, description) in enumerate(phases, 1):
        print(f"{i}. {description}")

    print("\n⚠️  NOTE: Some phases require manual annotation:")
    print("   - After Phase 2.1, manually annotate error types")
    print("   - After Phase 2.2, manually annotate hallucinations")
    print("   - After Phase 3.1, manually complete deep annotations")
    print("\n")

    response = input("Continue with automated phases? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    # Run Phase 2 and 3.1 (data preparation)
    success = True
    for script, description in phases[:3]:
        if not run_phase(script, description):
            success = False
            break

    if not success:
        print("\n❌ Pipeline stopped due to errors")
        return

    print("\n" + "=" * 70)
    print("  MANUAL ANNOTATION REQUIRED")
    print("=" * 70)
    print("\nPlease complete the following manual annotation steps:")
    print("\n1. Error Type Annotation:")
    print("   - Open: data/processed/error_analysis.jsonl")
    print("   - Annotate error_type for each entry")
    print("   - Save the file")
    print("\n2. Hallucination Annotation:")
    print("   - Open: data/processed/hallucination_analysis.jsonl")
    print("   - Set has_hallucination (true/false) for each entry")
    print("   - Add hallucination_types if applicable")
    print("   - Save the file")
    print("\n3. Deep Annotation (Interpretability):")
    print("   - Open: data/annotations/deep_annotation_sample.jsonl")
    print("   - Complete all annotation fields (steps, scores, etc.)")
    print("   - See docs/ANNOTATION_GUIDE.md for detailed instructions")
    print("   - Save the file")
    print("\n" + "=" * 70)

    response = input("\nHave you completed all annotations? (y/n): ")
    if response.lower() != 'y':
        print("\nPipeline paused. Run this script again after completing annotations.")
        return

    # Run interpretability calculation
    if not run_phase("phase3_calculate_interpretability.py",
                     "Phase 3.2: Calculate Interpretability Metrics"):
        print("\n❌ Pipeline stopped due to errors")
        return

    # Run Phase 4 and 5
    for script, description in phases[3:]:
        if not run_phase(script, description):
            success = False
            break

    if success:
        print("\n" + "=" * 70)
        print("  ✓ ALL PHASES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated outputs:")
        print("  📊 Results: results/")
        print("  📈 Figures: results/figures/")
        print("  📄 Report: docs/FINAL_REPORT.md")
        print("\nNext steps:")
        print("  1. Review the final report")
        print("  2. Add case study details")
        print("  3. Proofread and refine")
        print("  4. Create presentation")
    else:
        print("\n❌ Pipeline completed with errors. Please review output.")

if __name__ == "__main__":
    main()
