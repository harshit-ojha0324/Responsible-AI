"""
Phase 5: Report Generator
Generates a comprehensive markdown report with all findings.
"""

import json
import os
from datetime import datetime

def load_all_results():
    """Load all analysis results"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    results = {}

    # Load accuracy metrics
    try:
        with open(os.path.join(base_dir, "../results/accuracy_metrics.json"), "r") as f:
            results["accuracy"] = json.load(f)
    except FileNotFoundError:
        results["accuracy"] = None

    # Load interpretability metrics
    try:
        with open(os.path.join(base_dir, "../results/interpretability_metrics.json"), "r") as f:
            results["interpretability"] = json.load(f)
    except FileNotFoundError:
        results["interpretability"] = None

    # Load statistical analysis
    try:
        with open(os.path.join(base_dir, "../results/statistical_analysis.json"), "r") as f:
            results["statistics"] = json.load(f)
    except FileNotFoundError:
        results["statistics"] = None

    # Load error analysis
    try:
        with open(os.path.join(base_dir, "../results/error_type_statistics.json"), "r") as f:
            results["errors"] = json.load(f)
    except FileNotFoundError:
        results["errors"] = None

    # Load hallucination analysis
    try:
        with open(os.path.join(base_dir, "../results/hallucination_statistics.json"), "r") as f:
            results["hallucinations"] = json.load(f)
    except FileNotFoundError:
        results["hallucinations"] = None

    return results

def generate_executive_summary(results):
    """Generate executive summary section"""
    summary = """## Executive Summary

This study compares **process-based supervision** (step-by-step reasoning) versus **outcome-based supervision** (final answers only) for LLM reasoning tasks, with a focus on implications for legal and regulatory compliance.

### Key Findings

"""

    # Add accuracy findings
    if results["accuracy"]:
        acc = results["accuracy"]
        outcome_acc = acc.get("outcome_accuracy", 0) * 100
        process_acc = acc.get("process_accuracy", 0) * 100
        structured_acc = acc.get("structured_accuracy", 0) * 100

        summary += f"""#### 1. Factual Reliability (Accuracy)

- **Outcome Supervision**: {outcome_acc:.1f}% accuracy
- **Process Supervision**: {process_acc:.1f}% accuracy
- **Structured Process**: {structured_acc:.1f}% accuracy

"""

    # Add interpretability findings if available
    if results["interpretability"] and "summary" in results["interpretability"]:
        summary += """#### 2. Interpretability Metrics

Process-based supervision enables deeper analysis of reasoning quality:

"""
        interp = results["interpretability"]["summary"]
        for cond in ["process", "structured"]:
            if cond in interp:
                summary += f"""- **{cond.capitalize()}**:
  - Step Correctness: {interp[cond]['step_correctness']['mean']:.2f}/2.0
  - Faithfulness: {interp[cond]['faithfulness']['mean']:.2f}/2.0
  - Clarity: {interp[cond]['clarity']['mean']:.2f}/5.0
  - Verification Effort: {interp[cond]['verification_effort']['mean']:.2f}/5.0

"""

    # Add hallucination findings if available
    if results["hallucinations"]:
        hall = results["hallucinations"]
        summary += f"""#### 3. Hallucination Rate

- Overall hallucination rate in reasoning traces: {hall.get('hallucination_rate', 0):.1f}%
- This has important implications for trustworthiness of explanations

"""

    summary += """### Implications for Responsible AI and Law

The findings have significant implications for:
- **GDPR Article 22**: Right to explanation for automated decision-making
- **EU AI Act**: Transparency and auditability requirements
- **Algorithmic Accountability**: Meaningful human oversight capabilities

"""

    return summary

def generate_methodology_section():
    """Generate methodology section"""
    return """## Methodology

### Experimental Design

This study employed a controlled experimental design comparing three conditions:

1. **Outcome Supervision**: Model provides only final numerical answer
2. **Process Supervision**: Model shows step-by-step reasoning (Chain-of-Thought)
3. **Structured Process**: Model uses explicit step formatting

### Dataset

- **Source**: GSM8K (Grade School Math 8K)
- **Sample Size**: 150-200 math problems
- **Stratification**: Problems sampled to ensure diversity

### Metrics

#### Factual Reliability
- Final answer accuracy (compared to ground truth)
- Error type classification
- Hallucination rate in reasoning

#### Interpretability
- **Step Correctness Score**: Mean quality of reasoning steps (0-2 scale)
- **Faithfulness Score**: Alignment with expert solution (0-2 scale)
- **Auditability Scores**: Clarity, verification effort, coherence (1-5 Likert scale)

### Annotation Process

- 50-70 problems selected for deep annotation
- Stratified by correctness and condition
- Multiple raters for inter-rater reliability (where applicable)

