from models import DecomposedClaim

from utils.logger import system_logger

class ClaimExtractor:
    def __init__(self):
        self.agent_name = "ClaimExtractor"

    def process(self, conversation_text: str, llm_client) -> DecomposedClaim:
        prompt = f"""
You are an expert insurance claim analyst.
Extract the core damage claim from the following conversation.
Then, decompose this claim into a series of smaller, verifiable yes/no questions (sub-claims) that can be verified by looking at images.

Conversation:
{conversation_text}

Provide your answer according to the specified JSON schema.
"""
        try:
            result = llm_client.generate_structured(prompt, DecomposedClaim)
            system_logger.log_interaction(
                agent_name=self.agent_name,
                input_data=conversation_text,
                output_data=result.model_dump(),
                prompt=prompt
            )
            return result
        except Exception as e:
            system_logger.error(f"Error in {self.agent_name}: {e}")
            raise
