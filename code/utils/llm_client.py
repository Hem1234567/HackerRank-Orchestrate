import os
import json
import base64
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
        else:
            self.client = None
            print("Warning: OPENROUTER_API_KEY not found. LLM calls will fail unless mocked.")

    def generate_structured(self, prompt: str, response_schema: type[BaseModel], model_name: str = "openai/gpt-4o-mini") -> BaseModel:
        if not self.client:
            return self._get_mock_data(response_schema)
        
        schema_json = response_schema.model_json_schema()
        full_prompt = f"{prompt}\n\nYou MUST return ONLY valid JSON matching this schema:\n{json.dumps(schema_json)}"
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=1500
        )
        return response_schema.model_validate_json(response.choices[0].message.content)

    def analyze_image_structured(self, prompt: str, image_path: str, response_schema: type[BaseModel], model_name: str = "openai/gpt-4o") -> BaseModel:
        if not self.client:
            return self._get_mock_data(response_schema)
            
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        schema_json = response_schema.model_json_schema()
        full_prompt = f"{prompt}\n\nYou MUST return ONLY valid JSON matching this schema:\n{json.dumps(schema_json)}"
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=1500
        )
        return response_schema.model_validate_json(response.choices[0].message.content)

    def _get_mock_data(self, response_schema: type[BaseModel]) -> BaseModel:
        schema_name = response_schema.__name__
        if schema_name == "DecomposedClaim":
            return response_schema.model_validate({
                "core_claim": "The laptop screen is cracked.",
                "sub_claims": [
                    {"id": "SC1", "question": "Is there a laptop in the image?"},
                    {"id": "SC2", "question": "Is there a visible crack on the screen?"}
                ]
            })
        elif schema_name == "ImageAnalysisReport":
            return response_schema.model_validate({
                "image_id": "mock_id",
                "evidences": [
                    {"sub_claim_id": "SC1", "answer": "Yes", "reasoning": "A laptop is clearly visible.", "confidence": "High"},
                    {"sub_claim_id": "SC2", "answer": "Yes", "reasoning": "There is a crack running across the top right of the screen.", "confidence": "High"}
                ],
                "image_quality_issues": "None",
                "potential_mismatch": False
            })
        elif schema_name == "FinalVerdict":
            return response_schema.model_validate({
                "decision": "Supported",
                "visible_issue_type": "Cracked Screen",
                "relevant_object_part": "Screen",
                "supporting_image_ids": ["img_001"],
                "justification": "The image clearly shows a laptop with a visible crack on the screen, supporting the user's claim."
            })
        elif schema_name == "RiskAssessment":
            return response_schema.model_validate({
                "risk_flags": [],
                "severity": "Low"
            })
        else:
            raise ValueError(f"No mock data for schema {schema_name}")

llm_client = LLMClient()
