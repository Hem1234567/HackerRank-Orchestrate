import os
import pandas as pd
from pipeline import DamageClaimPipeline
from utils.logger import system_logger

def load_data(base_path: str):
    claims_df = pd.read_csv(os.path.join(base_path, "dataset/claims.csv"))
    user_history_df = pd.read_csv(os.path.join(base_path, "dataset/user_history.csv"))
    evidence_req_df = pd.read_csv(os.path.join(base_path, "dataset/evidence_requirements.csv"))
    return claims_df, user_history_df, evidence_req_df

def process_row(row, user_history_df, evidence_req_df, pipeline, base_path):
    user_id = row['user_id']
    claim_id = f"CLAIM-{row.name}"  # Create a synthetic claim ID for logs
    conversation = row['user_claim']
    claim_object = row['claim_object']
    image_paths_raw = row['image_paths'].split(';')

    # Construct full paths and image dicts
    images = []
    for path in image_paths_raw:
        full_path = os.path.join(base_path, "dataset", path.strip())
        img_id = os.path.splitext(os.path.basename(full_path))[0]
        images.append({"id": img_id, "path": full_path})

    # Get user history
    user_history = user_history_df[user_history_df['user_id'] == user_id]
    if not user_history.empty:
        user_history_dict = user_history.iloc[0].to_dict()
    else:
        user_history_dict = {
            "past_claim_count": 0, "last_90_days_claim_count": 0, 
            "history_flags": "none", "history_summary": "No prior history"
        }

    # Run pipeline
    output = pipeline.process_claim(
        user_id=user_id,
        claim_id=claim_id,
        conversation=conversation,
        claim_object=claim_object,
        images=images,
        user_history=user_history_dict,
        evidence_requirements=evidence_req_df
    )
    return output

def main():
    print("--- HackerRank Orchestrate Pipeline ---")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        claims_df, user_history_df, evidence_req_df = load_data(base_path)
    except FileNotFoundError as e:
        print(f"Error loading dataset: {e}. Are you running from the right directory?")
        return

    print(f"Loaded {len(claims_df)} claims to process.")
    
    pipeline = DamageClaimPipeline()
    all_outputs = []

    for index, row in claims_df.iterrows():
        print(f"\nProcessing row {index + 1}/{len(claims_df)} for user {row['user_id']}...")
        try:
            output = process_row(row, user_history_df, evidence_req_df, pipeline, base_path)
            all_outputs.append(output)
            print(f" -> Decision: {output.claim_status} | Issue: {output.issue_type}")
        except Exception as e:
            print(f" -> Failed to process row {index}: {e}")
            # If a row fails, we still need to provide an output for it.
            # We can create a fallback output.
            from models import OutputRow
            fallback = OutputRow(
                user_id=row['user_id'],
                image_paths=row['image_paths'],
                user_claim=row['user_claim'],
                claim_object=row['claim_object'],
                evidence_standard_met=False,
                evidence_standard_met_reason=f"Pipeline error: {str(e)}",
                risk_flags="manual_review_required",
                issue_type="unknown",
                object_part="unknown",
                claim_status="not_enough_information",
                claim_status_justification="Pipeline encountered a critical error during processing.",
                supporting_image_ids="none",
                valid_image=False,
                severity="unknown"
            )
            all_outputs.append(fallback)

    output_csv_path = os.path.join(base_path, "output.csv")
    pipeline.export_to_csv(all_outputs, output_csv_path)
    print(f"\nPipeline complete. Results written to {output_csv_path}")

if __name__ == "__main__":
    main()
