class PromptTemplateManager:

    def __init__(self):
        self.templates = {
            "extract_info": """You are a precise data extraction assistant for insurance claims.

Extract the following fields from the claim document below.

Rules:
- Return ONLY a valid JSON object. No explanation, no markdown, no extra text.
- If a field is not found in the document, use null as the value.
- Do not invent or infer values that are not explicitly stated.

Required fields:
- Claimant Name
- Policy Number
- Incident Date       (format: YYYY-MM-DD)
- Claim Amount        (format: numeric string, e.g. "4500.00")
- Incident Description

Example of expected output:
{{
  "Claimant Name": "Jane Doe",
  "Policy Number": "POL-000000",
  "Incident Date": "2025-03-10",
  "Claim Amount": "2300.00",
  "Incident Description": "Rear-end collision on Highway 101."
}}

Document:
{document_text}

JSON output:""",
            "generate_summary": """You are a claims analyst writing internal summaries.

Based on the structured claim data below, write a concise 2–3 sentence summary
for an internal reviewer. Be factual. Do not add information not present in the data.
Return only the summary text, no labels or headers.

Claim data:
{extracted_info}

Summary:"""
        }

    def get_prompt(self, template_name: str, **kwargs) -> str:
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(
                f"Template '{template_name}' não encontrado. "
                f"Disponíveis: {list(self.templates.keys())}"
            )
        return template.format(**kwargs)