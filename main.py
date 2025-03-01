import os
import wave
import json
import time
import requests
import google.generativeai as genai
import openai
import pyaudio
import anthropic
from gradio_client import Client

# 缓存变量
_cached_ref_wav_path = None
_tts_available = False
_tts_retry_count = 0
_tts_url = "http://127.0.0.1:7865"  # 默认GPT-SoVITS URL


# 初始化TTS服务
def initialize_tts():
    global _tts_available, _tts_retry_count

    # 如果已经确认TTS服务可用，直接返回
    if _tts_available:
        return True

    # 如果已经尝试超过最大重试次数，直接返回不可用
    if _tts_retry_count >= 2:
        return False

    print(f"正在检查TTS服务可用性 (尝试 {_tts_retry_count + 1}/3)...")
    try:
        # 尝试连接TTS服务
        response = requests.get(f"{_tts_url}/sdapi/v1/server-info", timeout=3)
        if response.status_code == 200:
            print("TTS服务已连接成功!")
            _tts_available = True
            return True
        else:
            print(f"TTS服务返回非200状态码: {response.status_code}")
    except Exception as e:
        print(f"无法连接到TTS服务: {str(e)}")

    # 连接失败，增加重试计数
    _tts_retry_count += 1
    return False


# 加载AI提示词预设
def load_preset(preset_name=None):
    if not preset_name:
        # 默认使用BoxBear预设
        preset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend",
                                   "_BoxBear_Gemini_Novel_V1.1_Release (1).json")
    else:
        preset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "presets")
        preset_file = os.path.join(preset_dir, f"{preset_name}.json")

    try:
        if not os.path.exists(preset_file):
            print(f"预设文件不存在: {preset_file}")
            return None

        with open(preset_file, 'r', encoding='utf-8') as f:
            preset_data = json.load(f)
            return preset_data
    except Exception as e:
        print(f"加载预设失败: {str(e)}")
        return None


# 构建提示词
def build_prompt(user_input, preset, character_content="", first_message=True, character_name=""):
    prompt_parts = []

    # 使用预设指令
    if preset and "instructions" in preset:
        for instruction in preset["instructions"]:
            if instruction.get("enabled", False) and instruction.get("content"):
                if instruction.get("role") == "system":
                    prompt_parts.append(f"<system>\n{instruction['content']}\n</system>")
                elif instruction.get("role") == "user":
                    prompt_parts.append(f"User: {instruction['content']}")
                elif instruction.get("role") == "assistant":
                    prompt_parts.append(f"Assistant: {instruction['content']}")
                else:
                    # 默认作为系统指令
                    prompt_parts.append(f"<system>\n{instruction['content']}\n</system>")

    # 角色设定（仅在第一次对话时添加）
    if first_message and character_content:
        prompt_parts.append(f"<system>\n角色设定：\n{character_content}\n</system>")

    # 用户输入
    prompt_parts.append(f"User: {user_input}")

    # 指示AI回复
    prompt_parts.append("Assistant:")

    # 结尾提示
    if first_message:
        prompt_parts.append(
            f"请根据角色设定扮演角色 {character_name}，进行回复，回复时请用""包裹说的话用（）包裹你的动作。")
    else:
        prompt_parts.append(
            f"请继续扮演角色 {character_name}，进行回复，回复时请用""包裹说的话用（）包裹你的动作。")

    return "\n".join(prompt_parts)


# AI 回复生成 (支持多种 AI 服务)
# AI 回复生成 (支持多种 AI 服务)
def generate_ai_response(user_input, ai_provider, ai_settings, preset=None, character_file_content="",
                         first_message=True, character_name="", image_data=None):
    # 加载预设（如果提供）
    if preset is None or (isinstance(preset, str) and preset):
        preset = load_preset(preset)

    # 构建提示词
    prompt = build_prompt(user_input, preset, character_file_content, first_message, character_name)
    print(f"调试信息 - 最终 Prompt: {prompt}")

    # 根据所选 AI 提供商调用不同的 API
    try:
        if ai_provider == "gemini":
            return generate_with_gemini(prompt, ai_settings, preset, image_data)
        elif ai_provider == "openai":
            return generate_with_openai(prompt, ai_settings, preset, image_data)
        elif ai_provider == "claude":
            return generate_with_claude(prompt, ai_settings, preset, image_data)
        else:
            print(f"未知的 AI 提供商: {ai_provider}")
            return "AI 回复生成失败，未知的 AI 提供商。"
    except Exception as e:
        print(f"Error generating AI response with {ai_provider}: {e}")
        return f"AI 回复生成失败，请稍后再试。错误: {str(e)}"


