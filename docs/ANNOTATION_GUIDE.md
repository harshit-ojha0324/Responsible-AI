# Annotation Guide

Detailed instructions for manual annotation tasks in Phases 2 and 3.

---

## Phase 2.1: Error Type Annotation

### File Location
`data/processed/error_analysis.jsonl`

### Task
Classify each incorrect response by error type.

### Error Types

#### 1. Arithmetic Error
Calculation mistake where the operation is correct but the result is wrong.

**Examples**:
- "3 × 5 = 11" (should be 15)
- "24 / 3 = 6" (should be 8)
- "7 + 8 = 16" (should be 15)

#### 2. Conceptual Error
Wrong approach, formula, or mathematical concept.

**Examples**:
- Using addition when multiplication is needed
- Applying wrong formula (e.g., area instead of perimeter)
- Misunderstanding the mathematical relationship

#### 3. Reading Comprehension Error
Misunderstood the problem statement.

**Examples**:
- Used wrong numbers from the problem
- Solved for the wrong quantity
- Missed a condition or constraint

#### 4. Incomplete Reasoning
Missing critical steps or logic gaps.

**Examples**:
- Skipped intermediate calculations
- Jumped to conclusion without justification
- Left out necessary steps

#### 5. Formatting/Parsing Error
The answer is present in the response but wasn't extracted correctly.

**Examples**:
- Answer is "$42" but extracted as null
- Answer is "forty-two" (spelled out) but not parsed
- Answer is in an unexpected format

### How to Annotate

For each entry in the file:

```json
{
  "problem_id": "gsm8k_123",
  "condition": "process",
  "question": "...",
  "response": "...",
  "error_type": null,     // ← ADD ERROR TYPE HERE
  "error_notes": ""       // ← ADD NOTES HERE (optional)
}
```

Change to:
```json
{
  "problem_id": "gsm8k_123",
  "condition": "process",
  "question": "...",
  "response": "...",
  "error_type": "arithmetic",
  "error_notes": "In Step 2, calculated 3 × 5 = 11 instead of 15"
}
```

### Tips
- Read the full response carefully
- Compare with ground_truth
- One error type per entry (choose primary cause)
- Add detailed notes - these will be useful for the report

---

## Phase 2.2: Hallucination Annotation

### File Location
`data/processed/hallucination_analysis.jsonl`

### Task
Identify if responses contain hallucinations (factually incorrect statements in reasoning).

### Hallucination Types

#### 1. Factual Error
Objectively false statement.

**Examples**:
- "3 × 5 = 11"
- "The square root of 16 is 8"
- "There are 60 minutes in a day"

#### 2. Irrelevant Information
Introduces facts unrelated to the problem.

**Examples**:
- "This problem is similar to the Pythagorean theorem..."
  (when problem is about simple arithmetic)
- Brings in concepts not in the problem
- Makes references to external knowledge incorrectly

#### 3. Logical Inconsistency
Contradicts earlier steps or itself.

**Examples**:
- Step 1: "x = 5"
- Step 3: "Since x = 7..." (contradiction)
- Uses a value that conflicts with previous derivation

#### 4. Confabulation
Makes up non-existent details.

**Examples**:
- "According to the formula in the problem..." (no formula given)
- "As stated earlier..." (nothing was stated earlier)
- Invents problem constraints that don't exist

### How to Annotate

For each entry:

```json
{
  "problem_id": "gsm8k_456",
  "response": "First, 3 × 5 = 11. Then...",
  "has_hallucination": null,      // ← true or false
  "hallucination_types": [],      // ← list types if true
  "hallucination_examples": "",   // ← quote specific text
  "notes": ""
}
```

Change to:
```json
{
  "problem_id": "gsm8k_456",
  "response": "First, 3 × 5 = 11. Then...",
  "has_hallucination": true,
  "hallucination_types": ["factual_error"],
  "hallucination_examples": "3 × 5 = 11 (should be 15)",
  "notes": "Arithmetic error in first step affects rest of reasoning"
}
```

### Special Cases

**Correct answer with hallucination**: Mark as hallucination even if final answer is correct
```json
{
  "is_correct": true,
  "has_hallucination": true,
  "notes": "Got right answer despite arithmetic error (compensating error later)"
}
```

**Multiple hallucinations**: List all types
```json
{
  "hallucination_types": ["factual_error", "inconsistent"],
  "hallucination_examples": "Step 1: 3×5=11 (error); Step 3: contradicts Step 1"
}
```

### Tips
- Check ALL arithmetic carefully
- Look for internal contradictions
- Verify any claimed "facts"
- Quote specific text in examples field

---

## Phase 3: Deep Annotation (Interpretability)

### File Location
`data/annotations/deep_annotation_sample.jsonl`

### Task
The most intensive annotation - deeply analyze reasoning quality.

This is the **most important** phase for interpretability metrics.

---

### Step 1: Extract Reasoning Steps

Break down the response into individual logical steps.

