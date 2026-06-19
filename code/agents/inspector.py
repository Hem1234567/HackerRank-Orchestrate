import json
from models import DecomposedClaim, ImageAnalysisReport
from utils.logger import system_logger

class VisualInspector:
    def process(self, claim_object: str, decomposed_claim: DecomposedClaim, image_path: str, image_id: str, evidence_req: str, llm_client) -> ImageAnalysisReport:
        prompt = f"""
You are an expert visual damage inspector.
Analyze the provided image to verify the following sub-claims for a {claim_object} claim:
"""
        for sc in decomposed_claim.sub_claims:
            prompt += f"- [{sc.id}] {sc.question}\n"
            
        prompt += f"""
Minimum Evidence Requirement:
{evidence_req}

Use a step-by-step reasoning process:
1. Examine the image quality and whether the object matches the core claim category ({decomposed_claim.core_claim}).
2. Evaluate if the image meets the 'Minimum Evidence Requirement' specified above. Determine `evidence_standard_met` (true/false) and provide a short `evidence_standard_met_reason`.
3. Determine `valid_image` (true if the image is an actual photo usable for review, false if it's a screenshot, illustration, or unreadable).
4. Identify any `quality_issues` using the allowed RiskFlag enum (e.g. blurry_image, cropped_or_obstructed, low_light_or_glare, wrong_angle, wrong_object, wrong_object_part). Use 'none' if no issues.
5. For each sub-claim, look for specific visual evidence. Answer each carefully (Yes, No, Unclear) and provide your reasoning and confidence (High, Medium, Low).

Provide your analysis according to the structured JSON schema. Make sure `image_id` matches the input '{image_id}'.
"""
        # Log the interaction internally
        system_logger.log_interaction("VisualInspector", prompt, {
            "sub_claims": [sc.model_dump() for sc in decomposed_claim.sub_claims],
            "image_path": image_path,
            "evidence_req": evidence_req
        })

        try:
            result = llm_client.analyze_image_structured(prompt, image_path, ImageAnalysisReport)
            system_logger.log_interaction("VisualInspector", "Parsed output successfully", result.model_dump())
            return result
        except Exception as e:
            system_logger.error(f"Error in VisualInspector for image {image_id}: {e}")
            raise
