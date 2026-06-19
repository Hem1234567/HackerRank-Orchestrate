from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

# --- Enums matching the Hackathon problem_statement.md ---

ClaimStatus = Literal["supported", "contradicted", "not_enough_information"]

IssueType = Literal[
    "dent", "scratch", "crack", "glass_shatter", "broken_part", "missing_part",
    "torn_packaging", "crushed_packaging", "water_damage", "stain", "none", "unknown"
]

ObjectPart = Literal[
    "front_bumper", "rear_bumper", "door", "hood", "windshield", "side_mirror",
    "headlight", "taillight", "fender", "quarter_panel", "body", "unknown",
    "screen", "keyboard", "trackpad", "hinge", "lid", "corner", "port", "base",
    "box", "package_corner", "package_side", "seal", "label", "contents", "item"
]

RiskFlag = Literal[
    "none", "blurry_image", "cropped_or_obstructed", "low_light_or_glare", "wrong_angle",
    "wrong_object", "wrong_object_part", "damage_not_visible", "claim_mismatch",
    "possible_manipulation", "non_original_image", "text_instruction_present",
    "user_history_risk", "manual_review_required"
]

Severity = Literal["none", "low", "medium", "high", "unknown"]

ClaimObject = Literal["car", "laptop", "package"]

# --- Internal Pipeline Models ---

class SubClaim(BaseModel):
    id: str
    question: str

class DecomposedClaim(BaseModel):
    core_claim: str
    sub_claims: List[SubClaim]

class EvidenceReport(BaseModel):
    sub_claim_id: str
    answer: Literal["Yes", "No", "Unclear"]
    reasoning: str
    confidence: Literal["High", "Medium", "Low"]

class ImageAnalysisReport(BaseModel):
    image_id: str
    evidences: List[EvidenceReport]
    evidence_standard_met: bool = Field(description="True if the image is sufficient to evaluate the claim.")
    evidence_standard_met_reason: str = Field(description="Short reason for the evidence decision.")
    valid_image: bool = Field(description="True if the image is usable for automated review.")
    quality_issues: Optional[List[RiskFlag]] = Field(default=[], description="List of any image quality or mismatch risk flags.")

class FinalVerdict(BaseModel):
    claim_status: ClaimStatus
    issue_type: IssueType
    object_part: ObjectPart
    claim_status_justification: str
    supporting_image_ids: List[str]

class RiskAssessment(BaseModel):
    risk_flags: List[RiskFlag]
    severity: Severity

class OutputRow(BaseModel):
    user_id: str
    image_paths: str
    user_claim: str
    claim_object: ClaimObject
    evidence_standard_met: bool
    evidence_standard_met_reason: str
    risk_flags: str  # semicolon separated
    issue_type: IssueType
    object_part: str
    claim_status: ClaimStatus
    claim_status_justification: str
    supporting_image_ids: str  # semicolon separated
    valid_image: bool
    severity: Severity
