# Class Presentation Deck Plan

## Purpose
- Explain the study to the class: motivation, methods, key findings, and why it matters for Responsible AI & law.

## Slide Outline (15-20 slides, ~12-15 min)
1. **Title & Team** — project name, team members, date.
2. **Motivation** — why process vs outcome supervision matters; link to trustworthy AI.
3. **Research Question** — what we are testing (factual reliability + interpretability).
4. **Study Design** — three conditions (Outcome, Process, Structured Process) and prompts.
5. **Dataset** — GSM8K overview; sample size; why chosen.
6. **Model & Setup** — model used, API setup, sampling, cost/rate limits.
7. **Pipeline Overview** — data flow from prompts ? responses ? extraction ? metrics.
8. **Accuracy Results** — bar chart (01_accuracy_comparison.png) and key numbers.
9. **Interpretability Metrics** — step correctness, faithfulness, auditability highlights (03_interpretability_metrics.png).
10. **Correlations** — faithfulness vs accuracy (06_correlation_heatmap.png & 07_faithfulness_vs_accuracy.png); main takeaways.
11. **Qualitative Case** — one illustrative failure/success example (from failure_case_analysis.jsonl).
12. **Error/Hallucination Notes** — what we checked or plan to add (optional if not finalized).
13. **Legal/Policy Lens** — GDPR Art.22, EU AI Act transparency; why process traces help auditing.
14. **Limitations** — sample size, manual annotation effort, model choice.
15. **Lessons & Recommendations** — when to favor process supervision; cautions about unfaithful reasoning.
16. **Next Steps** — add more problems/models, polish report, collect more annotations.
17. **Q&A Backup Slides** — appendix for prompt templates, rubric snippets, additional figures.

## Figures to Include
- 01_accuracy_comparison.png
- 03_interpretability_metrics.png
- 05_summary_comparison.png
- 06_correlation_heatmap.png
- 07_faithfulness_vs_accuracy.png
- (Optional) 02_error_distribution.png / 04_hallucination_rates.png if stats available.

## Talking Points
- Emphasize that process supervision improves diagnosability and correlates strongly with accuracy.
- Structured prompts boost clarity/auditability but may not always improve faithfulness.
- Legal angle: process traces support transparency and human oversight; beware “illusion of explainability.”

## Prep Checklist
- Export figures from `results/figures/` into slides.
- Pull key numbers from `results/accuracy_metrics.json`, `interpretability_metrics.json`, `statistical_analysis.json`.
- Add one short case study narrative (problem ? model steps ? takeaway).
- Keep slides visual; reserve detailed rubrics for backup.
