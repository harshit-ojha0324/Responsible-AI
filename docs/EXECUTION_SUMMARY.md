# Execution Summary: What, How, When

Quick reference guide for executing each phase of the project.

---

## Phase Execution Order

### Phase 1: ✅ COMPLETED
- Dataset preparation
- Response generation
- Answer extraction
- Basic accuracy metrics

**No action needed** - you've already done this!

---

## Phase 2: Error & Hallucination Analysis

### WHAT: Analyze error patterns and hallucinations in model responses

### HOW:

**Step 1**: Generate error analysis template
```bash
cd code
python phase2_error_analysis.py
```
**Output**: `data/processed/error_analysis.jsonl` (30-50 entries)

**Step 2**: Manual annotation (~2-3 hours)
- Open `data/processed/error_analysis.jsonl`
- For each entry, set `error_type` to one of:
  - `arithmetic`, `conceptual`, `comprehension`, `incomplete`, `formatting`
- Add notes in `error_notes`
- Save file

**Step 3**: Generate hallucination template
```bash
python phase2_hallucination_detection.py
```
**Output**: `data/processed/hallucination_analysis.jsonl` (50 entries)

**Step 4**: Manual annotation (~2-3 hours)
- Open `data/processed/hallucination_analysis.jsonl`
- For each entry:
  - Set `has_hallucination`: true/false
  - If true, list types in `hallucination_types`
  - Quote examples in `hallucination_examples`
- Save file

**Step 5**: Generate statistics
```bash
python phase2_error_analysis.py
python phase2_hallucination_detection.py
```
**Outputs**:
- `results/error_type_statistics.json`
- `results/hallucination_statistics.json`

### WHEN: Week 3 of timeline
**Time required**: ~6-8 hours total (2 hrs automated setup, 4-6 hrs annotation)

---

## Phase 3: Interpretability Metrics

### WHAT: Deep analysis of reasoning quality and faithfulness

### HOW:

**Step 1**: Select samples for annotation
```bash
python phase3_sample_selection.py
```
**Output**: `data/annotations/deep_annotation_sample.jsonl` (120 entries)

**Step 2**: Deep manual annotation (~10-20 hours) ⚠️ MOST INTENSIVE
- Open `data/annotations/deep_annotation_sample.jsonl`
- For EACH of 120 entries:
  1. Extract reasoning steps → `reasoning_steps` (list)
  2. Score each step 0-2 → `step_scores` (list)
  3. Extract expert steps → `expert_steps` (list)
  4. Score alignment 0-2 → `alignment_scores` (list)
  5. Rate clarity 1-5 → `clarity_score`
  6. Rate verification effort 1-5 → `verification_effort_score`
  7. Rate coherence 1-5 → `coherence_score`
- Save file

**Pro tip**: Do in batches of 10-15, take breaks every hour

**Step 3**: Calculate metrics
```bash
python phase3_calculate_interpretability.py
```
**Output**: `results/interpretability_metrics.json`

### WHEN: Week 4 of timeline
**Time required**: ~10-20 hours (mostly manual annotation)

**See**: `docs/ANNOTATION_GUIDE.md` for detailed rubrics and examples

---

## Phase 4: Statistical Analysis & Visualizations

### WHAT: Statistical tests, visualizations, and qualitative case studies

### HOW:

