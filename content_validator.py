import json

class ContentValidator:

    def validate_json(self, text):

        try:
            parsed = json.loads(text)
            return parsed

        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON returned by model",
                "raw_output": text
            }