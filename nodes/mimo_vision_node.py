"""MiMo 多模态反推提示词节点"""
import base64, io, json, urllib.request, numpy as np
from PIL import Image
from .config import get_api_config

MODELS = [
    "mi/mimo-v2.5",
    "mi/mimo-v2.5-pro",
]

PROMPT_TEMPLATES = {
    "图片反推": "请仔细观察这张图片，用英文写出详细的画面描述（prompt），适合用于AI图片生成。包括主体、风格、构图、光影、色调等细节。",
    "视频反推": "请仔细观看这段视频，用英文写出详细的画面描述（prompt），适合用于AI视频生成。包括场景、动作、运镜、风格等细节。",
    "音频描述": "请仔细聆听这段音频，用中文描述你听到的内容，包括语音内容、背景音、情绪等。（需要模型支持音频输入）",
    "中译英": "请将以下中文提示词翻译成自然流畅的英文，保持提示词风格，适合用于AI图片/视频生成：",
    "英译中": "Please translate the following English prompt into natural Chinese, keeping the prompt style suitable for AI image/video generation:",
    "自定义": "",
}


def encode_image_b64(image_tensor):
    i = 255.0 * image_tensor.cpu().numpy()[0]
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def encode_video_b64(video):
    for attr in ("path", "file"):
        if hasattr(video, attr):
            path = getattr(video, attr, None)
            if isinstance(path, str):
                import os
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")
    if hasattr(video, "save_to"):
        import os, tempfile
        tmp = os.path.join(tempfile.gettempdir(), f"mimo_vid_{id(video)}.mp4")
        try:
            video.save_to(tmp)
            with open(tmp, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    raise ValueError(f"无法读取视频数据: {type(video)}")


def encode_audio_b64(audio_dict):
    waveform = audio_dict["waveform"]
    sr = audio_dict["sample_rate"]
    if waveform.dim() == 3:
        waveform = waveform[0]
    if waveform.dim() == 2 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0)
    elif waveform.dim() == 2:
        waveform = waveform[0]
    waveform = (waveform.cpu().numpy() * 32767).astype(np.int16)
    buf = io.BytesIO()
    import wave
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(waveform.tobytes())
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class MiMoVisionNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (MODELS, {"default": "mi/mimo-v2.5", "tooltip": "注意: mimo-v2.5-pro 不是多模态模型，仅支持纯文本对话"}),
                "prompt_template": (list(PROMPT_TEMPLATES.keys()), {"default": "图片反推"}),
                "custom_prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "选择\"自定义\"时使用"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "video": ("VIDEO",),
                "audio": ("AUDIO",),
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "中译英/英译时输入要翻译的文本，可连接 ShowText 或其他节点的 STRING 输出"}),
                "api_key": ("STRING", {"default": "", "tooltip": "留空读config.env"}),
                "api_base": ("STRING", {"default": "", "tooltip": "留空读config.env"}),
            },
            "hidden": {
                "temperature": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "run"
    CATEGORY = "MiMo TTS"

    def run(self, **kwargs):
        model = kwargs.get("model", "mi/mimo-v2.5")
        prompt_template = kwargs.get("prompt_template", "图片反推")
        custom_prompt = kwargs.get("custom_prompt", "")
        image = kwargs.get("image", None)
        video = kwargs.get("video", None)
        audio = kwargs.get("audio", None)
        text = str(kwargs.get("text", ""))
        temperature = float(kwargs.get("temperature", 0.6) or 0.6)
        api_key = str(kwargs.get("api_key", ""))
        api_base = str(kwargs.get("api_base", ""))

        key, base = get_api_config(api_key.strip(), api_base.strip())
        if not key:
            return ("错误: 请填入api_key或设置config.env",)

        base_text = custom_prompt if prompt_template == "自定义" else PROMPT_TEMPLATES[prompt_template]

        if prompt_template in ("中译英", "英译中"):
            if not str(text).strip():
                return ("错误: 中译英/英译中 需要输入要翻译的文本",)
            full_text = f"{base_text}\n\n{text}"
        else:
            full_text = base_text

        content_parts = [{"type": "text", "text": full_text}]

        if image is not None:
            b64 = encode_image_b64(image)
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })

        if video is not None:
            b64 = encode_video_b64(video)
            content_parts.append({
                "type": "video_url",
                "video_url": {"url": f"data:video/mp4;base64,{b64}"}
            })

        if audio is not None:
            b64 = encode_audio_b64(audio)
            content_parts.append({
                "type": "audio_url",
                "audio_url": {"url": f"data:audio/wav;base64,{b64}"}
            })

        if len(content_parts) == 1 and prompt_template not in ("中译英", "英译中"):
            return ("错误: 请至少连接一个 image、video 或 audio 输入",)

        messages = [
            {"role": "system", "content": "你是一个专业的多模态分析助手，擅长从图片、视频、音频中提取详细描述。"},
            {"role": "user", "content": content_parts},
        ]

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }).encode()

        req = urllib.request.Request(
            f"{base}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            return (result["choices"][0]["message"]["content"],)
        except Exception as e:
            return (f"错误: {str(e)}",)