# 使用 Google Gemini 生成回复
# 使用 Google Gemini 生成回复（添加图片支持）
def generate_with_gemini(prompt, ai_settings, preset=None, image_data=None):
    api_key = ai_settings.get("apiKey", "")
    model_name = ai_settings.get("model", "gemini-2.0-flash-lite-preview-02-05")
    temperature = float(ai_settings.get("temperature", 0.7))

    if not api_key:
        return "未设置 Gemini API Key，请在设置中配置。"

    genai.configure(api_key=api_key)

    try:
        # 检查是否支持图片输入的模型
        vision_models = ["gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-pro",
                         "gemini-2.0-pro-exp-02-05"]
        is_vision_model = any(vm in model_name for vm in vision_models)

        model = genai.GenerativeModel(model_name)

        # 使用预设温度（如果有）
        if preset and "temperature" in preset:
            temperature = float(preset.get("temperature", temperature))

        generation_config = {
            "temperature": temperature,
            "top_p": float(preset.get("top_p", 0.95)) if preset else 0.95,
            "top_k": int(preset.get("top_k", 40)) if preset else 40,
            "max_output_tokens": 2000
        }

        # 如果有图片且模型支持图片
        if image_data and is_vision_model:
            import base64
            from google.generativeai.types import Part

            # 将Base64图片数据转换为二进制
            if isinstance(image_data, str) and image_data.startswith("data:"):
                # 处理Data URL格式
                image_format = image_data.split(';')[0].split('/')[1]
                base64_data = image_data.split(',')[1]
                image_binary = base64.b64decode(base64_data)
            elif isinstance(image_data, str):
                # 直接是Base64字符串
                image_binary = base64.b64decode(image_data)
            else:
                # 已经是二进制数据
                image_binary = image_data

            # 创建多模态请求
            response = model.generate_content(
                [
                    Part.from_text(prompt),
                    Part.from_data(image_binary, mime_type="image/jpeg")
                ],
                generation_config=generation_config
            )
        else:
            response = model.generate_content(prompt, generation_config=generation_config)

        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"Gemini API 错误: {str(e)}"


# 使用 OpenAI GPT 生成回复（添加图片支持）
def generate_with_openai(prompt, ai_settings, preset=None, image_data=None):
    api_key = ai_settings.get("apiKey", "")
    model_name = ai_settings.get("model", "gpt-3.5-turbo")
    temperature = float(ai_settings.get("temperature", 0.7))

    if not api_key:
        return "未设置 OpenAI API Key，请在设置中配置。"

    client = openai.OpenAI(api_key=api_key)

    try:
        # 使用预设温度（如果有）
        if preset and "temperature" in preset:
            temperature = float(preset.get("temperature", temperature))

        # 检查是否为支持图片的模型
        vision_models = ["gpt-4-vision", "gpt-4o", "gpt-4-turbo"]
        is_vision_model = any(vm in model_name for vm in vision_models)

        if image_data and is_vision_model:
            # 处理图片输入
            import base64

            # 准备图片内容
            if isinstance(image_data, str) and image_data.startswith("data:"):
                # 已经是Data URL格式
                image_url = image_data
            elif isinstance(image_data, str):
                # 转换Base64为Data URL
                image_url = f"data:image/jpeg;base64,{image_data}"
            else:
                # 转换二进制为Base64 Data URL
                base64_data = base64.b64encode(image_data).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{base64_data}"

            # 创建多模态请求
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ]
        else:
            messages = [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=2000,
            top_p=float(preset.get("top_p", 0.95)) if preset else 0.95,
            presence_penalty=float(preset.get("presence_penalty", 0)) if preset else 0,
            frequency_penalty=float(preset.get("frequency_penalty", 0)) if preset else 0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return f"OpenAI API 错误: {str(e)}"


# 使用 Anthropic Claude 生成回复（添加图片支持）
def generate_with_claude(prompt, ai_settings, preset=None, image_data=None):
    api_key = ai_settings.get("apiKey", "")
    model_name = ai_settings.get("model", "claude-3-sonnet-20240229")
    temperature = float(ai_settings.get("temperature", 0.7))

    if not api_key:
        return "未设置 Claude API Key，请在设置中配置。"

    client = anthropic.Anthropic(api_key=api_key)

    try:
        # 使用预设温度（如果有）
        if preset and "temperature" in preset:
            temperature = float(preset.get("temperature", temperature))

        # Claude 3模型支持图片输入
        claude_vision_models = ["claude-3", "claude-3-5", "claude-3-7"]
        is_vision_model = any(vm in model_name for vm in claude_vision_models)

        if image_data and is_vision_model:
            # 处理图片输入
            import base64
            from anthropic.types import ImageBlockParam, MediaBlockParam

            # 准备图片内容
            if isinstance(image_data, str) and image_data.startswith("data:"):
                # 已经是Data URL格式，提取Base64部分
                base64_data = image_data.split(',')[1]
            elif isinstance(image_data, str):
                # 已经是Base64字符串
                base64_data = image_data
            else:
                # 转换二进制为Base64
                base64_data = base64.b64encode(image_data).decode('utf-8')

            # 创建多模态请求
            message = client.messages.create(
                model=model_name,
                max_tokens=2000,
                temperature=temperature,
                top_p=float(preset.get("top_p", 0.95)) if preset else 0.95,
                system="You are a helpful AI assistant that specializes in role-playing and character simulation.",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_data}}
                    ]
                }]
            )
        else:
            message = client.messages.create(
                model=model_name,
                max_tokens=2000,
                temperature=temperature,
                top_p=float(preset.get("top_p", 0.95)) if preset else 0.95,
                system="You are a helpful AI assistant that specializes in role-playing and character simulation.",
                messages=[{"role": "user", "content": prompt}]
            )
        return message.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return f"Claude API 错误: {str(e)}"