**Step 1**: Statistical analysis
```bash
python phase4_statistical_analysis.py
```
**Output**: `results/statistical_analysis.json`
- Paired t-tests
- Effect sizes (Cohen's d)
- Summary tables

**Step 2**: Generate visualizations
```bash
python phase4_visualizations.py
```
**Output**: `results/figures/*.png` (5 figures)
1. Accuracy comparison
2. Error distribution
3. Interpretability metrics
4. Hallucination rates
5. Summary comparison

**Step 3**: Qualitative failure analysis
```bash
python phase4_qualitative_analysis.py
```
**Output**: `data/processed/failure_case_analysis.jsonl`

**Step 4**: Manual case study review (~2-3 hours)
- Open `data/processed/failure_case_analysis.jsonl`
- Review ~40 identified failure cases
- Confirm patterns, add detailed analysis
- Extract key insights

### WHEN: Week 5 of timeline
**Time required**: ~3-5 hours (30 min automated, 2-3 hrs manual review)

---

## Phase 5: Report Generation

### WHAT: Generate comprehensive research report

### HOW:

**Step 1**: Generate report
```bash
python phase5_report_generator.py
```
**Output**: `docs/FINAL_REPORT.md` (~20-25 pages)

**Step 2**: Manual editing (~2-3 hours)
1. Review generated report
2. Add case study details from Phase 4
3. Refine legal implications section
4. Add references and citations
5. Proofread and polish

**Step 3**: Create presentation (not automated)
- 15-20 slides
- Use figures from Phase 4
- Practice 12-15 min delivery

### WHEN: Week 6 of timeline
**Time required**: ~3-5 hours (5 min generation, 2-3 hrs editing, 1-2 hrs presentation)

---

## Master Script: Run All Automated Parts

```bash
cd code
python run_all_phases.py
```

This script will:
1. Run Phase 2 templates (5 min)
2. **PAUSE** → You do Phase 2 annotations
3. Run Phase 3.1 sample selection (5 min)
4. **PAUSE** → You do Phase 3 deep annotations
5. Run Phase 3.2 metrics calculation (5 min)
6. Run Phase 4 analysis & visualizations (10 min)
7. Run Phase 5 report generation (5 min)

**Total automated time**: ~30 minutes
**Total manual time**: ~20-30 hours

---

## Critical Path Timeline

### Week 3 (Phase 2)
- **Monday**: Generate templates (30 min)
- **Tuesday-Thursday**: Complete annotations (6-8 hours)
- **Friday**: Generate statistics, review results (1 hour)

### Week 4 (Phase 3)
- **Monday**: Generate annotation templates (30 min)
- **Tuesday-Friday**: Deep annotations in batches (10-20 hours)
  - Batch 1: 30 entries (3-5 hours)
  - Batch 2: 30 entries (3-5 hours)
  - Batch 3: 30 entries (3-5 hours)
  - Batch 4: 30 entries (3-5 hours)
- **Friday evening**: Calculate metrics (5 min)

### Week 5 (Phase 4)
- **Monday**: Run statistical analysis (30 min)
- **Tuesday**: Generate visualizations (30 min)
- **Wednesday**: Generate failure cases (30 min)
- **Thursday-Friday**: Review and analyze cases (2-3 hours)

### Week 6 (Phase 5)
- **Monday**: Generate report (5 min)
- **Tuesday-Wednesday**: Edit and refine report (2-3 hours)
- **Thursday**: Create presentation (2 hours)
- **Friday**: Practice and finalize (1 hour)

---

## Daily Workflow Example (Phase 3 Deep Annotation)

**Goal**: Annotate 15 entries per session

**Session structure** (2 hours):
```
0:00 - 0:10   Setup, review rubrics
0:10 - 0:40   Annotate 5 entries (6 min each)
0:40 - 0:45   Break
0:45 - 1:15   Annotate 5 entries (6 min each)
1:15 - 1:20   Break
1:20 - 1:50   Annotate 5 entries (6 min each)
1:50 - 2:00   Save, quality check
```

**Progress tracking**:
- 120 total entries
- 15 per session
- 8 sessions needed
- 2-3 sessions per day → 3-4 days

---

## Quality Checkpoints

### After Phase 2
✅ Check that error types are distributed (not all one type)
✅ Verify hallucination examples are quoted correctly
✅ Statistics files generated successfully

### After Phase 3
✅ All 120 entries have non-null scores
✅ Step scores and alignment scores are lists (not single values)
✅ Likert scores are 1-5 (not 0-5)
✅ Metrics file generated successfully

### After Phase 4
✅ All 5 figures generated
✅ Figures display correctly (no errors)
✅ Statistical tests show p-values
✅ Case studies documented

### After Phase 5
✅ Report includes all sections
✅ Figures embedded correctly
✅ Legal implications section complete
✅ No placeholder text remains

---

## Troubleshooting Quick Reference

| Error | Solution |
|-------|----------|
| File not found | Run from `code/` directory |
| Import error | `pip install -r requirements.txt` |
| Empty results | Check that prerequisite phase completed |
| Annotation file corrupt | Validate JSON syntax |
| Figures won't generate | Ensure data files exist first |
| Script hangs | Check for infinite loops, add print statements |

---

## Final Checklist Before Submission

- [ ] All annotations completed
- [ ] All statistics files generated
- [ ] All 5 figures created
- [ ] Final report reviewed and edited
- [ ] Case studies documented
- [ ] References added
- [ ] Presentation created
- [ ] Code documented
- [ ] README updated
- [ ] Files organized

---

## Success Metrics

**Minimum Viable Project**:
- ✅ 100+ problems evaluated
- ✅ Accuracy comparison with stats
- ✅ 30+ problems annotated
- ✅ 10+ failure cases documented
- ✅ 15-page report

**Target Project** (your goal):
- ✅ 150-200 problems evaluated
- ✅ All metrics computed
- ✅ 60+ problems deeply annotated
- ✅ Publication-quality visualizations
- ✅ 20-25 page comprehensive report

**Stretch Goals**:
- ✅ Multi-model comparison
- ✅ Interactive dashboard
- ✅ Workshop submission

---

**You've got this! Follow the phases, take breaks, and maintain quality over speed.** 🎯

