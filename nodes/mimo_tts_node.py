"""MiMo TTS 预置音色语音合成节点"""
import base64, json, wave, io, urllib.request
from .config import get_api_config, wav_to_audio, empty

PRESET_VOICES = ["冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"]
EMOTION_PRESETS = ["无", "(开心)", "(悲伤)", "(愤怒)", "(温柔)", "(紧张)", "(慵懒)", "(激动)", "(冷漠)", "(哽咽)", "(低语)", "(喊话)", "(叹气)", "(笑)", "(东北话)", "(四川话)", "(粤语)", "(唱歌)"]

class MiMoTTSNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "你好！"}),
                "voice": (PRESET_VOICES, {"default": "冰糖"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": "MiMo API Key，留空读config.env"}),
                "api_base": ("STRING", {"default": "", "tooltip": "API地址，留空用默认"}),
                "context": ("STRING", {"multiline": True, "default": ""}),
                "emotion": (EMOTION_PRESETS, {"default": "无"}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "generate"
    CATEGORY = "MiMo TTS"

    def generate(self, text, voice, api_key="", api_base="", context="", emotion="无"):
        if emotion != "无":
            text = f"{emotion}{text}"
        key, base = get_api_config(api_key, api_base)
        if not key:
            return (empty(), "错误: 请填入api_key或设置config.env")
        try:
            messages = []
            if context:
                messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": text})
            payload = json.dumps({"model": "mi/mimo-v2.5-tts", "messages": messages, "audio": {"format": "wav", "voice": voice}}).encode()
            req = urllib.request.Request(f"{base}/chat/completions", data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            result = json.loads(urllib.request.urlopen(req, timeout=120).read())
            audio_bytes = base64.b64decode(result["choices"][0]["message"]["audio"]["data"])
            audio = wav_to_audio(audio_bytes)
            dur = audio["waveform"].shape[-1] / audio["sample_rate"]
            return (audio, f"音色: {voice} | 时长: {dur:.1f}s")
        except Exception as e:
            return (empty(), f"错误: {str(e)}")