# 提取引号内的文本用于TTS
def extract_dialogue_for_tts(text):
    import re

    # 匹配引号内的文本 ("文本" 或 "文本")
    dialogue_parts = re.findall(r'[""]([^""]+)["""]', text)

    if dialogue_parts:
        # 连接所有对话部分，用适当的标点符号分隔
        combined_dialogue = "。".join(dialogue_parts)
        return combined_dialogue
    else:
        # 如果没有找到引号包裹的文本，返回原始文本（截断到300个字符）
        return text[:300]


# GPT-SoVITS 文本转语音
def text_to_speech_gptsovits(text, tts_settings=None, character_name=""):
    global _cached_ref_wav_path, _tts_available, _tts_url

    # 先检查TTS服务是否可用
    if not initialize_tts():
        return None

    # 默认设置
    tts_settings = tts_settings or {}
    speed = float(tts_settings.get("speed", 1.0))
    ref_audio = tts_settings.get("refAudio")

    try:
        client = Client(_tts_url)

        # 使用绝对路径 (更可靠)
        project_root = os.path.dirname(os.path.abspath(__file__))  # main.py 所在目录
        gpt_sovits_root = os.path.abspath(os.path.join(project_root, "GPT-SoVITS"))  # GPT-SoVITS 目录

        gpt_model_dir = os.path.join(gpt_sovits_root, "GPT_weights_v3")
        sovits_model_dir = os.path.join(gpt_sovits_root, "SoVITS_weights_v3")

        # 检查目录是否存在
        if not os.path.exists(gpt_model_dir) or not os.path.exists(sovits_model_dir):
            print(f"Error: GPT-SoVITS model directories not found")
            return None

        # 列出所有可用的模型文件
        gpt_models = [f for f in os.listdir(gpt_model_dir) if f.endswith(".ckpt")]
        sovits_models = [f for f in os.listdir(sovits_model_dir) if f.endswith(".pth")]

        if not gpt_models:
            print(f"Error: No GPT models (.ckpt) found in {gpt_model_dir}")
            return None
        if not sovits_models:
            print(f"Error: No SoVITS models (.pth) found in {sovits_model_dir}")
            return None

        # 选择模型（后续可以改为用户选择）
        gpt_model_path = os.path.join(gpt_model_dir, gpt_models[0])
        sovits_model_path = os.path.join(sovits_model_dir, sovits_models[0])

        print(f"Using GPT model: {gpt_model_path}")
        print(f"Using SoVITS model: {sovits_model_path}")

        # 1. 切换 SoVITS 模型
        client.predict(
            sovits_path=sovits_model_path,
            prompt_language="中文",
            text_language="中文",
            api_name="/change_sovits_weights"
        )

        # 2. 切换 GPT 模型
        client.predict(
            gpt_path=gpt_model_path,
            api_name="/change_gpt_weights"
        )

        # 3. 获取参考音频路径
        if ref_audio and "data" in ref_audio:
            # 从base64保存临时文件作为参考音频
            import base64
            import tempfile

            try:
                # 解析base64数据
                audio_data = ref_audio["data"].split(",")[1]
                decoded_data = base64.b64decode(audio_data)

                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(decoded_data)
                    ref_wav_path = temp_file.name
                    _cached_ref_wav_path = ref_wav_path

                print(f"使用上传的参考音频: {ref_wav_path}")
            except Exception as e:
                print(f"处理上传参考音频失败: {e}")
                ref_wav_path = get_default_ref_audio()
        else:
            ref_wav_path = get_default_ref_audio()

        # 提取对话文本用于TTS
        tts_text = extract_dialogue_for_tts(text)
        if not tts_text:
            print("没有找到适合TTS的对话文本")
            return None

        # 4. 生成 TTS
        result = client.predict(
            ref_wav_path=ref_wav_path,
            prompt_text="",
            prompt_language="中文",
            text=tts_text,
            text_language="中文",
            how_to_cut="按标点符号切",
            top_k=20,
            top_p=0.95,
            temperature=0.8,
            ref_free=False,
            speed=speed,
            if_freeze=False,
            inp_refs=None,
            sample_steps="8",
            api_name="/get_tts_wav"
        )
        print(f"GPT-SoVITS 生成音频成功：{result}")
        return result

    except Exception as e:
        print(f"Error calling GPT-SoVITS API: {e}")
        _tts_available = False  # 发生错误后标记TTS为不可用
        return None