"""

def generate_results_section(results):
    """Generate results section"""
    section = """## Results

### Accuracy Comparison

"""

    if results["accuracy"]:
        acc = results["accuracy"]
        section += f"""| Condition | Accuracy |
|-----------|----------|
| Outcome | {acc.get('outcome_accuracy', 0)*100:.1f}% |
| Process | {acc.get('process_accuracy', 0)*100:.1f}% |
| Structured | {acc.get('structured_accuracy', 0)*100:.1f}% |

"""

    # Statistical significance
    if results["statistics"] and "accuracy_comparison" in results["statistics"]:
        stats = results["statistics"]["accuracy_comparison"]
        if "paired_tests" in stats:
            section += """### Statistical Significance

"""
            tests = stats["paired_tests"]
            if "outcome_vs_process" in tests:
                t = tests["outcome_vs_process"]
                section += f"""**Outcome vs Process**: t={t['t_stat']:.4f}, p={t['p_value']:.4f}
"""

    section += """\n![Accuracy Comparison](../results/figures/01_accuracy_comparison.png)

"""

    # Interpretability results
    if results["interpretability"]:
        section += """### Interpretability Metrics

![Interpretability Metrics](../results/figures/03_interpretability_metrics.png)

"""

    # Error analysis
    if results["errors"]:
        section += """### Error Type Distribution

![Error Distribution](../results/figures/02_error_distribution.png)

"""

    # Hallucinations
    if results["hallucinations"]:
        section += """### Hallucination Analysis

![Hallucination Rates](../results/figures/04_hallucination_rates.png)

"""

    return section

def generate_legal_implications():
    """Generate legal and regulatory implications section"""
    return """## Legal and Regulatory Implications

### GDPR Article 22: Right to Explanation

**Article 22** grants individuals the right not to be subject to decisions based solely on automated processing, including profiling, with legal or similarly significant effects. For such systems, **meaningful information about the logic involved** must be provided.

#### Implications of Our Findings:

- **If Process Supervision Shows Higher Reliability**: Process-based explanations can support GDPR compliance by providing meaningful insight into the decision-making logic
- **If Reasoning Contains Hallucinations**: Relying on potentially unfaithful reasoning traces could **violate** the spirit of Article 22 by providing misleading explanations
- **Recommendation**: Organizations must verify that reasoning traces are factually accurate before presenting them as "explanations"

### EU AI Act: Transparency Requirements

The **EU AI Act** (Articles 13, 52) requires high-risk AI systems to be designed with appropriate transparency, enabling users to interpret outputs and use them appropriately.

#### Implications:

- **Auditability**: Process supervision enables independent verification of reasoning
- **Interpretability Metrics**: Step correctness and faithfulness scores provide quantitative measures of explanation quality
- **Risk**: Low-quality reasoning (hallucinations, errors) could undermine transparency goals

### U.S. Administrative Procedure Act § 706

Federal agencies must provide reasoned explanations for decisions. Courts can set aside agency actions found to be "arbitrary and capricious."

#### Implications:

- **Algorithmic Decisions**: If agencies use LLMs, reasoning traces could support judicial review
- **Faithfulness Matters**: Unfaithful reasoning could expose agencies to legal challenges
- **Standard**: Reasoning must be consistent, logical, and grounded in facts

### Broader Implications for Algorithmic Accountability

#### Strengths of Process Supervision:
1. ✅ Enables ex-post auditability
2. ✅ Supports meaningful human oversight
3. ✅ Provides documentation trail
4. ✅ Facilitates bias detection

#### Risks of Process Supervision:
1. ⚠️ Hallucinations create "illusion of explainability"
2. ⚠️ False confidence in incorrect reasoning
3. ⚠️ May not reflect actual model decision process
4. ⚠️ Adds complexity without guaranteed accuracy

### Policy Recommendations

1. **Mandate Verification**: Require independent verification of reasoning quality before using as legal explanation
2. **Establish Standards**: Define minimum thresholds for faithfulness and step correctness
3. **Human-in-the-Loop**: Require human review for high-stakes decisions
4. **Disclosure**: Clearly communicate that reasoning may not perfectly reflect model internals
5. **Continuous Monitoring**: Track hallucination rates and reasoning quality over time

"""

def generate_limitations():
    """Generate limitations section"""
    return """## Limitations

1. **Limited Scope**: Study focused on math problems (GSM8K); results may not generalize to other domains
2. **Single Model**: Analysis based on one model; different models may show different patterns
3. **Annotation Subjectivity**: Some metrics require subjective human judgment
4. **Sample Size**: Annotated subset (50-70 problems) limits statistical power for some analyses
5. **Faithfulness Measurement**: Alignment with expert solution is a proxy, not direct measure of model's actual reasoning process
6. **Temporal Limitations**: Models evolve rapidly; findings reflect current model capabilities

