import boto3
import json
import logging
import os
import time

from prompt_manager import PromptTemplateManager
from model_invoker import ModelInvoker
from content_validator import ContentValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")
prompt_manager = PromptTemplateManager()
model = ModelInvoker()
validator = ContentValidator()

S3_BUCKET = os.environ.get("S3_BUCKET")
if not S3_BUCKET:
    raise EnvironmentError(
        "Variável de ambiente S3_BUCKET não definida. "
        "Execute: export S3_BUCKET=nome-do-seu-bucket"
    )


def process_document(bucket: str, key: str) -> dict:
    """
    Processa um documento de sinistro do S3.

    Args:
        bucket: nome do bucket S3
        key:    caminho do arquivo dentro do bucket

    Returns:
        dict com 'extracted_info', 'summary' e 'metadata'

    Raises:
        FileNotFoundError: se o objeto não existir no S3
        RuntimeError: se o modelo falhar após retries
    """
    logger.info(f"Iniciando processamento: s3://{bucket}/{key}")
    start_total = time.time()

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        document_text = response["Body"].read().decode("utf-8")
        logger.info(f"Documento lido com sucesso ({len(document_text)} caracteres)")
    except s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"Arquivo não encontrado: s3://{bucket}/{key}")
    except Exception as e:
        logger.error(f"Erro ao ler S3: {e}")
        raise

    try:
        extract_prompt = prompt_manager.get_prompt(
            "extract_info",
            document_text=document_text
        )
        logger.info("Invocando modelo para extração de informações...")
        t0 = time.time()
        extracted_raw = model.invoke(extract_prompt)
        logger.info(f"Extração concluída em {time.time() - t0:.2f}s")
    except Exception as e:
        logger.error(f"Erro na extração: {e}")
        raise RuntimeError(f"Falha ao extrair informações do documento: {e}")

    validated_info = validator.validate_json(extracted_raw)
    if "error" in validated_info:
        logger.warning(
            f"JSON inválido retornado pelo modelo. Raw output: {extracted_raw[:200]}"
        )

    try:
        summary_prompt = prompt_manager.get_prompt(
            "generate_summary",
            extracted_info=json.dumps(validated_info, ensure_ascii=False)
        )
        logger.info("Invocando modelo para geração de resumo...")
        t0 = time.time()
        summary = model.invoke(summary_prompt, temperature=0.7, max_tokens=200)
        logger.info(f"Resumo gerado em {time.time() - t0:.2f}s")
    except Exception as e:
        logger.error(f"Erro na geração de resumo: {e}")
        summary = "Resumo indisponível devido a erro no modelo."

    elapsed = time.time() - start_total
    logger.info(f"Processamento finalizado em {elapsed:.2f}s")

    return {
        "extracted_info": validated_info,
        "summary": summary,
        "metadata": {
            "source": f"s3://{bucket}/{key}",
            "processing_time_seconds": round(elapsed, 2),
            "extraction_valid": "error" not in validated_info,
        }
    }


if __name__ == "__main__":
    result = process_document(
        bucket=S3_BUCKET,
        key="claims/claim1.txt"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))