"""共享配置"""
import os
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent

def get_api_config(api_key="", api_base=""):
    key = api_key.strip() if api_key else ""
    base = api_base.strip() if api_base else ""
    # 1. 节点参数优先
    if key and base:
        return key, base
    if key:
        return key, "https://api.xiaomimimo.com/v1"
    # 2. config.env
    cfg = PLUGIN_DIR / "config.env"
    if cfg.exists():
        with open(cfg) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MIMO_API_KEY="):
                    key = line.split("=", 1)[1]
                elif line.startswith("MIMO_API_BASE=") and not base:
                    base = line.split("=", 1)[1]
    if key and base:
        return key, base
    if key:
        return key, base or "https://api.xiaomimimo.com/v1"
    # 3. 环境变量
    key = os.environ.get("MIMO_API_KEY", "")
    base = base or os.environ.get("MIMO_API_BASE", "https://api.xiaomimimo.com/v1")
    if key:
        return key, base
    # 4. ~/.hermes/.env
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith("MIMO_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    break
    return key, base or "https://api.xiaomimimo.com/v1"

def wav_to_audio(wav_bytes):
    import io, wave, torch, numpy as np
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr, ch, sw = wf.getframerate(), wf.getnchannels(), wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    if sw == 2:
        arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 4:
        arr = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        arr = arr.reshape(-1, ch).T
    else:
        arr = arr.reshape(1, -1)
    return {"waveform": torch.from_numpy(arr).unsqueeze(0), "sample_rate": sr}

def empty():
    import torch
    return {"waveform": torch.zeros(1, 1, 1), "sample_rate": 24000}
