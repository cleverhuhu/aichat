from flask import Flask, request, jsonify
import os
import json
import uuid
import shutil
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 设置文件和目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "user_settings.json")
HISTORY_DIR = os.path.join(BASE_DIR, "history")
CHARACTERS_DIR = os.path.join(BASE_DIR, "..", "char")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")

# 确保必要的目录存在
for directory in [HISTORY_DIR, CHARACTERS_DIR, PRESETS_DIR]:
    os.makedirs(directory, exist_ok=True)


# 健康检查路由
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


# 路由：获取设置
@app.route('/get_settings', methods=['GET'])
def get_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return jsonify({"success": True, "settings": settings})
        else:
            # 如果设置文件不存在，返回一个空的成功响应
            return jsonify({"success": True, "settings": {}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：保存设置
@app.route('/save_settings', methods=['POST'])
def save_settings():
    try:
        settings = request.json

        # 确保settings是一个字典
        if not isinstance(settings, dict):
            return jsonify({"success": False, "error": "Settings must be a JSON object"})

        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：列出角色文件
@app.route('/list_characters', methods=['GET'])
def list_characters():
    try:
        characters = [f for f in os.listdir(CHARACTERS_DIR) if f.endswith('.txt')]
        return jsonify({"success": True, "characters": characters})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：创建角色
@app.route('/create_character', methods=['POST'])
def create_character():
    try:
        data = request.json
        name = data.get('name', '').strip()
        description = data.get('description', '')
        file_name = data.get('file_name', f"{name}.txt")

        if not name:
            return jsonify({"success": False, "error": "Character name is required"})

        # 确保文件名以.txt结尾
        if not file_name.endswith('.txt'):
            file_name += '.txt'

        file_path = os.path.join(CHARACTERS_DIR, file_name)

        # 写入角色文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(description)

        return jsonify({"success": True, "file_name": file_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：获取角色内容
@app.route('/get_character/<character_file>', methods=['GET'])
def get_character(character_file):
    try:
        file_path = os.path.join(CHARACTERS_DIR, character_file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return jsonify({"success": True, "content": content})
        else:
            return jsonify({"success": False, "error": "Character file not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：更新角色内容
@app.route('/update_character', methods=['POST'])
def update_character():
    try:
        data = request.json
        file_name = data.get('file_name')
        content = data.get('content', '')

        if not file_name:
            return jsonify({"success": False, "error": "Character file name is required"})

        file_path = os.path.join(CHARACTERS_DIR, file_name)

        # 写入角色文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：删除角色
@app.route('/delete_character/<character_file>', methods=['DELETE'])
def delete_character(character_file):
    try:
        file_path = os.path.join(CHARACTERS_DIR, character_file)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Character file not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：列出预设配置
@app.route('/list_presets', methods=['GET'])
def list_presets():
    try:
        # 添加默认预设文件
        default_preset = "_BoxBear_Gemini_Novel_V1.1_Release (1).json"
        source_path = os.path.join(BASE_DIR, default_preset)
        target_path = os.path.join(PRESETS_DIR, default_preset)

        # 复制默认预设到预设目录（如果不存在）
        if os.path.exists(source_path) and not os.path.exists(target_path):
            shutil.copy2(source_path, target_path)

        presets = [f for f in os.listdir(PRESETS_DIR) if f.endswith('.json')]
        return jsonify({"success": True, "presets": presets})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：获取预设内容
@app.route('/get_preset/<preset_name>', methods=['GET'])
def get_preset(preset_name):
    try:
        # 先尝试在预设目录中查找
        preset_path = os.path.join(PRESETS_DIR, preset_name)

        # 如果在预设目录中找不到，则尝试直接在后端目录中查找（用于默认预设）
        if not os.path.exists(preset_path):
            preset_path = os.path.join(BASE_DIR, preset_name)

        if os.path.exists(preset_path):
            with open(preset_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
                return jsonify({"success": True, "preset": preset_data})
        else:
            return jsonify({"success": False, "error": "Preset not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：保存预设
@app.route('/save_preset', methods=['POST'])
def save_preset():
    try:
        preset_data = request.json
        preset_name = preset_data.get('name', f"preset_{uuid.uuid4().hex[:8]}")

        # 确保文件名以.json结尾
        if not preset_name.endswith('.json'):
            preset_name += '.json'

        preset_path = os.path.join(PRESETS_DIR, preset_name)

        with open(preset_path, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "preset_name": preset_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：删除预设
@app.route('/delete_preset/<preset_name>', methods=['DELETE'])
def delete_preset(preset_name):
    try:
        preset_path = os.path.join(PRESETS_DIR, preset_name)
        if os.path.exists(preset_path):
            os.remove(preset_path)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Preset not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：列出历史记录
@app.route('/list_history', methods=['GET'])
def list_history():
    try:
        history_files = []
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(HISTORY_DIR, filename)
                stat = os.stat(file_path)

                # 提取ID和名称
                file_id = filename.split('.')[0]

                # 尝试加载历史记录获取角色信息
                character = ""
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                        if 'character' in history_data:
                            character = history_data['character'].split('.')[0]
                except:
                    pass

                history_files.append({
                    "id": file_id,
                    "name": filename,
                    "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "character": character
                })

        # 按日期排序，最新的在前
        history_files.sort(key=lambda x: x['date'], reverse=True)
        return jsonify({"success": True, "history": history_files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：获取历史记录内容
@app.route('/get_history/<history_id>', methods=['GET'])
def get_history(history_id):
    try:
        for filename in os.listdir(HISTORY_DIR):
            if filename.startswith(history_id):
                file_path = os.path.join(HISTORY_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    return jsonify({"success": True, "history": history_data})
        return jsonify({"success": False, "error": "History not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 路由：删除历史记录
@app.route('/delete_history/<history_id>', methods=['DELETE'])
def delete_history(history_id):
    try:
        for filename in os.listdir(HISTORY_DIR):
            if filename.startswith(history_id):
                file_path = os.path.join(HISTORY_DIR, filename)
                os.remove(file_path)
                return jsonify({"success": True})
        return jsonify({"success": False, "error": "History not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 聊天AI路由
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 从请求中获取数据
        data = request.json
        user_message = data.get('message', '')
        character_file = data.get('character', '')
        first_message = data.get('first_message', True)
        chat_id = data.get('current_chat_id')
        ai_provider = data.get('ai_provider', 'gemini')
        ai_settings = data.get('ai_settings', {})
        tts_enabled = data.get('tts_enabled', False)
        tts_settings = data.get('tts_settings', {})
        preset_name = data.get('preset', None)

        # 加载角色文件内容
        character_content = ""
        character_name = character_file.split('.')[0] if character_file else "AI助手"

        if character_file:
            character_path = os.path.join(CHARACTERS_DIR, character_file)
            if os.path.exists(character_path):
                with open(character_path, 'r', encoding='utf-8') as f:
                    character_content = f.read()

        # 导入main.py中的函数
        import sys
        sys.path.append(os.path.join(BASE_DIR, '..'))
        from main import generate_ai_response, process_speech

        # 加载预设（如果有）
        preset = preset_name

        # 生成AI回复
        ai_response = generate_ai_response(
            user_message,
            ai_provider,
            ai_settings,
            preset,
            character_content,
            first_message,
            character_name
        )

        # 处理TTS（如果启用）
        tts_result = {"tts_played": False}
        if tts_enabled and ai_response:
            tts_result = process_speech(
                ai_provider,
                ai_settings,
                preset,
                tts_enabled,
                character_name,
                user_message,
                ai_response,
                tts_settings
            )

        # 创建或更新聊天历史
        if not chat_id:
            # 创建新的聊天历史
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            chat_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"
            history_filename = f"{chat_id}.json"
            history_data = {
                "character": character_file,
                "created_at": datetime.now().isoformat(),
                "messages": [
                    {"text": user_message, "type": "user", "timestamp": datetime.now().isoformat()},
                    {"text": ai_response, "type": "ai", "timestamp": datetime.now().isoformat(),
                     "tts_played": tts_result.get("tts_played", False)}
                ],
                "preset": preset_name
            }
        else:
            # 更新现有的聊天历史
            history_filename = f"{chat_id}.json"
            history_path = os.path.join(HISTORY_DIR, history_filename)

            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            else:
                history_data = {
                    "character": character_file,
                    "created_at": datetime.now().isoformat(),
                    "messages": [],
                    "preset": preset_name
                }

            # 添加新消息
            history_data["messages"].append({
                "text": user_message,
                "type": "user",
                "timestamp": datetime.now().isoformat()
            })
            history_data["messages"].append({
                "text": ai_response,
                "type": "ai",
                "timestamp": datetime.now().isoformat(),
                "tts_played": tts_result.get("tts_played", False)
            })

        # 保存历史记录
        history_path = os.path.join(HISTORY_DIR, history_filename)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "response": ai_response,
            "chat_id": chat_id,
            "tts_played": tts_result.get("tts_played", False)
        })

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')