import json
import logging
from datetime import datetime
import os

class ChatLogger:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"transcript_{self.session_id}.jsonl")
        
        # Setup basic standard logging as well
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("DamageClaimSystem")

    def log_interaction(self, agent_name: str, input_data: any, output_data: any, prompt: str = ""):
        """Logs the interaction to a JSONL file for transcript auditing."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt,
            "input": input_data if isinstance(input_data, (str, dict, list)) else str(input_data),
            "output": output_data if isinstance(output_data, (str, dict, list)) else str(output_data)
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        self.logger.info(f"[{agent_name}] Interaction logged.")

    def info(self, message: str):
        self.logger.info(message)
        
    def error(self, message: str):
        self.logger.error(message)

# Global logger instance
system_logger = ChatLogger()
