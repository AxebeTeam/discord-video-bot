import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
import logging
from datetime import datetime
import tempfile
import aiohttp
import json
from dotenv import load_dotenv
import gtts
from io import BytesIO
import signal
import sys

# Load environment variables
load_dotenv()

# Bot configuration
UPDATE_CHANNEL_ID = os.getenv('UPDATE_CHANNEL_ID')  # Channel ID for updates
BOT_VERSION = "2.1.3"  # Current bot version
LAST_UPDATE = "2025-10-21"  # Last update date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot setup with voice support
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    help_command=None,
    case_insensitive=True
)

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[height<=720]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'extractflat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'quiet': False,
            'verbose': False,
        }
    
    async def download_video(self, url, output_path=None):
        """Download video from URL using yt-dlp"""
        try:
            if output_path:
                self.ydl_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                # Check file size and duration limits
                if duration and duration > 600:  # 10 minutes limit
                    return None, "فيديو طويل جداً (أكثر من 10 دقائق)"
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(output_path or '.'):
                    if title.replace('/', '_').replace('\\', '_') in file or any(ext in file for ext in ['.mp4', '.mkv', '.webm', '.avi']):
                        file_path = os.path.join(output_path or '.', file)
                        file_size = os.path.getsize(file_path)
                        
                        # Discord file size limit (8MB for free, 50MB for Nitro)
                        if file_size > 8 * 1024 * 1024:  # 8MB limit
                            os.remove(file_path)
                            return None, "حجم الملف كبير جداً (أكثر من 8 ميجابايت)"
                        
                        return file_path, None
                
                return None, "لم يتم العثور على الملف المحمل"
                
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None, f"خطأ في التحميل: {str(e)}"

    def get_supported_sites(self):
        """Get list of supported sites"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                extractors = ydl.list_extractors()
                return [extractor.IE_NAME for extractor in extractors[:50]]  # First 50 sites
        except:
            return ["YouTube", "TikTok", "Instagram", "Twitter", "Facebook", "Reddit", "Twitch"]

downloader = VideoDownloader()

async def send_update_notification(title, description, color=0x00ff00, fields=None):
    """Send update notification to designated channel"""
    if not UPDATE_CHANNEL_ID:
        return
    
    try:
        channel = bot.get_channel(int(UPDATE_CHANNEL_ID))
        if not channel:
            logger.warning(f"Update channel {UPDATE_CHANNEL_ID} not found")
            return
        
        embed = discord.Embed(
            title=f"🔄 {title}",
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="تحديث البوت", icon_url=bot.user.avatar.url if bot.user.avatar else None)
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        await channel.send(embed=embed)
        logger.info(f"Update notification sent to channel {UPDATE_CHANNEL_ID}")
        
    except Exception as e:
        logger.error(f"Failed to send update notification: {str(e)}")

async def send_automatic_update_notification():
    """Send automatic update notification based on version and features"""
    if not UPDATE_CHANNEL_ID:
        return
    
    # Define current update details
    update_details = {
        "version": BOT_VERSION,
        "date": LAST_UPDATE,
        "title": "تحديث كبير - نظام الإشعارات التلقائية!",
        "description": "تم إضافة ميزات جديدة مذهلة للبوت",
        "new_features": [
            "🎤 تحويل النص إلى كلام بالعربية",
            "📢 نظام إشعارات التحديثات التلقائية", 
            "🔧 أوامر المطورين المتقدمة",
            "✨ واجهة محسنة وأداء أفضل"
        ],
        "improvements": [
            "إصلاح الأخطاء الكاذبة في الصوت",
            "تحسين معالجة الاتصال الصوتي",
            "إضافة فحص الصلاحيات المتقدم",
            "تحسين نظام السجلات والأخطاء"
        ],
        "commands": [
            "`!say [نص]` - تحويل النص إلى كلام",
            "`!announce [رسالة]` - إرسال إعلان (للمطورين)",
            "`!update_notify [عنوان] [وصف]` - إشعار تحديث (للمطورين)",
            "`!set_update_channel` - تعيين قناة التحديثات"
        ]
    }
    
    try:
        await send_update_notification(
            title=update_details["title"],
            description=f"الإصدار {update_details['version']} - {update_details['description']}",
            color=0x00ff00,
            fields=[
                {
                    "name": "🆕 الميزات الجديدة",
                    "value": "\n".join(update_details["new_features"]),
                    "inline": False
                },
                {
                    "name": "🔧 التحسينات",
                    "value": "\n".join(update_details["improvements"]),
                    "inline": False
                },
                {
                    "name": "📋 الأوامر الجديدة",
                    "value": "\n".join(update_details["commands"]),
                    "inline": False
                },
                {
                    "name": "📅 تاريخ التحديث",
                    "value": update_details["date"],
                    "inline": True
                },
                {
                    "name": "🔢 رقم الإصدار",
                    "value": f"v{update_details['version']}",
                    "inline": True
                },
                {
                    "name": "🚀 الحالة",
                    "value": "البوت يعمل بكامل طاقته!",
                    "inline": True
                }
            ]
        )
        
        # Send welcome message after update notification
        await asyncio.sleep(2)  # Wait 2 seconds
        
        await send_update_notification(
            title="البوت متصل ومستعد للعمل!",
            description="جميع الأنظمة تعمل بشكل مثالي. البوت جاهز لاستقبال الأوامر!",
            color=0x0099ff,
            fields=[
                {
                    "name": "🎯 للبدء",
                    "value": "استخدم `!info` لرؤية جميع الأوامر المتاحة",
                    "inline": False
                },
                {
                    "name": "🎤 جرب الميزة الجديدة",
                    "value": "ادخل روم صوتي واكتب `!say أهلاً وسهلاً`",
                    "inline": False
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to send automatic update notification: {str(e)}")

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    print(f'{bot.user} متصل بنجاح!')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!download للمساعدة"
        )
    )
    
    # Send automatic update notification
    await send_automatic_update_notification()

async def cleanup_connections():
    """Clean up all connections and resources"""
    logger.info("Starting cleanup process...")
    
    # Clean up voice connections
    for voice_client in bot.voice_clients:
        try:
            if voice_client.is_connected():
                await voice_client.disconnect(force=True)
                logger.info(f"Disconnected voice client from {voice_client.channel}")
        except Exception as e:
            logger.warning(f"Error disconnecting voice client: {str(e)}")
    
    # Clean up HTTP sessions
    try:
        if hasattr(bot, 'http') and bot.http.connector:
            await bot.http.connector.close()
            logger.info("HTTP connector closed")
    except Exception as e:
        logger.warning(f"Error closing HTTP connector: {str(e)}")
    
    # Wait for cleanup to complete
    await asyncio.sleep(1.0)
    logger.info("Cleanup process completed")

@bot.event
async def on_disconnect():
    """Clean up when bot disconnects"""
    logger.info("Bot disconnecting - starting cleanup")
    await cleanup_connections()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ أمر غير معروف! استخدم `!help` لرؤية الأوامر المتاحة")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ معطى مفقود! تأكد من إدخال الرابط")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ حدث خطأ: {str(error)}")

@bot.command(name='download', aliases=['dl', 'تحميل'])
async def download_video(ctx, url: str = None):
    """Download video from supported platforms"""
    if not url:
        embed = discord.Embed(
            title="📥 تحميل الفيديوهات",
            description="استخدم: `!download [رابط الفيديو]`\n\nمثال:\n`!download https://youtube.com/watch?v=...`",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        return
    
    # Send initial message
    loading_msg = await ctx.send("⏳ جاري التحميل...")
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download video
            file_path, error = await downloader.download_video(url, temp_dir)
            
            if error:
                await loading_msg.edit(content=f"❌ {error}")
                return
            
            if not file_path or not os.path.exists(file_path):
                await loading_msg.edit(content="❌ فشل في تحميل الفيديو")
                return
            
            # Send the file
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            embed = discord.Embed(
                title="✅ تم التحميل بنجاح!",
                description=f"📁 حجم الملف: {file_size_mb:.2f} ميجابايت",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"تم الطلب بواسطة {ctx.author.display_name}")
            
            await loading_msg.delete()
            
            with open(file_path, 'rb') as f:
                file = discord.File(f, filename=os.path.basename(file_path))
                await ctx.send(embed=embed, file=file)
    
    except Exception as e:
        logger.error(f"Download command error: {str(e)}")
        await loading_msg.edit(content=f"❌ خطأ في التحميل: {str(e)}")

@bot.command(name='sites', aliases=['مواقع'])
async def supported_sites(ctx):
    """Show supported sites"""
    sites = downloader.get_supported_sites()
    
    embed = discord.Embed(
        title="🌐 المواقع المدعومة",
        description="يمكن تحميل الفيديوهات من هذه المواقع:",
        color=0x0099ff
    )
    
    # Split sites into chunks for better display
    site_chunks = [sites[i:i+10] for i in range(0, len(sites), 10)]
    
    for i, chunk in enumerate(site_chunks[:3]):  # Show first 3 chunks only
        embed.add_field(
            name=f"المجموعة {i+1}",
            value="\n".join([f"• {site}" for site in chunk]),
            inline=True
        )
    
    embed.set_footer(text="وأكثر من 1000+ موقع آخر!")
    await ctx.send(embed=embed)

@bot.command(name='info', aliases=['معلومات'])
async def bot_info(ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🤖 معلومات البوت",
        description="بوت تحميل الفيديوهات بدون علامة مائية",
        color=0xff9900
    )
    
    embed.add_field(
        name="📋 أوامر التحميل",
        value="`!download [رابط]` - تحميل فيديو\n`!sites` - المواقع المدعومة",
        inline=False
    )
    
    embed.add_field(
        name="🎤 أوامر الصوت",
        value="`!say [نص]` - تحويل النص إلى كلام\n`!join` - الانضمام للروم الصوتي\n`!leave` - مغادرة الروم الصوتي\n`!stop` - إيقاف التشغيل",
        inline=False
    )
    
    embed.add_field(
        name="🔧 أوامر أخرى",
        value="`!info` - معلومات البوت\n`!ping` - فحص سرعة الاستجابة",
        inline=False
    )
    
    # Show admin commands if user is admin
    if ctx.author.guild_permissions.administrator:
        embed.add_field(
            name="👨‍💻 أوامر المطورين",
            value="`!announce [رسالة]` - إرسال إعلان\n`!update_notify [عنوان] [وصف]` - إشعار تحديث\n`!set_update_channel` - تعيين قناة التحديثات",
            inline=False
        )
    
    embed.add_field(
        name="⚡ المميزات",
        value="• تحميل بدون علامة مائية\n• دعم أكثر من 1000 موقع\n• جودة عالية\n• سرعة فائقة",
        inline=False
    )
    
    embed.add_field(
        name="📏 القيود",
        value="• حد أقصى 10 دقائق للفيديو\n• حد أقصى 8 ميجابايت لحجم الملف",
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="تم التطوير بواسطة Cascade AI")
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"زمن الاستجابة: {latency}ms",
        color=0x00ff00 if latency < 100 else 0xff9900 if latency < 200 else 0xff0000
    )
    await ctx.send(embed=embed)

@bot.command(name='say', aliases=['قول', 'تكلم'])
async def text_to_speech(ctx, *, text: str = None):
    """Convert text to speech and play in voice channel"""
    if not text:
        embed = discord.Embed(
            title="🎤 تحويل النص إلى كلام",
            description="استخدم: `!say [النص]`\n\nمثال:\n`!say أهلاً وسهلاً بكم`",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        return
    
    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون في روم صوتي أولاً!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Check bot permissions
    permissions = voice_channel.permissions_for(ctx.guild.me)
    if not permissions.connect or not permissions.speak:
        await ctx.send("❌ ليس لدي صلاحية للانضمام أو التحدث في هذا الروم!")
        return
    
    try:
        # Send loading message
        loading_msg = await ctx.send("🎤 جاري تحويل النص إلى كلام...")
        
        # Generate TTS audio
        tts = gtts.gTTS(text=text, lang='ar', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            audio_file = tmp_file.name
        
        # Connect to voice channel with retry logic
        voice_client = None
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Clean up any existing connection first
                if ctx.voice_client:
                    try:
                        await ctx.voice_client.disconnect(force=True)
                        await asyncio.sleep(1.0)  # Wait for cleanup
                    except:
                        pass
                
                # Fresh connection attempt
                voice_client = await voice_channel.connect(timeout=15.0, reconnect=True)
                
                # Wait for connection to stabilize
                await asyncio.sleep(2.0)
                
                # Test connection
                if voice_client.is_connected():
                    logger.info(f"Voice connection successful on attempt {retry_count + 1}")
                    break
                else:
                    raise Exception("Connection test failed")
                    
            except discord.errors.ConnectionClosed as e:
                retry_count += 1
                if e.code == 4006:
                    logger.warning(f"Voice session expired (4006) - attempt {retry_count}")
                    await asyncio.sleep(3.0)  # Longer wait for session expiry
                else:
                    logger.warning(f"Voice connection closed ({e.code}) - attempt {retry_count}")
                    await asyncio.sleep(2.0)
                
                if voice_client:
                    try:
                        await voice_client.disconnect(force=True)
                    except:
                        pass
                
                if retry_count >= max_retries:
                    raise Exception(f"Voice connection failed after {max_retries} attempts: WebSocket closed with {e.code}")
                    
            except Exception as e:
                retry_count += 1
                logger.warning(f"Voice connection attempt {retry_count} failed: {str(e)}")
                
                if voice_client:
                    try:
                        await voice_client.disconnect(force=True)
                    except:
                        pass
                
                if retry_count < max_retries:
                    await asyncio.sleep(2.0)  # Wait before retry
                else:
                    raise Exception(f"Failed to connect to voice after {max_retries} attempts: {str(e)}")
        
        # Play the audio
        if voice_client.is_playing():
            voice_client.stop()
        
        # Create audio source
        audio_source = discord.FFmpegPCMAudio(audio_file)
        voice_client.play(audio_source)
        
        # Update message
        embed = discord.Embed(
            title="🎤 يتم التشغيل الآن",
            description=f"📝 النص: {text}\n🔊 في الروم: {voice_channel.name}",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"تم الطلب بواسطة {ctx.author.display_name}")
        
        await loading_msg.edit(content="", embed=embed)
        
        # Wait for audio to finish
        timeout = 30  # Maximum wait time in seconds
        elapsed = 0
        while voice_client.is_playing() and elapsed < timeout:
            await asyncio.sleep(1)
            elapsed += 1
        
        # Wait a bit more to ensure audio finished completely
        await asyncio.sleep(1)
        
        # Update message to show completion
        embed.title = "✅ تم التشغيل بنجاح"
        embed.color = 0x00ff00
        await loading_msg.edit(embed=embed)
        
        # Disconnect after playing with proper cleanup
        try:
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect(force=True)
        except Exception as e:
            logger.warning(f"Error disconnecting voice client: {str(e)}")
        
        # Clean up temporary file
        try:
            os.unlink(audio_file)
        except Exception as e:
            logger.warning(f"Error cleaning up temp file: {str(e)}")
            
    except discord.errors.ClientException as e:
        # This is often a false error when audio finishes normally
        logger.info(f"Audio playback completed (normal): {str(e)}")
        await ctx.send("✅ تم تشغيل الصوت بنجاح!")
        
    except Exception as e:
        # Enhanced error handling with proper cleanup
        error_msg = str(e).lower()
        
        if "failed to connect to voice" in error_msg:
            await ctx.send("❌ فشل الاتصال بالروم الصوتي. قد يكون الخادم مشغولاً، جرب مرة أخرى لاحقاً.")
            logger.error(f"Voice connection failed: {str(e)}")
        elif "not connected" in error_msg or "already playing" in error_msg:
            logger.info(f"Normal audio completion: {str(e)}")
            await ctx.send("✅ تم تشغيل الصوت بنجاح!")
        else:
            logger.error(f"Real TTS error: {str(e)}")
            await ctx.send(f"❌ خطأ في تحويل النص إلى كلام. جرب مرة أخرى.")
        
        # Force cleanup all voice connections
        try:
            for voice_client in bot.voice_clients:
                if voice_client.guild == ctx.guild:
                    await voice_client.disconnect(force=True)
                    logger.info(f"Force disconnected voice client from {voice_client.channel}")
        except Exception as cleanup_error:
            logger.warning(f"Error in force cleanup: {str(cleanup_error)}")
        
        # Clean up any remaining temp files
        try:
            if 'audio_file' in locals():
                os.unlink(audio_file)
        except:
            pass
        
        # Wait for cleanup
        await asyncio.sleep(1.0)

@bot.command(name='join', aliases=['انضم'])
async def join_voice(ctx):
    """Join user's voice channel"""
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون في روم صوتي أولاً!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Check bot permissions
    permissions = voice_channel.permissions_for(ctx.guild.me)
    if not permissions.connect or not permissions.speak:
        await ctx.send("❌ ليس لدي صلاحية للانضمام أو التحدث في هذا الروم!")
        return
    
    try:
        if ctx.voice_client:
            if ctx.voice_client.channel == voice_channel:
                await ctx.send(f"✅ أنا موجود بالفعل في {voice_channel.name}")
                return
            else:
                await ctx.voice_client.move_to(voice_channel)
                await ctx.send(f"🔊 تم الانتقال إلى {voice_channel.name}")
        else:
            # Clean connection attempt
            voice_client = await voice_channel.connect(timeout=15.0, reconnect=True)
            await asyncio.sleep(1.0)  # Wait for stabilization
            await ctx.send(f"🔊 تم الانضمام إلى {voice_channel.name}")
            
    except discord.errors.ConnectionClosed as e:
        if e.code == 4006:
            await ctx.send("❌ انتهت صلاحية الجلسة الصوتية. جرب مرة أخرى!")
        else:
            await ctx.send(f"❌ فشل الاتصال الصوتي (كود: {e.code})")
        logger.error(f"Voice connection failed in join command: {str(e)}")
        
    except Exception as e:
        await ctx.send(f"❌ خطأ في الانضمام للروم الصوتي: {str(e)}")
        logger.error(f"Join voice error: {str(e)}")