"""

def generate_future_work():
    """Generate future work section"""
    return """## Future Work

1. **Multi-Domain Evaluation**: Extend to legal reasoning, medical diagnosis, financial analysis
2. **Model Comparison**: Compare across different model families (GPT, Claude, Llama, etc.)
3. **Automated Faithfulness**: Develop automated methods to detect reasoning hallucinations
4. **Intervention Studies**: Test if highlighting errors improves human decision-making
5. **Longitudinal Analysis**: Track how reasoning quality changes with model updates
6. **Legal Case Studies**: Apply framework to real legal AI systems
7. **Regulatory Compliance Testing**: Develop compliance test suites for AI Act, GDPR

"""

def generate_conclusions(results):
    """Generate conclusions"""
    conclusion = """## Conclusions

This study provides empirical evidence on the tradeoffs between process-based and outcome-based supervision for LLM reasoning, with direct implications for legal and regulatory compliance.

### Key Takeaways:

"""

    if results["accuracy"]:
        acc = results["accuracy"]
        outcome_acc = acc.get("outcome_accuracy", 0) * 100
        process_acc = acc.get("process_accuracy", 0) * 100

        if abs(outcome_acc - process_acc) < 2:
            conclusion += """1. **Accuracy**: No significant difference in final answer accuracy between conditions
"""
        elif process_acc > outcome_acc:
            conclusion += """1. **Accuracy**: Process supervision shows higher accuracy
"""
        else:
            conclusion += """1. **Accuracy**: Outcome supervision shows higher accuracy
"""

    conclusion += """2. **Interpretability**: Process supervision enables deeper analysis of reasoning quality
3. **Hallucinations**: Reasoning traces may contain factual errors even when final answer is correct
4. **Legal Implications**: Process-based explanations can support compliance but require verification

### For Policymakers:

- Establish standards for reasoning quality in high-stakes AI systems
- Require validation of explanation faithfulness
- Balance transparency benefits against hallucination risks

### For Practitioners:

- Implement multi-layered verification for process-based explanations
- Monitor reasoning quality continuously
- Design human-AI collaboration workflows that leverage strengths of both

### For Researchers:

- Develop better measures of explanation faithfulness
- Investigate automated hallucination detection
- Study impact of explanations on human decision-making

---

**This research contributes to the growing body of work on Responsible AI and algorithmic accountability, providing concrete evidence to inform policy and practice.**

"""

    return conclusion

def generate_full_report(results):
    """Generate complete markdown report"""
    report = f"""# Process vs. Outcome Supervision for Trustworthy and Interpretable LLM Reasoning

**A Comprehensive Evaluation Study**

*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

"""

    report += generate_executive_summary(results)
    report += "\n---\n\n"
    report += generate_methodology_section()
    report += "\n---\n\n"
    report += generate_results_section(results)
    report += "\n---\n\n"
    report += generate_legal_implications()
    report += "\n---\n\n"
    report += """## Qualitative Analysis

*This section should include detailed case studies from the failure case analysis.*

Refer to `failure_case_analysis.jsonl` for documented examples of:
- Correct answers with flawed reasoning
- Incorrect answers with sound reasoning approaches
- Hallucinations with high confidence
- Incomplete reasoning patterns

Key insights and representative examples should be integrated here after manual review.

---

"""
    report += generate_limitations()
    report += "\n---\n\n"
    report += generate_future_work()
    report += "\n---\n\n"
    report += generate_conclusions(results)

    # Appendix
    report += """\n---

## Appendices

### Appendix A: Complete Annotation Rubrics

See `docs/annotation_rubrics.md` for detailed rubrics.

### Appendix B: Prompt Templates

See `code/prompts.py` for exact prompts used.

### Appendix C: Statistical Details

Full statistical analysis available in `results/statistical_analysis.json`.

### Appendix D: Code Repository

Complete code and data: [GitHub Repository Link]

"""

    return report

def main():
    print("Phase 5: Generating Final Report")
    print("=" * 70)

    # Load all results
    results = load_all_results()

    # Check what's available
    print("\nAvailable results:")
    for key, value in results.items():
        status = "✓" if value is not None else "✗"
        print(f"  {status} {key}")

    # Generate report
    report = generate_full_report(results)

    # Save report
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "../docs/FINAL_REPORT.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Final report generated: {output_path}")
    print(f"\nReport length: {len(report.split())} words")

    print("\nNext steps:")
    print("1. Review and edit the generated report")
    print("2. Add case studies from qualitative analysis")
    print("3. Proofread and refine legal implications section")
    print("4. Add references and citations")
    print("5. Create presentation slides")

if __name__ == "__main__":
    main()
