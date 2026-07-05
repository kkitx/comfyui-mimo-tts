from .mimo_tts_node import MiMoTTSNode
from .mimo_script_player import MiMoScriptPlayerNode
from .mimo_audio_concat import MiMoAudioConcatNode
from .mimo_voiceclone_node import MiMoVoiceCloneNode
from .mimo_voicedesign_node import MiMoVoiceDesignNode
from .mimo_vision_node import MiMoVisionNode

NODE_CLASS_MAPPINGS = {
    "MiMo TTS": MiMoTTSNode,
    "MiMo Script Player": MiMoScriptPlayerNode,
    "MiMo Audio Concat": MiMoAudioConcatNode,
    "MiMo Voice Clone": MiMoVoiceCloneNode,
    "MiMo Voice Design": MiMoVoiceDesignNode,
    "MiMo Vision": MiMoVisionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MiMo TTS": "MiMo TTS 预置音色",
    "MiMo Script Player": "MiMo 剧本配音",
    "MiMo Audio Concat": "MiMo 音频拼接",
    "MiMo Voice Clone": "MiMo 音色克隆",
    "MiMo Voice Design": "MiMo 音色设计",
    "MiMo Vision": "MiMo 多模态反推",
}
