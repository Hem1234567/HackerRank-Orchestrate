from typing import List, Dict, Any
from agents.extractor import ClaimExtractor
from agents.inspector import VisualInspector
from agents.judge import VerdictJudge
from agents.risk_assessor import RiskAssessor
from models import OutputRow
from utils.llm_client import LLMClient
from utils.logger import system_logger
import pandas as pd

class DamageClaimPipeline:
    def __init__(self):
        self.llm_client = LLMClient()
        self.extractor = ClaimExtractor()
        self.inspector = VisualInspector()
        self.judge = VerdictJudge()
        self.risk_assessor = RiskAssessor()

    def process_claim(self, user_id: str, claim_id: str, conversation: str, claim_object: str, images: List[Dict[str, str]], user_history: Dict, evidence_requirements: pd.DataFrame) -> OutputRow:
        system_logger.info(f"Starting pipeline for claim {claim_id}")

        # --- Stage 1: Extraction ---
        system_logger.info("Stage 1: Extracting and decomposing claim")
        decomposed_claim = self.extractor.process(conversation, self.llm_client)
        
        # Determine the appropriate evidence requirement
        # For simplicity, we query the requirement where applies_to matches the claim type if possible,
        # but since we don't have the final issue type yet, we will pass all relevant requirements for this object.
        relevant_reqs = evidence_requirements[
            (evidence_requirements['claim_object'] == claim_object) | 
            (evidence_requirements['claim_object'] == 'all')
        ]
        evidence_req_text = "\n".join([f"- {row['applies_to']}: {row['minimum_image_evidence']}" for _, row in relevant_reqs.iterrows()])

        # --- Stage 2: Visual Inspection ---
        system_logger.info("Stage 2: Visual Inspection of images")
        evidence_reports = []
        for img in images:
            report = self.inspector.process(
                claim_object=claim_object,
                decomposed_claim=decomposed_claim,
                image_path=img["path"],
                image_id=img["id"],
                evidence_req=evidence_req_text,
                llm_client=self.llm_client
            )
            evidence_reports.append(report.model_dump())

        # --- Stage 3: Verdict ---
        system_logger.info("Stage 3: Evidence Sufficiency & Judgment")
        final_verdict = self.judge.process(
            claim_object=claim_object,
            original_claim=decomposed_claim.core_claim,
            decomposed_claims=[sc.question for sc in decomposed_claim.sub_claims],
            evidence_reports=evidence_reports,
            llm_client=self.llm_client
        )

        # --- Stage 4: Risk Assessment ---
        system_logger.info("Stage 4: Risk & Quality Assessment")
        risk_assessment = self.risk_assessor.process(
            evidence_reports=evidence_reports,
            user_history=user_history,
            llm_client=self.llm_client
        )

        # Ensure evidence standard logic is combined
        # We'll take the most optimistic view: if any image meets the standard, it's true.
        evidence_met = any(r['evidence_standard_met'] for r in evidence_reports)
        # For the reason, we just take the reason from the first report, or build a combined string.
        evidence_met_reasons = [r['evidence_standard_met_reason'] for r in evidence_reports if r['evidence_standard_met_reason']]
        evidence_met_reason_str = evidence_met_reasons[0] if evidence_met_reasons else "Could not determine evidence standard."
        
        valid_image = any(r['valid_image'] for r in evidence_reports)

        system_logger.info(f"Finished pipeline for claim {claim_id}. Verdict: {final_verdict.claim_status}")

        image_paths_str = ";".join([img["path"] for img in images])
        
        # Process risk flags correctly
        # Hackathon requirement says 'none' if empty
        flags = risk_assessment.risk_flags
        if not flags or flags == ["none"]:
            risk_flags_str = "none"
        else:
            risk_flags_str = ";".join([f for f in flags if f != "none"])

        supporting_ids = final_verdict.supporting_image_ids
        if not supporting_ids or supporting_ids == ["none"]:
            supporting_ids_str = "none"
        else:
            supporting_ids_str = ";".join([i for i in supporting_ids if i != "none"])

        # Construct OutputRow
        output = OutputRow(
            user_id=user_id,
            image_paths=image_paths_str,
            user_claim=conversation,
            claim_object=claim_object,
            evidence_standard_met=evidence_met,
            evidence_standard_met_reason=evidence_met_reason_str,
            risk_flags=risk_flags_str,
            issue_type=final_verdict.issue_type,
            object_part=final_verdict.object_part,
            claim_status=final_verdict.claim_status,
            claim_status_justification=final_verdict.claim_status_justification,
            supporting_image_ids=supporting_ids_str,
            valid_image=valid_image,
            severity=risk_assessment.severity
        )

        return output

    def export_to_csv(self, outputs: List[OutputRow], output_path: str):
        import pandas as pd
        # Must produce output.csv with exact schema in problem_statement.md
        df = pd.DataFrame([out.model_dump() for out in outputs])
        
        # Convert booleans to lowercase true/false strings as is standard in CSV sometimes, 
        # but pandas true/false is okay. Let's make sure it's strictly "true" or "false".
        df['evidence_standard_met'] = df['evidence_standard_met'].apply(lambda x: 'true' if x else 'false')
        df['valid_image'] = df['valid_image'].apply(lambda x: 'true' if x else 'false')

        # Ensure exact column order
        cols = [
            "user_id", "image_paths", "user_claim", "claim_object", 
            "evidence_standard_met", "evidence_standard_met_reason", 
            "risk_flags", "issue_type", "object_part", "claim_status", 
            "claim_status_justification", "supporting_image_ids", 
            "valid_image", "severity"
        ]
        df = df[cols]
        df.to_csv(output_path, index=False)
        system_logger.info(f"Exported {len(outputs)} claims to {output_path}")
