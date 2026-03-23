import time
from model_invoker import ModelInvoker

models = [
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0"
]

document_text = open("claims/claim1.txt").read()

results = {}

for model in models:

    invoker = ModelInvoker(model)

    start_time = time.time()

    output = invoker.invoke(
        "Extract key information from this document:\n" + document_text
    )

    elapsed = time.time() - start_time

    results[model] = {
        "time_seconds": elapsed,
        "output_length": len(output),
        "output_sample": output[:120]
    }

print(results)