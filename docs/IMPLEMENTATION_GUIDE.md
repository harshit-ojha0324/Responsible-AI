# Implementation Guide: Process vs. Outcome Supervision

Complete guide for implementing all phases of the research project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [File Structure](#file-structure)
5. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Goal**: Compare process-based supervision (step-by-step reasoning) vs. outcome-based supervision (final answers only) in terms of:
- Factual reliability (accuracy)
- Interpretability and auditability
- Implications for legal/regulatory compliance

**Timeline**: 6 weeks (see `project_implementation_plan_extracted.md`)

**Scope**: Evaluation study on 150-200 math problems

---

## Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. API Configuration

Create `.env` file in project root:

```bash
# For OpenAI
OPENAI_API_KEY=your_api_key_here

# For Anthropic
ANTHROPIC_API_KEY=your_api_key_here

# For OpenRouter (Grok, etc.)
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Directory Structure

Ensure the following directories exist:

```
resp_ai/
├── code/                  # All Python scripts
├── data/
│   ├── raw/              # Raw model responses
│   ├── processed/        # Processed data with extracted answers
│   └── annotations/      # Manual annotation files
├── docs/                 # Documentation and reports
├── results/              # Analysis results and metrics
│   └── figures/          # Visualizations
└── .env                  # API keys (DO NOT COMMIT)
```

---

## Phase-by-Phase Implementation

## ✅ Phase 1: Setup and Data Collection (COMPLETED)

You have already completed:
- Dataset preparation (`prepare_dataset.py`)
- Response generation (`generate_responses.py`)
- Answer extraction (`extract_answers.py`)
- Basic accuracy calculation (`calculate_metrics.py`)

**Outputs**:
- `data/dataset_manifest.csv` - Selected problems
- `data/raw/responses.jsonl` - Raw model responses
- `data/processed/responses_with_answers.jsonl` - Extracted answers
- `results/accuracy_metrics.json` - Accuracy metrics

---

## 📊 Phase 2: Error Analysis and Hallucination Detection

### Phase 2.1: Error Type Analysis

**Script**: `code/phase2_error_analysis.py`

**What it does**:
- Samples incorrect responses (30-50 per condition)
- Creates annotation template for manual error classification

**How to run**:
```bash
cd code
python phase2_error_analysis.py
```

**Output**: `data/processed/error_analysis.jsonl`

**Manual Step**: Open the output file and annotate each error with one of:
- `arithmetic`: Calculation mistake
- `conceptual`: Wrong approach or formula
- `comprehension`: Misunderstood problem
- `incomplete`: Missing steps or logic gaps
- `formatting`: Answer present but not extracted

**Example annotation**:
```json
{
  "problem_id": "gsm8k_042",
  "condition": "process",
  "error_type": "arithmetic",  // ← Add this
  "error_notes": "3 × 5 calculated as 11 in Step 2"  // ← Add this
}
```

After annotation, run again to generate statistics:
```bash
python phase2_error_analysis.py
```

**Output**: `results/error_type_statistics.json`

---

### Phase 2.2: Hallucination Detection

**Script**: `code/phase2_hallucination_detection.py`

**What it does**:
- Samples 50 process/structured responses
- Includes automatic detection flags for arithmetic errors
- Creates template for manual hallucination annotation

**How to run**:
```bash
python phase2_hallucination_detection.py
```

**Output**: `data/processed/hallucination_analysis.jsonl`

**Manual Step**: For each response:
1. Set `has_hallucination`: `true` or `false`
2. If true, list types in `hallucination_types`:
   - `factual_error`: Objectively false statement
   - `irrelevant`: Unrelated facts
   - `inconsistent`: Contradicts earlier steps
   - `confabulation`: Makes up details
3. Copy specific hallucination text to `hallucination_examples`

After annotation, run again to generate statistics:
```bash
python phase2_hallucination_detection.py
```

**Output**: `results/hallucination_statistics.json`

---

## 🔍 Phase 3: Interpretability Metrics

### Phase 3.1: Sample Selection

**Script**: `code/phase3_sample_selection.py`

**What it does**:
- Selects 60 problems stratified by correctness
- Creates template for deep annotation (most intensive phase)

**How to run**:
```bash
python phase3_sample_selection.py
```

**Output**: `data/annotations/deep_annotation_sample.jsonl`

---

### Phase 3.2: Deep Annotation (MANUAL - Most Important)

**File**: `data/annotations/deep_annotation_sample.jsonl`

For EACH problem, you need to:

#### Step 1: Extract Reasoning Steps
```json
"reasoning_steps": [
  "Calculate total items: 3 + 5 = 8",
  "Divide by 2: 8 / 2 = 4",
  "Final answer is 4"
]
```

#### Step 2: Score Each Step (0-2)
```json
"step_scores": [2, 2, 2]
```

Scoring rubric:
- **0**: Incorrect/unjustified (wrong calculation, false premise, illogical)
- **1**: Partially correct/incomplete (right direction but imprecise)
- **2**: Correct and well-justified (accurate, clear reasoning)

#### Step 3: Extract Expert Steps
From the `ground_truth` field, extract the reference solution steps:
```json
"expert_steps": [
  "Find total: 3 + 5 = 8",
  "Divide by cost: 8 / 2 = 4"
]
```

#### Step 4: Score Alignment (0-2)
Compare each model step with expert solution:
```json
"alignment_scores": [2, 2]
```

Alignment rubric:
- **0**: Different and incorrect/irrelevant
- **1**: Similar operation but imprecise
- **2**: Essentially same operation and correct

#### Step 5: Auditability Scores (1-5 Likert)
```json
"clarity_score": 5,              // How clear is the reasoning?
"verification_effort_score": 5,  // How easy to verify?
"coherence_score": 5             // Do steps flow logically?
```

Scale:
- 1 = Very poor
- 2 = Poor
- 3 = Neutral
- 4 = Good
- 5 = Excellent

**Time estimate**: 5-10 minutes per problem × 60 problems = **5-10 hours total**

**Tip**: Do in batches of 10-15 to avoid fatigue.

---

### Phase 3.3: Calculate Interpretability Metrics

**Script**: `code/phase3_calculate_interpretability.py`

**What it does**:
- Calculates mean scores for all interpretability metrics
- Aggregates by condition

**How to run** (after completing annotations):
```bash
python phase3_calculate_interpretability.py
```

**Output**: `results/interpretability_metrics.json`

---

## 📈 Phase 4: Statistical Analysis and Visualizations

### Phase 4.1: Statistical Analysis

**Script**: `code/phase4_statistical_analysis.py`

**What it does**:
- Compares accuracy across conditions with paired t-tests
- Calculates effect sizes (Cohen's d)
- Generates summary statistics table

**How to run**:
```bash
python phase4_statistical_analysis.py
```

**Output**: `results/statistical_analysis.json`

---

### Phase 4.2: Create Visualizations

**Script**: `code/phase4_visualizations.py`

**What it does**:
- Generates 5 publication-quality figures (300 DPI)

**How to run**:
```bash
python phase4_visualizations.py
```

**Outputs**: `results/figures/`
- `01_accuracy_comparison.png`
- `02_error_distribution.png`
- `03_interpretability_metrics.png`
- `04_hallucination_rates.png`
- `05_summary_comparison.png`

---

### Phase 4.3: Qualitative Failure Analysis

**Script**: `code/phase4_qualitative_analysis.py`

**What it does**:
- Identifies failure patterns using heuristics
- Samples 10 examples per pattern for case studies

**How to run**:
```bash
python phase4_qualitative_analysis.py
```

**Output**: `data/processed/failure_case_analysis.jsonl`

**Manual Step**: Review case studies, confirm patterns, add detailed analysis

---

## 📝 Phase 5: Report Generation

**Script**: `code/phase5_report_generator.py`

**What it does**:
- Generates comprehensive markdown report
- Includes all findings, legal implications, visualizations

**How to run**:
```bash
python phase5_report_generator.py
```

**Output**: `docs/FINAL_REPORT.md`

**Manual Step**:
1. Review generated report
2. Add case study details from qualitative analysis
3. Refine legal implications section
4. Add references and citations
5. Proofread

---

## 🚀 Running All Phases Automatically

**Master Script**: `code/run_all_phases.py`

Runs all automated phases in sequence, pausing for manual annotation:

```bash
cd code
python run_all_phases.py
```

The script will:
1. Run Phase 2 (error and hallucination templates)
2. Pause for manual annotation
3. Run Phase 3.1 (sample selection)
4. Pause for deep annotation
5. Run Phase 3.2 (calculate metrics)
6. Run Phase 4 (analysis and visualizations)
7. Run Phase 5 (report generation)

---

## File Structure

### Code Files
```
code/
├── prepare_dataset.py                    # Phase 1.1 ✅
├── generate_responses.py                 # Phase 1.2 ✅
├── extract_answers.py                    # Phase 1.3 ✅
├── calculate_metrics.py                  # Phase 1.4 ✅
├── phase2_error_analysis.py              # Phase 2.1
├── phase2_hallucination_detection.py     # Phase 2.2
├── phase3_sample_selection.py            # Phase 3.1
├── phase3_calculate_interpretability.py  # Phase 3.2
├── phase4_statistical_analysis.py        # Phase 4.1
├── phase4_visualizations.py              # Phase 4.2
├── phase4_qualitative_analysis.py        # Phase 4.3
├── phase5_report_generator.py            # Phase 5
└── run_all_phases.py                     # Master script
```

### Data Files
```
data/
├── dataset_manifest.csv                  # Selected problems
├── raw/
│   └── responses.jsonl                   # Raw model responses
├── processed/
│   ├── responses_with_answers.jsonl      # Extracted answers
│   ├── error_analysis.jsonl              # Error annotations
│   ├── hallucination_analysis.jsonl      # Hallucination annotations
│   └── failure_case_analysis.jsonl       # Case studies
└── annotations/
    └── deep_annotation_sample.jsonl      # Deep annotations
```

### Results Files
```
results/
├── accuracy_metrics.json                 # Phase 1
├── error_type_statistics.json            # Phase 2
├── hallucination_statistics.json         # Phase 2
├── interpretability_metrics.json         # Phase 3
├── statistical_analysis.json             # Phase 4
└── figures/                              # Phase 4
    ├── 01_accuracy_comparison.png
    ├── 02_error_distribution.png
    ├── 03_interpretability_metrics.png
    ├── 04_hallucination_rates.png
    └── 05_summary_comparison.png
```

---

## Troubleshooting

### Issue: "File not found" errors

**Solution**: Ensure you're running scripts from the `code/` directory:
```bash
cd code
python phase2_error_analysis.py
```

### Issue: Missing dependencies

**Solution**: Reinstall requirements:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: API rate limits

**Solution**: Add delays in `generate_responses.py` or use a different model

### Issue: Annotation files are overwhelming

**Solution**: Start with a smaller sample (modify `SAMPLE_SIZE` in scripts)

### Issue: Visualizations won't generate

**Solution**:
1. Check that all required results files exist
2. Run Phase 4.1 before 4.2
3. Ensure matplotlib backend is configured

---

## Time Estimates

| Phase | Automated | Manual | Total |
|-------|-----------|--------|-------|
| Phase 1 | ✅ Done | - | - |
| Phase 2 | 5 min | 2-3 hours | ~3 hours |
| Phase 3 | 5 min | 5-10 hours | ~10 hours |
| Phase 4 | 10 min | 2-3 hours | ~3 hours |
| Phase 5 | 5 min | 2-3 hours | ~3 hours |
| **Total** | ~30 min | ~15-20 hours | **~20 hours** |

---

## Next Steps After Completion

1. ✅ Review `docs/FINAL_REPORT.md`
2. ✅ Create presentation slides
3. ✅ Prepare for Q&A
4. ✅ Optional: Submit to workshop/conference
5. ✅ Optional: Create interactive dashboard

---

## Support

For questions or issues:
1. Check this guide
2. Review `project_implementation_plan_extracted.md`
3. Check script comments and docstrings
4. Review example output files

---

**Good luck with your research!** 🎓
