# ComfyUI MiMo TTS

基于小米 MiMo TTS API 的 ComfyUI 语音合成插件，支持预置音色、音色克隆、音色设计、剧本批量配音和音频拼接。

## 功能

- **MiMo TTS 预置音色** - 8种预设音色 + 18种情感标签
- **MiMo 音色克隆** - 上传参考音频，克隆任意音色
- **MiMo 音色设计** - 用文字描述自定义音色
- **MiMo 剧本配音** - JSON 剧本批量生成多角色对话
- **MiMo 音频拼接** - 将多个音频合并为一个

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/你的用户名/comfyui-mimo-tts.git
```

或直接将 `comfyui-mimo-tts` 文件夹放入 `ComfyUI/custom_nodes/` 目录。

## 配置

编辑 `config.env` 文件，填入你的 API Key：

```
MIMO_API_KEY=你的API密钥
MIMO_API_BASE=http://你的服务器地址/v1
```

也可在节点界面直接填入 `api_key` 和 `api_base`（优先级更高）。

## 节点说明

### MiMo TTS 预置音色

| 参数 | 说明 |
|------|------|
| text | 要合成的文本 |
| voice | 音色：冰糖/茉莉/苏打/白桦/Mia/Chloe/Milo/Dean |
| emotion | 情感标签（可选） |

### MiMo 音色克隆

| 参数 | 说明 |
|------|------|
| text | 要合成的文本 |
| voice_audio | 接入 Load Audio 节点的参考音频 |
| voice_file | 或手动输入音频文件路径 |

### MiMo 音色设计

| 参数 | 说明 |
|------|------|
| text | 要合成的文本 |
| voice_description | 音色描述，如"青年女性，声音甜美温柔" |

### MiMo 剧本配音

输入 JSON 格式剧本：

```json
{
  "characters": {
    "小玲": {"voice": "冰糖"},
    "哥哥": {"voice": "白桦"}
  },
  "lines": [
    {"char": "小玲", "text": "你好！"},
    {"char": "哥哥", "text": "你好啊！"}
  ]
}
```

### MiMo 音频拼接

将多个 AUDIO 输出连接起来，最多支持 5 路输入。不同采样率自动重采样。

## 使用示例

### 基础用法

```
MiMo TTS → PreviewAudio
```

### 多角色对话

```
MiMo TTS (小玲) ──→ audio_1 ──┐
                                ├──→ MiMo Audio Concat → SaveAudio
MiMo TTS (哥哥) ──→ audio_2 ──┘
```

### 音色克隆

```
Load Audio → MiMo Voice Clone → PreviewAudio
```

## 依赖

- ComfyUI 0.25.0+
- PyTorch
- torchaudio（音色克隆和音频拼接需要）
- ffmpeg（可选，剧本配音的 WAV 拼接需要，未安装时自动使用 Python 原生拼接）

## License

MIT
