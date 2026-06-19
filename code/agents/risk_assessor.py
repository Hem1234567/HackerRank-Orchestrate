from models import RiskAssessment
from typing import List, Dict
from utils.logger import system_logger

class RiskAssessor:
    def process(self, evidence_reports: List[Dict], user_history: Dict, llm_client) -> RiskAssessment:
        prompt = f"""
You are a fraud and risk assessment AI for an insurance claims system.
Review the following visual analysis reports and user history data to determine the risk level of the claim.

Visual Analysis Reports:
"""
        for report in evidence_reports:
            prompt += f"\nImage ID: {report['image_id']}\n"
            prompt += f"  - Quality Issues: {report.get('quality_issues', [])}\n"

        prompt += f"""
User History:
- Past Claim Count: {user_history.get('past_claim_count')}
- Last 90 Days Count: {user_history.get('last_90_days_claim_count')}
- History Flags: {user_history.get('history_flags')}
- Summary: {user_history.get('history_summary')}

Task:
Identify any risk flags. The allowed risk flags are:
blurry_image, cropped_or_obstructed, low_light_or_glare, wrong_angle, wrong_object, wrong_object_part, damage_not_visible, claim_mismatch, possible_manipulation, non_original_image, text_instruction_present, user_history_risk, manual_review_required.

Include any relevant flags from the image quality issues or the user history. If there are no flags, output an empty list or ["none"].
Assign a severity level: "none", "low", "medium", "high", or "unknown".

Provide your assessment following the structured JSON schema exactly.
"""
        system_logger.log_interaction("RiskAssessor", prompt, {
            "reports": evidence_reports,
            "history": user_history
        })

        try:
            result = llm_client.generate_structured(prompt, RiskAssessment)
            system_logger.log_interaction("RiskAssessor", "Parsed output successfully", result.model_dump())
            return result
        except Exception as e:
            system_logger.error(f"Error in RiskAssessor: {e}")
            raise
