from models import FinalVerdict
from typing import List, Dict
from utils.logger import system_logger

class VerdictJudge:
    def process(self, claim_object: str, original_claim: str, decomposed_claims: List[str], evidence_reports: List[Dict], llm_client) -> FinalVerdict:
        prompt = f"""
You are the final judge for a damage claim verification system.
Review the original user claim about a '{claim_object}', its decomposition, and the factual visual evidence gathered from the images.

Original Claim: {original_claim}

Decomposed Sub-Claims:
{decomposed_claims}

Visual Evidence Reports:
"""
        for report in evidence_reports:
            prompt += f"\nImage ID: {report['image_id']}\n"
            for ev in report['evidences']:
                prompt += f"  - Sub-claim [{ev['sub_claim_id']}]: {ev['answer']}. Reasoning: {ev['reasoning']}\n"
            prompt += f"  - Meets Evidence Standard: {report['evidence_standard_met']}\n"
            prompt += f"  - Valid Image: {report['valid_image']}\n"
            prompt += f"  - Quality Issues: {report['quality_issues']}\n"

        prompt += """
Task:
Determine the final verdict and metadata based *only* on the visual evidence.
1. `claim_status`:
   - "supported": Visual evidence confirms all key sub-claims.
   - "contradicted": Visual evidence contradicts the claim (e.g. wrong object, or object is visibly undamaged where damage was claimed).
   - "not_enough_information": Images are unclear, missing relevant parts, or don't definitively prove/disprove the claim.
2. `issue_type`: Use the exact enum for the visible issue (e.g. dent, scratch, crack, stain, etc. 'none' if no issue, 'unknown' if unclear).
3. `object_part`: Use the exact enum for the relevant object part (e.g. front_bumper, screen, box, etc. 'unknown' if unclear).
4. `supporting_image_ids`: Provide a list of image IDs that directly support the decision. If no image supports it, use an empty list or ["none"].
5. `claim_status_justification`: Provide a concise explanation grounded in the image evidence.

Provide your final verdict following the structured JSON schema exactly.
"""
        system_logger.log_interaction("VerdictJudge", prompt, {
            "claim": original_claim,
            "reports": evidence_reports
        })

        try:
            result = llm_client.generate_structured(prompt, FinalVerdict)
            system_logger.log_interaction("VerdictJudge", "Parsed output successfully", result.model_dump())
            return result
        except Exception as e:
            system_logger.error(f"Error in VerdictJudge: {e}")
            raise
