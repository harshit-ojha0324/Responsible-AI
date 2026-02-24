# Prompt templates for Phase 1

OUTCOME_PROMPT = """Answer the following math problem. Provide ONLY the final numerical answer, without showing any work or reasoning.

Problem: {question}

Answer:"""

PROCESS_PROMPT = """Solve the following math problem step by step. Show all your reasoning clearly, then provide the final answer.

Problem: {question}

Solution:"""

STRUCTURED_PROMPT = """Solve the following math problem using the following format:

Step 1: [First reasoning step]
Step 2: [Second reasoning step]
...
Final Answer: [Numerical answer]

Problem: {question}

Solution:"""
