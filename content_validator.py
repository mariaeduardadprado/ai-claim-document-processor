import json
import logging
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError

logger = logging.getLogger(__name__)

class ClaimSchema(BaseModel):
    claimant_name:       Optional[str] = None
    policy_number:       Optional[str] = None
    incident_date:       Optional[str] = None
    claim_amount:        Optional[str] = None
    incident_description: Optional[str] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_model_output(cls, data: dict) -> "ClaimSchema":
        """Mapeia as chaves do modelo (com espaços) para o schema."""
        return cls(
            claimant_name=data.get("Claimant Name"),
            policy_number=data.get("Policy Number"),
            incident_date=data.get("Incident Date"),
            claim_amount=data.get("Claim Amount"),
            incident_description=data.get("Incident Description"),
        )

    def coverage_report(self) -> dict:
        fields = self.model_dump()
        filled   = [k for k, v in fields.items() if v is not None]
        missing  = [k for k, v in fields.items() if v is None]
        coverage = round(len(filled) / len(fields) * 100)
        return {
            "coverage_pct": coverage,
            "filled_fields": filled,
            "missing_fields": missing,
        }


class ContentValidator:

    def validate_json(self, text: str) -> dict:
        """
        Valida o output bruto do modelo.

        Returns:
            dict com os dados validados + metadados de qualidade,
            ou dict com 'error' se o JSON for inválido.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON inválido: {e}. Raw output (200 chars): {text[:200]}")
            return {
                "error": "invalid_json",
                "detail": str(e),
                "raw_output": text[:500],
            }

        try:
            claim = ClaimSchema.from_model_output(parsed)
            report = claim.coverage_report()

            if report["coverage_pct"] < 60:
                logger.warning(
                    f"Cobertura baixa: {report['coverage_pct']}%. "
                    f"Campos ausentes: {report['missing_fields']}"
                )
            else:
                logger.info(f"Validação OK — cobertura: {report['coverage_pct']}%")

            return {
                **claim.model_dump(),
                "validation": report,
            }

        except ValidationError as e:
            logger.error(f"Schema inválido: {e}")
            return {
                "error": "schema_validation_failed",
                "detail": str(e),
                "raw_parsed": parsed,
            }