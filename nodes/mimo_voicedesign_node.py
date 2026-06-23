"""MiMo Voice Design 音色设计节点"""
import base64, json, urllib.request
from .config import get_api_config, wav_to_audio, empty

class MiMoVoiceDesignNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "你好，这是一段测试语音。"}),
                "voice_description": ("STRING", {"multiline": True, "default": "青年女性，声音甜美温柔"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "api_base": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "generate"
    CATEGORY = "MiMo TTS"

    def generate(self, text, voice_description, api_key="", api_base=""):
        key, base = get_api_config(api_key, api_base)
        if not key:
            return (empty(), "错误: 请填入api_key或设置config.env")
        try:
            messages = [{"role": "user", "content": voice_description}, {"role": "assistant", "content": text}]
            payload = json.dumps({"model": "mi/mimo-v2.5-tts-voicedesign", "messages": messages, "audio": {"format": "wav"}}).encode()
            req = urllib.request.Request(f"{base}/chat/completions", data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            result = json.loads(urllib.request.urlopen(req, timeout=120).read())
            audio = wav_to_audio(base64.b64decode(result["choices"][0]["message"]["audio"]["data"]))
            dur = audio["waveform"].shape[-1] / audio["sample_rate"]
            return (audio, f"音色设计: {voice_description[:30]}... | {dur:.1f}s")
        except Exception as e:
            return (empty(), f"错误: {str(e)}")
