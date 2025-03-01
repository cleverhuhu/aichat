# sr.py
import speech_recognition as sr

def speech_to_text(audio_file_path=None):
    """
    将语音转换为文字。
    如果 audio_file_path 为 None，则从麦克风实时捕获语音。
    """
    recognizer = sr.Recognizer()

    if audio_file_path:
        # 从音频文件中读取
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
    else:
        # 从麦克风实时捕获
        microphone = sr.Microphone()
        with microphone as source:
            print("请说话...")
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source)

    try:
        # 使用 Google Web Speech API 进行语音识别
        text = recognizer.recognize_google(audio_data, language="zh-CN")
        print("识别结果: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API 无法识别音频")
        return None
    except sr.RequestError as e:
        print(f"无法从Google Web Speech API获取结果; {e}")
        return None