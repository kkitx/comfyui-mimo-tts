# ComfyUI MiMo TTS

A ComfyUI speech synthesis plugin based on Xiaomi MiMo TTS API. Supports preset voices, voice cloning, voice design, script-based batch dubbing, and audio concatenation.

## Features

- **MiMo TTS Preset Voices** - 8 preset voices + 18 emotion tags
- **MiMo Voice Clone** - Upload a reference audio to clone any voice
- **MiMo Voice Design** - Describe the voice style in text
- **MiMo Script Player** - Batch generate multi-character dialogues from JSON scripts
- **MiMo Audio Concat** - Merge multiple audio clips into one

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

## Requirements

- ComfyUI 0.25.0+
- PyTorch
- torchaudio (required for voice clone and audio concat)
- ffmpeg (optional, used for WAV concatenation in script player; falls back to Python native concat if not installed)

## License

MIT
