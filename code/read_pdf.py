import pypdf
import os

pdf_path = r"c:\Users\ddpat\Desktop\RESPAI\resp_ai\docs\project_implementation_plan.md.pdf"
output_path = r"c:\Users\ddpat\Desktop\RESPAI\resp_ai\docs\project_implementation_plan_extracted.md"

try:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write((text))
    print(f"Successfully extracted text to {output_path}")
except Exception as e:
    print(f"Error: {e}")
