import json
import os
from ..models.model_router import ModelRouter

class PredictionEngine:
    def __init__(self, storage_path="backend/storage/predictive_cache/predictions.json"):
        self.storage_path = storage_path
        self.router = ModelRouter()
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists(os.path.dirname(self.storage_path)):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)

    def predict(self, user_id, context_data):
        """
        Predicts future user behavior or needs based on context.
        """
        prompt = (
            f"Based on the user's recent activity and world states, predict their next few likely "
            f"questions or topics of interest.\n\n"
            f"Context: {json.dumps(context_data)}"
        )
        
        prediction = self.router.route("predictive_inference", prompt)
        self._save_prediction(user_id, prediction)
        return prediction

    def _save_prediction(self, user_id, prediction):
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        data[user_id] = {
            "prediction": prediction,
            "timestamp": os.path.getmtime(self.storage_path) # placeholder for real time
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f)

    def get_last_prediction(self, user_id):
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        return data.get(user_id, {}).get("prediction", "No prediction available.")
