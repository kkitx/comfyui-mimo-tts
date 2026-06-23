"""MiMo Audio Concat 音频拼接节点"""
import subprocess, os, time, json, wave, shutil, io
from pathlib import Path

try:
    import folder_paths
    TEMP_DIR = Path(folder_paths.get_temp_directory())
except ImportError:
    TEMP_DIR = Path(os.path.expanduser("~/.comfyui/temp"))

import torch
import numpy as np

def wav_bytes_to_audio(wav_bytes):
    import io
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
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

def wav_file_to_audio(path):
    with open(path, "rb") as f:
        return wav_bytes_to_audio(f.read())

def empty_audio():
    return {"waveform": torch.zeros(1, 1, 1), "sample_rate": 24000}

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


class MiMoAudioConcatNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_1": ("AUDIO",),
            },
            "optional": {
                "audio_2": ("AUDIO",),
                "audio_3": ("AUDIO",),
                "audio_4": ("AUDIO",),
                "audio_5": ("AUDIO",),
                "output_name": ("STRING", {"default": "merged"}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "concat"
    CATEGORY = "MiMo TTS"

    def concat(self, audio_1, audio_2=None, audio_3=None, audio_4=None, audio_5=None, output_name="merged"):
        import torchaudio
        audios = [a for a in [audio_1, audio_2, audio_3, audio_4, audio_5] if a is not None]
        if not audios:
            return (empty_audio(), "错误: 没有音频输入")
        sr = audios[0]["sample_rate"]
        parts = []
        for a in audios:
            w = a["waveform"]
            if w.dim() == 3:
                w = w.squeeze(0)
            if w.shape[0] > 1:
                w = w.mean(dim=0, keepdim=True)
            if a["sample_rate"] != sr:
                w = torchaudio.functional.resample(w, a["sample_rate"], sr)
            parts.append(w)
        merged = torch.cat(parts, dim=-1)
        out = {"waveform": merged.unsqueeze(0), "sample_rate": sr}
        dur = merged.shape[-1] / sr
        return (out, f"拼接 {len(audios)} 段 | 总时长: {dur:.1f}s")
