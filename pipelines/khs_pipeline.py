from services.db_insert import insert_khs_from_json

def run_khs_pipeline(user_id: str, khs_json: dict):
    insert_khs_from_json(khs_json, user_id)