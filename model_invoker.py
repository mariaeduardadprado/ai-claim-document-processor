import boto3
import json

bedrock_runtime = boto3.client("bedrock-runtime")

class ModelInvoker:

    def __init__(self, model_id="anthropic.claude-3-haiku-20240307-v1:0"):
        self.model_id = model_id

    def invoke(self, prompt, temperature=0.0, max_tokens=300):

        response = bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            })
        )

        response_body = json.loads(response["body"].read())

        return response_body["content"][0]["text"]