# 获取默认参考音频
def get_default_ref_audio():
    global _cached_ref_wav_path

    if _cached_ref_wav_path and os.path.exists(_cached_ref_wav_path):
        return _cached_ref_wav_path

    # 自动搜索参考音频
    project_root = os.path.dirname(os.path.abspath(__file__))

    for filename in os.listdir(project_root):
        if filename.endswith(".wav"):
            _cached_ref_wav_path = os.path.join(project_root, filename)
            print(f"找到参考音频: {_cached_ref_wav_path}")
            return _cached_ref_wav_path

    print("未找到参考音频文件")
    return None


# 播放音频
def play_audio(file_path):
    try:
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
    except Exception as e:
        print(f"Error playing audio: {e}")


# 写入历史记录
def write_to_history(user_input, ai_response):
    history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.txt")
    try:
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(f"User: {user_input}\n")
            f.write(f"AI: {ai_response}\n")  # 写入完整的 AI 回复
            f.write("-" * 40 + "\n")
    except Exception as e:
        print(f"Error writing to history file: {e}")


# 处理语音输入、AI 回复、TTS 和播放
def process_speech(ai_provider, ai_settings, preset, tts_enabled, character_name, user_input, ai_response,
                   tts_settings=None):
    if user_input and ai_response:
        # 将 AI 回复写入历史记录
        write_to_history(user_input, ai_response)

        # 检查是否启用TTS
        if tts_enabled:
            # 使用 GPT-SoVITS 生成语音
            print("正在生成语音...")
            audio_file = text_to_speech_gptsovits(ai_response, tts_settings, character_name)
            if audio_file:
                play_audio(audio_file)
                return {"success": True, "response": ai_response, "tts_played": True}
            else:
                print("TTS生成失败")
                return {"success": True, "response": ai_response, "tts_played": False}
        else:
            print("TTS功能未启用")
            return {"success": True, "response": ai_response, "tts_played": False}
    else:
        print("没有AI响应或用户输入")
        return {"success": False, "error": "No input or response", "tts_played": False}


# 检查TTS服务可用性
def check_tts_availability(url=None):
    global _tts_url, _tts_available, _tts_retry_count

    # 如果提供了URL，更新默认URL
    if url:
        _tts_url = url

    # 重置重试计数
    _tts_retry_count = 0

    # 尝试连接
    return initialize_tts()