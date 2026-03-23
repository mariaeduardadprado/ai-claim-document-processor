import boto3
import json

from prompt_manager import PromptTemplateManager
from model_invoker import ModelInvoker
from content_validator import ContentValidator

s3 = boto3.client("s3")

prompt_manager = PromptTemplateManager()
model = ModelInvoker()
validator = ContentValidator()


def process_document(bucket, key):

    response = s3.get_object(Bucket=bucket, Key=key)
    document_text = response["Body"].read().decode("utf-8")

    # Prompt de extração
    extract_prompt = prompt_manager.get_prompt(
        "extract_info",
        document_text=document_text
    )

    extracted_info = model.invoke(extract_prompt)

    validated_info = validator.validate_json(extracted_info)

    # Prompt de resumo
    summary_prompt = prompt_manager.get_prompt(
        "generate_summary",
        extracted_info=extracted_info
    )

    summary = model.invoke(summary_prompt, temperature=0.7, max_tokens=200)

    return {
        "extracted_info": validated_info,
        "summary": summary
    }


if __name__ == "__main__":

    result = process_document(
        "claim-documents-poc-duda",
        "claims/claim1.txt"
    )

    print(json.dumps(result, indent=2))