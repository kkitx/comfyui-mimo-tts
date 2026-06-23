"""MiMo Voice Clone 音色克隆节点"""
import base64, json, io, wave, urllib.request
from pathlib import Path
import torch
import numpy as np
from .config import get_api_config, wav_to_audio, empty

def _audio_to_wav_b64(audio, target_sr=24000):
    waveform = audio["waveform"]
    sr = audio["sample_rate"]
    if waveform.dim() == 3:
        waveform = waveform.squeeze(0)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != target_sr:
        import torchaudio
        waveform = torchaudio.functional.resample(waveform, sr, target_sr)
        sr = target_sr
    pcm = (waveform.squeeze().cpu().numpy() * 32767).clip(-32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return base64.b64encode(buf.getvalue()).decode()

class MiMoVoiceCloneNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "你好，这是克隆音色的测试。"}),
            },
            "optional": {
                "voice_audio": ("AUDIO",),
                "voice_file": ("STRING", {"default": "", "tooltip": "或手动输入音频文件路径"}),
                "api_key": ("STRING", {"default": ""}),
                "api_base": ("STRING", {"default": ""}),
                "context": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "generate"
    CATEGORY = "MiMo TTS"

    def generate(self, text, voice_audio=None, voice_file="", api_key="", api_base="", context=""):
        key, base = get_api_config(api_key, api_base)
        if not key:
            return (empty(), "错误: 请填入api_key或设置config.env")
        if voice_audio is not None:
            voice_b64 = _audio_to_wav_b64(voice_audio)
        elif voice_file and Path(voice_file).exists():
            voice_b64 = base64.b64encode(Path(voice_file).read_bytes()).decode()
        else:
            return (empty(), "错误: 请连接AUDIO输入或填入音频文件路径")
        try:
            messages = []
            if context:
                messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": text})
            payload = json.dumps({"model": "mi/mimo-v2.5-tts-voiceclone", "messages": messages, "audio": {"format": "wav", "voice": f"data:audio/wav;base64,{voice_b64}"}}).encode()
            req = urllib.request.Request(f"{base}/chat/completions", data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            try:
                resp = urllib.request.urlopen(req, timeout=120)
                result = json.loads(resp.read())
            except urllib.error.HTTPError as e:
                err_body = e.read().decode(errors="replace")
                return (empty(), f"错误: HTTP {e.code} - {err_body[:200]}")
            audio = wav_to_audio(base64.b64decode(result["choices"][0]["message"]["audio"]["data"]))
            dur = audio["waveform"].shape[-1] / audio["sample_rate"]
            return (audio, f"克隆 | {dur:.1f}s")
        except Exception as e:
            return (empty(), f"错误: {str(e)}")
