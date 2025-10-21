#!/usr/bin/env python3
"""
Setup script for Discord Video Downloader Bot
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 أو أحدث مطلوب")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} متوفر")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✅ FFmpeg متوفر")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg غير متوفر - سيتم تثبيته تلقائياً")
        return False

def install_requirements():
    """Install Python requirements"""
    try:
        print("📦 تثبيت المتطلبات...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ تم تثبيت المتطلبات بنجاح")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المتطلبات")
        return False

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ تم إنشاء ملف .env")
            print("⚠️  يرجى تحديث DISCORD_BOT_TOKEN في ملف .env")
        else:
            with open('.env', 'w') as f:
                f.write('DISCORD_BOT_TOKEN=your_bot_token_here\n')
            print("✅ تم إنشاء ملف .env")
            print("⚠️  يرجى إضافة توكن البوت في ملف .env")
    else:
        print("✅ ملف .env موجود")

def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'downloads', 'temp']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ تم إنشاء مجلد {dir_name}")

def main():
    """Main setup function"""
    print("🚀 إعداد بوت تحميل الفيديوهات")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 40)
    print("✅ تم الإعداد بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("1. احصل على توكن البوت من Discord Developer Portal")
    print("2. أضف التوكن في ملف .env")
    print("3. شغل البوت: python bot.py")
    print("\n🌐 للنشر على الإنترنت:")
    print("- Railway: railway login && railway deploy")
    print("- Heroku: git push heroku main")
    print("- Docker: docker-compose up -d")
    
    return True

if __name__ == "__main__":
    main()
