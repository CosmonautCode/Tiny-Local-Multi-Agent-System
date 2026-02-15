
from llama_cpp import Llama
from pathlib import Path

MODEL_PATH = Path("app/models/qwen2.5-1.5b-instruct-q8_0.gguf")

def load_multiple_instances(n_instances=2):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    instances = []
    for _ in range(n_instances):
        llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=8192,  # Full capacity - only loading 1 instance total
            n_threads=8,
            n_gpu_layers=-1,
            verbose=False,
            chat_format="chatml"
        )
        instances.append(llm)
    
    return instances

