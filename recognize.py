#!/home/linuxbrew/.linuxbrew/bin/python3.14
# -*- coding: utf-8 -*-
"""
语音识别脚本
用法：python3 recognize.py <语音文件路径>
"""

import speech_recognition as sr
import sys
import os

def recognize(audio_path):
    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在：{audio_path}")
        return None
    
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        print('✅ 音频加载成功')
        
        # 尝试多种识别方式
        # 1. Google（需要科学上网）
        try:
            text = r.recognize_google(audio, language='zh-CN')
            return f"📝 Google 识别：{text}"
        except:
            pass
        
        # 2. 百度（需要 API 密钥）
        # 配置方法：在 ~/.openclaw/voice-api-key 中存储密钥
        
        return "❌ 需要配置 API 密钥才能继续识别"
        
    except Exception as e:
        return f"❌ 错误：{e}"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 recognize.py <语音文件路径>")
        sys.exit(1)
    
    result = recognize(sys.argv[1])
    print(result)