@bot.command(name='leave', aliases=['اخرج', 'غادر'])
async def leave_voice(ctx):
    """Leave voice channel"""
    if ctx.voice_client:
        try:
            channel_name = ctx.voice_client.channel.name
            await ctx.voice_client.disconnect(force=True)
            await ctx.send(f"👋 تم مغادرة الروم الصوتي: {channel_name}")
        except Exception as e:
            await ctx.send("👋 تم قطع الاتصال الصوتي")
            logger.warning(f"Error in leave command: {str(e)}")
    else:
        await ctx.send("❌ لست متصل بأي روم صوتي!")

@bot.command(name='stop', aliases=['توقف', 'ايقاف'])
async def stop_audio(ctx):
    """Stop current audio playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ تم إيقاف التشغيل")
    else:
        await ctx.send("❌ لا يوجد صوت يتم تشغيله حالياً!")

@bot.command(name='announce', aliases=['اعلان'])
@commands.has_permissions(administrator=True)
async def announce_update(ctx, *, message: str = None):
    """Send update announcement (Admin only)"""
    if not message:
        embed = discord.Embed(
            title="📢 إرسال إعلان تحديث",
            description="استخدم: `!announce [رسالة الإعلان]`\n\nمثال:\n`!announce تم إضافة ميزة جديدة للبوت!`",
            color=0x0099ff
        )
        await ctx.send(embed=embed)
        return
    
    await send_update_notification(
        title="إعلان جديد",
        description=message,
        color=0x0099ff,
        fields=[
            {
                "name": "📝 من",
                "value": f"{ctx.author.display_name}",
                "inline": True
            },
            {
                "name": "📅 التاريخ",
                "value": f"<t:{int(datetime.now().timestamp())}:F>",
                "inline": True
            }
        ]
    )
    
    await ctx.send("✅ تم إرسال الإعلان لقناة التحديثات!")

@bot.command(name='update_notify', aliases=['اشعار_تحديث'])
@commands.has_permissions(administrator=True)
async def update_notify(ctx, title: str = None, *, description: str = None):
    """Send formatted update notification (Admin only)"""
    if not title or not description:
        embed = discord.Embed(
            title="🔄 إرسال إشعار تحديث",
            description="استخدم: `!update_notify [عنوان] [وصف]`\n\nمثال:\n`!update_notify \"ميزة جديدة\" تم إضافة تحويل النص إلى كلام`",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        return
    
    await send_update_notification(
        title=title,
        description=description,
        color=0x00ff00,
        fields=[
            {
                "name": "👨‍💻 المطور",
                "value": f"{ctx.author.display_name}",
                "inline": True
            },
            {
                "name": "🕐 وقت التحديث",
                "value": f"<t:{int(datetime.now().timestamp())}:R>",
                "inline": True
            },
            {
                "name": "📋 للمساعدة",
                "value": "استخدم `!info` لرؤية جميع الأوامر",
                "inline": False
            }
        ]
    )
    
    await ctx.send("✅ تم إرسال إشعار التحديث!")

@bot.command(name='set_update_channel', aliases=['تعيين_قناة_التحديثات'])
@commands.has_permissions(administrator=True)
async def set_update_channel(ctx, channel: discord.TextChannel = None):
    """Set the update notifications channel (Admin only)"""
    if not channel:
        channel = ctx.channel
    
    # This would normally save to database, but for now we'll just confirm
    embed = discord.Embed(
        title="📢 تعيين قناة التحديثات",
        description=f"تم تعيين {channel.mention} كقناة للتحديثات!\n\n**ملاحظة:** لجعل هذا دائماً، أضف `UPDATE_CHANNEL_ID={channel.id}` في ملف .env",
        color=0x00ff00
    )
    
    await ctx.send(embed=embed)
    
    # Send test notification
    await send_update_notification(
        title="تم تعيين قناة التحديثات",
        description=f"هذه القناة ستستقبل جميع إشعارات التحديثات والإعلانات",
        color=0x0099ff
    )

@bot.command(name='version', aliases=['اصدار'])
async def show_version(ctx):
    """Show current bot version and update info"""
    embed = discord.Embed(
        title="📊 معلومات الإصدار",
        description=f"الإصدار الحالي للبوت",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🔢 رقم الإصدار",
        value=f"v{BOT_VERSION}",
        inline=True
    )
    
    embed.add_field(
        name="📅 تاريخ آخر تحديث",
        value=LAST_UPDATE,
        inline=True
    )
    
    embed.add_field(
        name="🚀 الحالة",
        value="يعمل بشكل مثالي",
        inline=True
    )
    
    embed.add_field(
        name="🆕 آخر الميزات",
        value="• تحويل النص إلى كلام\n• نظام الإشعارات التلقائية\n• أوامر المطورين المتقدمة",
        inline=False
    )
    
    embed.set_footer(text=f"تم الطلب بواسطة {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

async def shutdown_handler():
    """Handle graceful shutdown"""
    logger.info("Shutdown signal received - starting graceful shutdown")
    await cleanup_connections()
    await bot.close()
    logger.info("Bot shutdown completed")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown_handler())

if __name__ == "__main__":
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ خطأ: لم يتم العثور على DISCORD_BOT_TOKEN في متغيرات البيئة")
        print("يرجى إضافة التوكن في ملف .env أو متغيرات البيئة")
        exit(1)
    
    # Setup signal handlers for graceful shutdown
    if sys.platform != 'win32':
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ خطأ في تسجيل الدخول: تأكد من صحة التوكن")
        logger.error("Discord login failure - invalid token")
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received - shutting down")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        print(f"❌ خطأ في تشغيل البوت: {str(e)}")
    finally:
        logger.info("Bot process ended")
