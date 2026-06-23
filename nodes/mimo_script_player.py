"""MiMo Script Player 剧本批量配音节点"""
import base64, json, os, shutil, subprocess, urllib.request, wave, io
from pathlib import Path
from .config import get_api_config, wav_to_audio, empty

def _find_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    for p in [r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]:
        if os.path.isfile(p):
            return p
    return None

def _find_ffprobe():
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        return ffprobe
    for p in [r"C:\ffmpeg\bin\ffprobe.exe", r"C:\Program Files\ffmpeg\bin\ffprobe.exe"]:
        if os.path.isfile(p):
            return p
    return None

def _concat_wavs_python(wav_files, output_path):
    with wave.open(wav_files[0], "rb") as first:
        params = first.getparams()
        all_frames = first.readframes(first.getnframes())
    for f in wav_files[1:]:
        with wave.open(f, "rb") as w:
            all_frames += w.readframes(w.getnframes())
    with wave.open(str(output_path), "wb") as out:
        out.setparams(params)
        out.writeframes(all_frames)

try:
    import folder_paths
    TEMP_DIR = Path(folder_paths.get_temp_directory())
except ImportError:
    TEMP_DIR = Path(os.path.expanduser("~/.comfyui/temp"))

class MiMoScriptPlayerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script_json": ("STRING", {"multiline": True, "default": '{\n  "characters": {\n    "小玲": {"voice": "冰糖"},\n    "哥哥": {"voice": "白桦"}\n  },\n  "lines": [\n    {"char": "小玲", "text": "你好！"},\n    {"char": "哥哥", "text": "你好啊！"}\n  ]\n}'}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "api_base": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "play_script"
    CATEGORY = "MiMo TTS"

    def play_script(self, script_json, api_key="", api_base=""):
        key, base = get_api_config(api_key, api_base)
        if not key:
            return (empty(), "错误: 请填入api_key或设置config.env")
        try:
            script = json.loads(script_json)
        except json.JSONDecodeError as e:
            return (empty(), f"错误: {e}")
        characters = script.get("characters", {})
        lines = script.get("lines", [])
        if not lines:
            return (empty(), "错误: 没有台词")
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        out_dir = TEMP_DIR / f"script_{id(script)}"
        out_dir.mkdir(exist_ok=True)
        wav_files, errors = [], []
        for i, line in enumerate(lines, 1):
            char = line.get("char", "?")
            text = line.get("text", "")
            voice = characters.get(char, {}).get("voice", "冰糖")
            context = characters.get(char, {}).get("context", "")
            try:
                messages = []
                if context:
                    messages.append({"role": "user", "content": context})
                messages.append({"role": "assistant", "content": text})
                payload = json.dumps({"model": "mi/mimo-v2.5-tts", "messages": messages, "audio": {"format": "wav", "voice": voice}}).encode()
                req = urllib.request.Request(f"{base}/chat/completions", data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
                result = json.loads(urllib.request.urlopen(req, timeout=120).read())
                wav = out_dir / f"{i:03d}_{char}.wav"
                wav.write_bytes(base64.b64decode(result["choices"][0]["message"]["audio"]["data"]))
                wav_files.append(str(wav))
            except Exception as e:
                errors.append(f"第{i}句: {e}")
        if not wav_files:
            return (empty(), f"全部失败: {errors[:3]}")
        list_file = out_dir / "list.txt"
        with open(list_file, "w") as f:
            for p in wav_files:
                f.write(f"file '{p.replace(chr(92), '/')}'\n")
        final = out_dir / "final.wav"
        ffmpeg = _find_ffmpeg()
        if ffmpeg:
            r = subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(final)], capture_output=True, text=True)
            if r.returncode != 0 or not final.exists():
                _concat_wavs_python(wav_files, final)
        else:
            _concat_wavs_python(wav_files, final)
        if final.exists():
            ffprobe = _find_ffprobe()
            if ffprobe:
                dur = float(subprocess.check_output([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(final)]).decode().strip())
            else:
                with wave.open(str(final), "rb") as wf:
                    dur = wf.getnframes() / wf.getframerate()
            info = f"剧本: {len(wav_files)}/{len(lines)}句 | {dur:.1f}s"
            if errors:
                info += f" | {len(errors)}句失败"
            return (wav_to_audio(final.read_bytes()), info)
        return (empty(), "拼接失败")
