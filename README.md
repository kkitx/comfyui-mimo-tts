# ComfyUI MiMo TTS

A ComfyUI speech synthesis plugin based on Xiaomi MiMo TTS API. Supports preset voices, voice cloning, voice design, script-based batch dubbing, audio concatenation, and multimodal prompt reverse engineering.

## Features

- **MiMo TTS Preset Voices** - 8 preset voices + 18 emotion tags
- **MiMo Voice Clone** - Upload a reference audio to clone any voice
- **MiMo Voice Design** - Describe the voice style in text
- **MiMo Script Player** - Batch generate multi-character dialogues from JSON scripts
- **MiMo Audio Concat** - Merge multiple audio clips into one
- **MiMo Vision** - Multimodal prompt reverse engineering for images, videos, and audio
- **Prompt Translation** - Chinese-English translation for prompts

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/comfyui-mimo-tts.git
```

Or simply place the `comfyui-mimo-tts` folder into `ComfyUI/custom_nodes/`.

## Configuration

Edit the `config.env` file with your API key:

```
MIMO_API_KEY=your-api-key
MIMO_API_BASE=http://your-server-address/v1
```

You can also enter `api_key` and `api_base` directly in the node settings (higher priority).

## Nodes

### MiMo TTS Preset Voices

| Parameter | Description |
|-----------|-------------|
| text | Text to synthesize |
| voice | Voice: BingTang / MoLi / SuDa / BaiHua / Mia / Chloe / Milo / Dean |
| emotion | Emotion tag (optional) |

### MiMo Voice Clone

| Parameter | Description |
|-----------|-------------|
| text | Text to synthesize |
| voice_audio | Connect a reference audio from Load Audio node |
| voice_file | Or manually enter an audio file path |

### MiMo Voice Design

| Parameter | Description |
|-----------|-------------|
| text | Text to synthesize |
| voice_description | Voice description, e.g. "young female, sweet and gentle voice" |

### MiMo Script Player

Input a JSON script:

```json
{
  "characters": {
    "XiaoLing": {"voice": "BingTang"},
    "Brother": {"voice": "BaiHua"}
  },
  "lines": [
    {"char": "XiaoLing", "text": "Hello!"},
    {"char": "Brother", "text": "Hey there!"}
  ]
}
```

### MiMo Audio Concat

Connect multiple AUDIO outputs together. Supports up to 5 inputs. Different sample rates are automatically resampled.

### MiMo Vision

Multimodal prompt reverse engineering using MiMo's vision capabilities. Supports images, videos, and audio inputs.

| Parameter | Description |
|-----------|-------------|
| model | Model: mi/mimo-v2.5 (multimodal) or mi/mimo-v2.5-pro (text only) |
| prompt_template | Preset: Image Reverse / Video Reverse / Audio Description / Chinese to English / English to Chinese / Custom |
| custom_prompt | Custom prompt text (used when "Custom" is selected) |
| image | Connect an IMAGE input for image-to-prompt |
| video | Connect a VIDEO input for video-to-prompt |
| audio | Connect an AUDIO input for audio description |
| text | Text to translate (for Chinese-English translation) |
| temperature | Generation temperature (default: 0.6) |

## Usage Examples

### Basic

```
MiMo TTS → PreviewAudio
```

### Multi-character Dialogue

```
MiMo TTS (XiaoLing) ──→ audio_1 ──┐
                                    ├──→ MiMo Audio Concat → SaveAudio
MiMo TTS (Brother)  ──→ audio_2 ──┘
```

### Voice Cloning

```
Load Audio → MiMo Voice Clone → PreviewAudio
```

### Image Prompt Reverse Engineering

```
Load Image → MiMo Vision (Image Reverse) → ShowText
```

### Video Prompt Reverse Engineering

```
Load Video → MiMo Vision (Video Reverse) → ShowText
```

### Audio Description

```
MiMo TTS → [audio] → MiMo Vision (Audio Description) → ShowText
```

### TTS → Vision Pipeline

```
MiMo TTS → MiMo Vision (Audio Description) → ShowText
```

### Prompt Translation

```
[中文提示词] → MiMo Vision (中译英) → [英文提示词] → SD/Flux
```

```
[English prompt] → MiMo Vision (英译中) → [中文提示词] → ShowText
```

## Requirements

- ComfyUI 0.25.0+
- PyTorch
- torchaudio (required for voice clone and audio concat)
- ffmpeg (optional, used for WAV concatenation in script player; falls back to Python native concat if not installed)

## License

MIT