**Example Response**:
```
Let's solve this step by step:
First, we need to find the total number of items. We have 3 apples and 5 oranges.
3 + 5 = 8 items total.
Now we divide by the price of $2 each.
8 / 2 = 4.
So the answer is 4.
```

**Extracted Steps**:
```json
"reasoning_steps": [
  "Find total items: 3 apples + 5 oranges",
  "Calculate: 3 + 5 = 8",
  "Divide by price: 8 / 2",
  "Calculate: 8 / 2 = 4",
  "Final answer: 4"
]
```

**Guidelines**:
- One step = one logical operation or conclusion
- Include both setup and calculation steps
- Keep steps atomic (don't combine multiple operations)
- Preserve original wording when possible

---

### Step 2: Score Each Step (0-2)

For each reasoning step, assign a score:

#### Score 0: Incorrect or Unjustified
- **Factual error**: Wrong calculation or false premise
- **Missing justification**: No explanation for claim
- **Illogical inference**: Doesn't follow from previous steps

**Examples**:
```
Step: "3 + 5 = 11"
Score: 0 (arithmetic error)

Step: "Therefore x must be 7"
Score: 0 (no justification provided)

Step: "Since it's a square, the answer is 42"
Score: 0 (illogical - doesn't follow)
```

#### Score 1: Partially Correct or Incomplete
- **Correct direction** but imprecise or sloppy
- **Partially justified** but missing some reasoning
- **Minor errors** with correct overall approach

**Examples**:
```
Step: "Add them together to get about 8"
Score: 1 (correct operation, imprecise language)

Step: "Divide by 2 to get the answer"
Score: 1 (correct but doesn't show calculation)

Step: "3 + 5 = 8 items"
Score: 1 if units matter but weren't in problem
```

#### Score 2: Correct and Well-Justified
- **Factually accurate**: No errors
- **Clear reasoning**: Easy to understand logic
- **Properly follows**: Builds on previous steps correctly

**Examples**:
```
Step: "Calculate total items: 3 + 5 = 8"
Score: 2 (clear, accurate, justified)

Step: "Divide total by price: 8 ÷ 2 = 4"
Score: 2 (correct operation and calculation)

Step: "Since area = length × width, A = 5 × 3 = 15"
Score: 2 (formula stated, correct application)
```

---

### Step 3: Extract Expert Steps

From the `ground_truth` field, extract the reference solution.

**Ground Truth Example**:
```
"Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?
#### 16 - 3 - 4 = 9
#### 9 * 2 = 18"
```

**Extracted Expert Steps**:
```json
"expert_steps": [
  "Subtract eggs consumed: 16 - 3 - 4 = 9",
  "Multiply by price: 9 × 2 = 18"
]
```

**Guidelines**:
- Focus on key logical steps
- GSM8K format: lines after "####" are calculations
- Simplify if needed (combine trivial steps)
- Aim for 2-5 expert steps per problem

---

### Step 4: Score Alignment (0-2)

Compare **model steps** with **expert steps**.

You're measuring: "Does the model follow the same reasoning path as an expert?"

#### Score 0: Different and Incorrect/Irrelevant
Model uses different operation AND gets it wrong, or goes off-track.

**Example**:
```
Expert: "Subtract eggs consumed: 16 - 3 - 4 = 9"
Model: "Multiply all the numbers: 16 × 3 × 4 = 192"
Score: 0 (completely different, wrong approach)
```

#### Score 1: Similar Operation but Imprecise/Partially Wrong
Right general approach but different details or minor errors.

**Example**:
```
Expert: "Subtract eggs consumed: 16 - 3 - 4 = 9"
Model: "First subtract 3: 16 - 3 = 13, then subtract 4: 13 - 4 = 9"
Score: 1 (same result, slightly different decomposition)
```

#### Score 2: Essentially Same Operation and Correct
Model reasoning matches expert reasoning.

**Example**:
```
Expert: "Subtract eggs consumed: 16 - 3 - 4 = 9"
Model: "Calculate remaining eggs: 16 - 3 - 4 = 9"
Score: 2 (same logic, different wording)
```

**Important**: You're scoring EACH model step against the MOST RELEVANT expert step.

**Alignment Process**:
1. For each expert step, find corresponding model step(s)
2. Score the alignment
3. Some model steps may not align with any expert step (mark as 0)
4. Some expert steps may not have model equivalent (note this)

**Example Full Alignment**:
```
Expert Steps (2):
1. "Subtract consumed: 16 - 3 - 4 = 9"
2. "Multiply by price: 9 × 2 = 18"

Model Steps (5):
1. "Janet starts with 16 eggs" → No expert match → 0
2. "She eats 3 for breakfast" → Partial match to Expert #1 → 1
3. "She uses 4 for muffins" → Partial match to Expert #1 → 1
4. "Remaining: 16 - 3 - 4 = 9" → Perfect match to Expert #1 → 2
5. "Revenue: 9 × $2 = $18" → Perfect match to Expert #2 → 2

alignment_scores: [0, 1, 1, 2, 2]
```

---

### Step 5: Auditability Scores (1-5 Likert Scale)

Rate overall quality of the response for human review.

#### Clarity Score (1-5)
"How easy is it to understand what the model is doing at each step?"

- **1**: Very unclear, confusing, hard to follow
- **2**: Mostly unclear, significant ambiguity
- **3**: Neutral, some clear parts, some unclear
- **4**: Mostly clear, minor ambiguities
- **5**: Very clear, easy to understand

**Consider**:
- Is reasoning explained or just stated?
- Are intermediate values shown?
- Is mathematical notation correct?

#### Verification Effort Score (1-5)
"How much effort would it take to check if each step is correct?"

- **1**: Very difficult, would need to redo entire problem
- **2**: Difficult, missing key information
- **3**: Moderate effort, some steps need validation
- **4**: Easy, can quickly verify most steps
- **5**: Very easy, all steps easily checkable

**Consider**:
- Are calculations shown explicitly?
- Can you verify each step independently?
- Is all needed information present?

#### Coherence Score (1-5)
"Do the steps flow logically from one to the next?"

- **1**: Incoherent, random jumps, doesn't make sense
- **2**: Poor flow, many logical gaps
- **3**: Adequate, some jumps but followable
- **4**: Good flow, logical progression
- **5**: Excellent, each step clearly builds on previous

**Consider**:
- Does each step follow from the previous?
- Are there unexplained jumps?
- Is the overall logic sound?

---

## Complete Annotation Example

### Input
```json
{
  "problem_id": "gsm8k_001",
  "condition": "process",
  "question": "Janet's ducks lay 16 eggs per day...",
  "ground_truth": "#### 16 - 3 - 4 = 9\n#### 9 * 2 = 18",
  "response": "Let's solve step by step. Janet starts with 16 eggs. She eats 3 for breakfast. Then she uses 4 for muffins. So remaining eggs are 16 - 3 - 4 = 9. She sells these at $2 each, so 9 × 2 = $18.",
  "reasoning_steps": [],
  "step_scores": [],
  "expert_steps": [],
  "alignment_scores": [],
  "clarity_score": null,
  "verification_effort_score": null,
  "coherence_score": null
}
```

### Annotated Output
```json
{
  "problem_id": "gsm8k_001",
  "condition": "process",
  "question": "Janet's ducks lay 16 eggs per day...",
  "ground_truth": "#### 16 - 3 - 4 = 9\n#### 9 * 2 = 18",
  "response": "Let's solve step by step. Janet starts with 16 eggs. She eats 3 for breakfast. Then she uses 4 for muffins. So remaining eggs are 16 - 3 - 4 = 9. She sells these at $2 each, so 9 × 2 = $18.",

  "reasoning_steps": [
    "Janet starts with 16 eggs",
    "She eats 3 for breakfast",
    "She uses 4 for muffins",
    "Calculate remaining: 16 - 3 - 4 = 9",
    "Multiply by price: 9 × 2 = 18"
  ],

  "step_scores": [2, 2, 2, 2, 2],

  "expert_steps": [
    "Subtract consumed eggs: 16 - 3 - 4 = 9",
    "Multiply by price: 9 × 2 = 18"
  ],

  "alignment_scores": [1, 1, 1, 2, 2],

  "clarity_score": 5,
  "verification_effort_score": 5,
  "coherence_score": 5,

  "notes": "Excellent response - clear, accurate, well-structured"
}
```

---

## Time Management

**Phase 2 Annotations**: ~2-3 hours total
- Error types: 30-50 entries × 2-3 min = ~2 hours
- Hallucinations: 50 entries × 3-4 min = ~3 hours

**Phase 3 Annotations**: ~5-10 hours total
- 60 problems (process + structured) = ~120 entries
- Deep annotation: 5-10 min per entry
- Total: **10-20 hours**

**Tips for Efficiency**:
1. Do in batches (10-15 at a time)
2. Take breaks every hour
3. Create templates for common patterns
4. Note ambiguous cases for discussion
5. Use a second monitor if possible

---

## Quality Checks

### Self-Consistency
Every ~20 annotations, re-annotate 2-3 previous ones without looking at your original scores. Check if you're consistent.

### Spot Checks
- Do arithmetic errors have score 0?
- Do perfect steps have score 2?
- Do alignment scores make sense?

### Common Mistakes to Avoid
- ❌ Being too lenient (everything is 2)
- ❌ Being too harsh (everything is 0)
- ❌ Not reading full response
- ❌ Confusing step scores with alignment scores
- ❌ Forgetting to extract expert steps

---

## Questions?

If you encounter ambiguous cases:
1. Note them in the "notes" field
2. Use your best judgment
3. Be consistent across similar cases
4. Document your reasoning

**Remember**: Perfect agreement isn't expected. Thoughtful, consistent annotation is the goal.

---

Good luck! 🎯
