import time
import threading
import requests
from ..workers.compression_worker import CompressionWorker
from ..workers.replay_worker import ReplayWorker
from ..workers.ranking_worker import RankingWorker
from ..workers.forgetting_worker import ForgettingWorker
from ..workers.meta_memory_worker import MetaMemoryWorker
from ..workers.evolution_worker import EvolutionWorker

class BackgroundWorker:
    def __init__(self, memory_manager, brain_api_url="http://localhost:5000", infra_url="http://localhost:8080"):
        self.memory = memory_manager
        self.brain_api_url = brain_api_url
        self.infra_url = infra_url
        self.running = False
        
        # Specialized workers
        self.compression = CompressionWorker()
        self.replay = ReplayWorker(memory_manager)
        self.ranking = RankingWorker(memory_manager)
        self.forgetting = ForgettingWorker(memory_manager)
        self.meta_memory = MetaMemoryWorker(memory_manager)
        self.evolution = EvolutionWorker(memory_manager)

    def start(self):
        self.running = True
        threading.Thread(target=self._run_reflection, daemon=True).start()
        threading.Thread(target=self._run_clustering, daemon=True).start()
        threading.Thread(target=self._run_decay, daemon=True).start()
        threading.Thread(target=self._run_compression, daemon=True).start()
        threading.Thread(target=self._run_replay, daemon=True).start()
        threading.Thread(target=self._run_state_inference, daemon=True).start()
        threading.Thread(target=self._run_prediction, daemon=True).start()
        threading.Thread(target=self._run_ranking, daemon=True).start()
        threading.Thread(target=self._run_forgetting, daemon=True).start()
        threading.Thread(target=self._run_meta_analysis, daemon=True).start()
        threading.Thread(target=self._run_evolution, daemon=True).start()

    def _run_state_inference(self):
        while self.running:
            print("[Worker] Running latent state inference...")
            # self.memory.state_inference.infer_and_update(...)
            time.sleep(60 * 15) # Every 15 mins

    def _run_prediction(self):
        while self.running:
            print("[Worker] Running world model prediction...")
            # self.memory.prediction_engine.predict(...)
            time.sleep(60 * 30) # Every 30 mins

    def _run_reflection(self):
        while self.running:
            print("[Worker] Running periodic reflection...")
            try:
                # Trigger reflection endpoint
                requests.post(f"{self.brain_api_url}/memory/reflect")
            except Exception as e:
                print(f"[Worker] Reflection error: {e}")
            time.sleep(60 * 60) # Every hour

    def _run_clustering(self):
        while self.running:
            print("[Worker] Running periodic clustering...")
            try:
                requests.post(f"{self.infra_url}/cluster")
            except Exception as e:
                print(f"[Worker] Clustering error: {e}")
            time.sleep(60 * 120) # Every 2 hours

    def _run_decay(self):
        while self.running:
            print("[Worker] Running periodic decay compaction...")
            try:
                requests.post(f"{self.infra_url}/compact")
            except Exception as e:
                print(f"[Worker] Decay error: {e}")
            time.sleep(60 * 240) # Every 4 hours

    def _run_compression(self):
        while self.running:
            print("[Worker] Running periodic compression...")
            # Mock: Get messages from sensory and compress
            # self.compression.compress_conversations(...)
            time.sleep(60 * 30) # Every 30 mins

    def _run_replay(self):
        while self.running:
            print("[Worker] Running periodic replay...")
            # self.replay.consolidate(user_id="user_123")
            time.sleep(60 * 60 * 6) # Every 6 hours

    def _run_ranking(self):
        time.sleep(15) # Delay to avoid startup lock contention
        while self.running:
            print("[Worker] Running periodic importance ranking...")
            try:
                self.ranking.maintain_importance()
            except Exception as e:
                print(f"[Worker] Ranking error: {e}")
            time.sleep(60 * 60) # Every hour

    def _run_forgetting(self):
        time.sleep(30) # Delay after ranking
        while self.running:
            print("[Worker] Running periodic memory forgetting and cleanup...")
            try:
                self.forgetting.run_cleanup()
            except Exception as e:
                print(f"[Worker] Forgetting error: {e}")
            time.sleep(60 * 60 * 24) # Every 24 hours

    def _run_meta_analysis(self):
        time.sleep(60) # Initial delay
        while self.running:
            print("[Worker] Running periodic meta-memory analysis...")
            try:
                self.meta_memory.run_analysis()
            except Exception as e:
                print(f"[Worker] Meta-memory error: {e}")
    def _run_evolution(self):
        time.sleep(120) # Delay after meta-analysis
        while self.running:
            print("[Worker] Running periodic autonomous memory evolution (AME)...")
            try:
                self.evolution.evolve()
            except Exception as e:
                print(f"[Worker] Evolution error: {e}")
            time.sleep(60 * 60) # Every hour
