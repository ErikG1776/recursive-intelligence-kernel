import requests
from typing import Optional, Dict, Any

class RIKClient:
    """
    Lightweight Python SDK for the Recursive Intelligence Kernel (RIK) API.
    Allows local or remote interaction with the kernel's reasoning, memory, and meta modules.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def run_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a recursive reasoning run.
        """
        response = requests.post(f"{self.base_url}/run_task", json={"task": task})
        response.raise_for_status()
        return response.json()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Fetch architecture fitness and performance metrics.
        """
        response = requests.get(f"{self.base_url}/metrics")
        response.raise_for_status()
        return response.json()

    def get_memory(self) -> Dict[str, Any]:
        """
        Retrieve the latest episodic memory entries.
        """
        response = requests.get(f"{self.base_url}/memory")
        response.raise_for_status()
        return response.json()