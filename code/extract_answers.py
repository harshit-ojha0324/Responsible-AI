import json
import re
import os
import pandas as pd

INPUT_FILE = "../data/raw/responses.jsonl"
OUTPUT_FILE = "../data/processed/responses_with_answers.jsonl"

def extract_number(text):
    if not text:
        return None
    # Look for "Final Answer: <number>" pattern common in CoT
    # Or just look for the last number in the text
    
    # specialized parsing for "Final Answer:"
    final_answer_match = re.search(r"Final Answer:\s*([^\n]+)", text, re.IGNORECASE)
    if final_answer_match:
        candidate = final_answer_match.group(1)
        # Verify it has digits
        if any(c.isdigit() for c in candidate):
             return normalize_number(candidate)
    
    # If no "Final Answer:", try to find the last number in the text
    # This is risky but standard fallback for Outcome-based prompting
    # outcome prompt explicitly asks for "ONLY the final numerical answer"
    # but models result often includes "Answer: 123" or just "123"
    
    # Clean up common wrappings like **123** or "123"
    cleaned = text.strip().replace("*", "").replace("\"", "")
    
    # Find all numbers
    numbers = re.findall(r'-?\d*\.?\d+(?:[eE][-+]?\d+)?', cleaned)
    if numbers:
        return float(numbers[-1])
    
    return None

def normalize_number(text):
    # Remove non-numeric chars except . and -
    # Also handle fractions 1/2 -> 0.5? complex
    # For GSM8K, answers are usually integers or simple floats.
    # We will try to cast to float.
    
    # Remove commas (1,000 -> 1000)
    text = text.replace(",", "")
    
    # Extract first valid number sequence
    match = re.search(r'-?\d*\.?\d+', text)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            pass
    return None

def process_responses():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    processed_count = 0
    with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            try:
                data = json.loads(line)
                
                # Extract answers
                extracted = {}
                for condition, response_text in data.get("responses", {}).items():
                    extracted[condition] = extract_number(response_text)
                
                data["extracted_answers"] = extracted
                
                # Normalize ground truth as well for comparison
                # GSM8K ground truth is usually in the 'answer' field but often has reasoning.
                # Wait, my manifest has 'answer' which is the raw GSM8K answer field?
                # GSM8K 'answer' field usually ends with "#### <number>"
                
                ground_truth_raw = data.get("ground_truth", "")
                gt_val = None
                if "####" in ground_truth_raw:
                    gt_val = extract_number(ground_truth_raw.split("####")[-1])
                else:
                    gt_val = extract_number(ground_truth_raw)
                
                data["ground_truth_numeric"] = gt_val
                
                fout.write(json.dumps(data) + "\n")
                processed_count += 1
            except json.JSONDecodeError:
                continue
                
    print(f"Processed {processed_count} responses. Saved to {output_path}")

if __name__ == "__main__":
    process_responses()
