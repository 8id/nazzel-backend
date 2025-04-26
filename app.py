from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS # <-- الخطوة 2: استيراد CORS
import yt_dlp as youtube_dl
import os
import logging
import shutil
import validators
import secrets
import string
import subprocess

# Configure logging
# زيادة مستوى التسجيل لرؤية معلومات أكثر فائدة عند الحاجة
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app) # <-- الخطوة 2: تفعيل CORS لجميع المصادر

# Configuration
UPLOAD_FOLDER = 'downloads'
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
ALLOWED_PLATFORMS = ['youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'facebook.com']
SECRET_KEY = secrets.token_hex(16)
app.config['SECRET_KEY'] = SECRET_KEY

# Create directories if they don't exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
logging.info(f"Ensured directories exist: {VIDEO_FOLDER}, {AUDIO_FOLDER}")

# Helper Functions
def is_valid_url(url):
    """Validates if the URL is a valid URL and from supported platforms."""
    if not url: # Check if url is empty or None
        return False
    if not validators.url(url):
        logging.warning(f"Invalid URL format: {url}")
        return False
    is_allowed = any(platform in url for platform in ALLOWED_PLATFORMS)
    if not is_allowed:
        logging.warning(f"URL from unsupported platform: {url}")
    return is_allowed

def generate_safe_filename(title):
    """Generates a safe filename from the video title."""
    safe_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    # استبدال المسافات بـ '_' قد يكون أفضل لتجنب مشاكل في بعض الأنظمة
    filename = ''.join(c for c in title if c in safe_chars).replace(' ', '_')
    # إزالة النقاط المتعددة المتتالية
    filename = "_".join(filter(None, filename.split('.')))
    # تقصير اسم الملف إذا كان طويلاً جداً (اختياري)
    max_len = 100
    if len(filename) > max_len:
        filename = filename[:max_len]
    return filename.strip('._ ') # إزالة أي رموز غير مرغوبة من البداية والنهاية

@app.route('/')
def home():
    # هذا المسار قد لا يتم استخدامه إذا كانت الواجهة الأمامية على Netlify
    # لكن من الجيد إبقاؤه للاختبار المحلي
    logging.info("Serving home page template.")
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url') # استخدام .get لتجنب KeyError إذا لم يتم إرسال الحقل
    mode = request.form.get('mode', 'video') # وضع افتراضي 'video'
    logging.info(f"Received /preview request for URL: {url}, Mode: {mode}")


    if not url:
         logging.warning("Preview request received without URL.")
         return jsonify({'error': 'الرجاء إدخال رابط!'}), 400 # Bad Request

    if not is_valid_url(url):
        logging.warning(f"Preview request with invalid/unsupported URL: {url}")
        return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400

    try:
        # استخدام الخيارات التي تسرع العملية وتجنب المشاكل
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'simulate': True, # simulate is deprecated, use skip_download
            'extract_flat': 'in_playlist', # أسرع لاستخراج المعلومات الأولية
            'forcejson': True, # الحصول على المخرجات كـ JSON مباشرة
            'noplaylist': True, # منع معالجة قوائم التشغيل
            'ignoreerrors': True, # محاولة الاستمرار حتى لو كان هناك خطأ بسيط
            'socket_timeout': 10, # مهلة للاتصال
        }

        # لا حاجة لتحديد format هنا لأننا نريد فقط المعلومات الأولية
        # سنحصل على الصيغ لاحقًا إذا لزم الأمر

        logging.info(f"Extracting info for {url} with options: {ydl_opts}")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if not info: # Check if info is None or empty
                     raise youtube_dl.utils.DownloadError("Failed to extract information, info is empty.")

            except youtube_dl.utils.DownloadError as e:
                logging.error(f"yt-dlp info extraction failed for {url}: {e}")
                # محاولة تقديم رسالة خطأ أكثر تحديدًا للمستخدم
                error_msg = 'فشل استخراج معلومات الفيديو. قد يكون الفيديو غير متاح، خاص، أو يتطلب تسجيل الدخول.'
                if 'private' in str(e).lower():
                    error_msg = 'الفيديو خاص ولا يمكن الوصول إليه.'
                elif 'unavailable' in str(e).lower():
                    error_msg = 'الفيديو غير متوفر في منطقتك أو تم حذفه.'
                elif 'login required' in str(e).lower():
                    error_msg = 'هذا المحتوى يتطلب تسجيل الدخول ولا يمكن تحميله حاليًا.'
                return jsonify({'error': error_msg}), 404 # Not Found or Forbidden
            except Exception as e:
                logging.error(f"Unexpected error during info extraction for {url}: {e}", exc_info=True) # Log traceback
                return jsonify({'error': 'حدث خطأ غير متوقع أثناء استخراج المعلومات.'}), 500


        # الآن لدينا المعلومات الأساسية، لنستخرج الصيغ المطلوبة
        title = info.get('title', 'غير متوفر')
        duration = info.get('duration') # قد يكون None
        thumbnail = info.get('thumbnail') or info.get('thumbnails', [{}])[0].get('url') # محاولة الحصول على الصورة المصغرة


        # إعادة استخراج الصيغ بشكل منفصل إذا لزم الأمر (قد لا يكون ضرورياً مع forcejson)
        # هذا الجزء قد يحتاج لمراجعة بناءً على مخرجات forcejson
        ydl_opts_formats = {
             'quiet': True,
             'no_warnings': True,
             'listformats': True, # طلب قائمة الصيغ
             'noplaylist': True,
             'ignoreerrors': True,
             'socket_timeout': 10,
        }
        logging.info(f"Extracting formats for {url}...")
        formats_info_str = None
        try:
             with youtube_dl.YoutubeDL(ydl_opts_formats) as ydl_formats:
                  # yt-dlp مع listformats يطبع إلى stdout, نحتاج لالتقاطه أو استخدام API مختلف
                  # الأسهل غالبًا هو استخراج المعلومات مرة أخرى بدون skip_download / extract_flat
                  info_with_formats = youtube_dl.YoutubeDL({'quiet': True, 'no_warnings': True, 'noplaylist': True, 'ignoreerrors': True}).extract_info(url, download=False)
                  if not info_with_formats:
                       raise youtube_dl.utils.DownloadError("Failed to extract formats.")
                  formats = info_with_formats.get('formats', [])

        except Exception as e:
             logging.error(f"Failed to get formats for {url}: {e}")
             formats = [] # متابعة بدون صيغ إذا فشل الاستخراج الثاني


        if mode == 'audio':
             # في وضع الصوت، نعرض خيارًا واحدًا فقط
             logging.info(f"Preview mode 'audio' for {url}. Sending audio-only option.")
             return jsonify({
                'title': title,
                'duration': duration or 0,
                'thumbnail': thumbnail or '',
                'qualities': [('bestaudio/best', 'صوت فقط')], # رمز الجودة وقيمتها
                'mode': mode # إعادة الوضع المطلوب
             })

        # فلترة وتجميع جودات الفيديو
        unique_qualities = {}
        for f in formats:
            # التأكد من وجود فيديو وصوت (أو فيديو فقط إذا كان المستخدم سيختار الصوت لاحقًا)
            # وله ارتفاع (height)
             if f.get('vcodec') != 'none' and f.get('height'):
                 height = f.get('height')
                 format_id = f.get('format_id')
                 # نعطي الأولوية للصيغ التي تحتوي على فيديو وصوت مدمجين (mp4 غالبًا)
                 # أو نأخذ أعلى جودة لكل ارتفاع
                 # هذا المنطق قد يحتاج لتحسين بناءً على المنصة
                 is_merged_format = f.get('acodec') != 'none' and f.get('ext') == 'mp4'

                 # إذا لم يكن لدينا هذا الارتفاع أو الصيغة الحالية أفضل (مدمجة أو أعلى bitrate)
                 if height not in unique_qualities or is_merged_format or f.get('tbr', 0) > unique_qualities.get(height, {}).get('tbr', 0):
                       unique_qualities[height] = {'id': format_id, 'label': str(height), 'tbr': f.get('tbr',0)} # tbr = total bitrate (approx)

        # تحويل القاموس إلى قائمة مرتبة حسب الارتفاع (الأعلى أولاً)
        # qualities_list = sorted(unique_qualities.values(), key=lambda item: int(item['label']), reverse=True)
        # Format required by frontend: list of tuples [ (id, label), ... ]
        qualities_tuples = sorted(
             [(q['id'], q['label']) for q in unique_qualities.values()],
             key=lambda item: int(item[1]), # Sort by height (label)
             reverse=True # Highest quality first
        )


        logging.info(f"Preview mode 'video' for {url}. Found qualities: {qualities_tuples}")
        return jsonify({
            'title': title,
            'duration': duration or 0,
            'thumbnail': thumbnail or '',
            'qualities': qualities_tuples, # إرسال قائمة الجودات المفلترة
            'mode': mode
        })

    except Exception as e:
        logging.error(f"General error in /preview for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ غير متوقع أثناء المعاينة. يرجى المحاولة مرة أخرى.'}), 500


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality')
    # التحقق من قيمة audio_only القادمة من الواجهة
    audio_only_str = request.form.get('audio_only', 'false').lower()
    audio_only = audio_only_str == 'true'

    mode = request.form.get('mode') # 'trim', 'auto', 'audio'
    start_time = request.form.get('start_time', '0') # قيمة بالثواني
    end_time = request.form.get('end_time') # قيمة بالثواني أو None

    logging.info(f"Received /download request for URL: {url}, Quality: {quality}, AudioOnly: {audio_only}, Mode: {mode}, Start: {start_time}, End: {end_time}")

    if not url or not quality:
         logging.warning("Download request missing URL or Quality.")
         return jsonify({'error': 'بيانات الطلب غير كاملة (الرابط أو الجودة مفقودة).'}), 400

    if not is_valid_url(url):
        logging.warning(f"Download request with invalid/unsupported URL: {url}")
        return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400

    # التحقق من وجود ffmpeg (مهم جدًا)
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        logging.error("FFmpeg not found in PATH!")
        # هذا الخطأ يجب ألا يحدث على Render إذا تم إعداد Dockerfile بشكل صحيح
        return jsonify({'error': 'خطأ في إعدادات الخادم: FFmpeg غير موجود.'}), 500

    # تحديد مجلد الإخراج بناءً على audio_only
    output_dir = AUDIO_FOLDER if audio_only else VIDEO_FOLDER
    logging.info(f"Output directory set to: {output_dir}")

    # اسم ملف مؤقت أولي (yt-dlp سيضيف الامتداد الصحيح)
    # استخدام اسم آمن ونظيف
    temp_filename_pattern = os.path.join(output_dir, f"download_{secrets.token_hex(8)}.%(ext)s")

    try:
        ydl_opts = {
            'outtmpl': temp_filename_pattern, # قالب لاسم الملف المؤقت
            'ffmpeg_location': ffmpeg_path,
            'quiet': True,
            'no_warnings': True,
            'encoding': 'utf-8',
            'noplaylist': True,
            'noprogress': True, # منع طباعة شريط التقدم
            'postprocessor_args': { # تحسينات لـ ffmpeg
                 'ffmpeg': ['-v', 'error'] # تقليل مخرجات ffmpeg في السجل
            } if not audio_only else { # خيارات خاصة بالصوت
                 'ffmpeg': ['-v', 'error']
            },
            # تحديد الصيغة النهائية بعناية
            'format': None, # سيتم تحديده أدناه
        }

        if audio_only:
            logging.info("Setting options for audio download.")
            ydl_opts.update({
                'format': 'bestaudio/best', # اطلب أفضل صوت
                'extract_audio': True,      # استخراج الصوت
                'audio_format': 'mp3',      # تحديد الصيغة النهائية للصوت
                'audio_quality': 0,         # 0 = أفضل جودة (لـ MP3 VBR)
                'keep_video': False,       # عدم الاحتفاظ بملف الفيديو المؤقت
                'postprocessors': [{       # تحديد المعالج اللاحق لاستخراج الصوت
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            })
            # اسم الملف النهائي سيكون له امتداد .mp3 بسبب المعالج اللاحق
            final_file_ext = 'mp3'
        else:
            logging.info(f"Setting options for video download, quality: {quality}")
            # تحتاج إلى دمج الفيديو والصوت إذا لم يكن quality يمثلهما معاً
            # quality قد يكون id لفيديو فقط، أو id لصيغة مدمجة
            # Format selection needs care. Example: best video with given ID + best audio, merged into mp4
            # Needs testing if `quality` refers to already merged formats (like from youtube)
            # Assuming quality might be just video stream ID
            ydl_opts.update({
                 'format': f"{quality}+bestaudio/bestvideo+bestaudio", # محاولة دمج أفضل فيديو + أفضل صوت
                 'merge_output_format': 'mp4', # الصيغة النهائية المفضلة
            })
            final_file_ext = 'mp4'

        # --- بدء عملية التنزيل والمعالجة بواسطة yt-dlp ---
        logging.info(f"Starting download/processing for {url} with options: {ydl_opts}")
        downloaded_file_path = None
        info = None
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # استخراج المعلومات الكاملة بما في ذلك مسار الملف بعد المعالجة
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise youtube_dl.utils.DownloadError("extract_info returned empty.")

                # الحصول على المسار النهائي للملف بعد معالجة yt-dlp (بما في ذلك تغيير الامتداد إلى mp3)
                # yt-dlp لا يعيد المسار مباشرة بشكل موثوق بعد المعالجات اللاحقة
                # سنحتاج لتخمين اسم الملف أو البحث عنه
                # الطريقة الأبسط: البحث عن أحدث ملف بالامتداد المتوقع في مجلد الإخراج
                list_of_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
                if not list_of_files:
                    raise FileNotFoundError("No files found in output directory after download.")

                # العثور على الملف الذي تم إنشاؤه مؤخرًا بالامتداد الصحيح
                latest_file = max(list_of_files, key=os.path.getctime)
                if latest_file.lower().endswith(f'.{final_file_ext}'):
                    downloaded_file_path = latest_file
                    logging.info(f"Download successful. File path identified: {downloaded_file_path}")
                else:
                    # حالة نادرة: ربما استخدم yt-dlp امتدادًا مختلفًا
                    logging.warning(f"Latest file {latest_file} doesn't have expected extension .{final_file_ext}. Trying to use it anyway.")
                    downloaded_file_path = latest_file # Attempt to use it


                if not downloaded_file_path or not os.path.exists(downloaded_file_path):
                     raise FileNotFoundError(f"Could not determine or find the final downloaded file with extension .{final_file_ext}")


            except youtube_dl.utils.DownloadError as e:
                logging.error(f"yt-dlp download/processing failed for {url}: {e}")
                error_msg = 'فشل تنزيل أو معالجة الملف. قد يكون المحتوى محمياً أو غير متاح بهذه الجودة.'
                return jsonify({'error': error_msg}), 500 # Internal Server Error or suitable code
            except FileNotFoundError as e:
                 logging.error(f"File handling error after download for {url}: {e}")
                 return jsonify({'error': 'خطأ في التعامل مع الملفات بعد التنزيل.'}), 500
            except Exception as e:
                logging.error(f"Unexpected error during yt-dlp processing for {url}: {e}", exc_info=True)
                return jsonify({'error': 'حدث خطأ غير متوقع أثناء التنزيل.'}), 500


        # --- الآن لدينا الملف المحمّل (downloaded_file_path) ---
        final_output_path = downloaded_file_path # المسار الافتراضي هو الملف المحمل

        # --- التعامل مع القص (Trimming) إذا كان مطلوبًا ---
        # يتم القص *بعد* التنزيل الكامل والمعالجة الأولية (مثل استخراج الصوت)
        if mode == 'trim' and info and (start_time != '0' or end_time):
            logging.info(f"Trimming requested: Start={start_time}s, End={end_time}s")
            video_duration = info.get('duration') # مدة الفيديو الأصلي بالثواني

            # التحقق من صحة أوقات القص (بالثواني)
            try:
                start_sec = float(start_time)
                if video_duration is not None and start_sec >= video_duration:
                    logging.warning(f"Start time {start_sec}s >= duration {video_duration}s")
                    os.remove(downloaded_file_path) # تنظيف الملف غير المقصوص
                    return jsonify({'error': 'وقت البداية يتجاوز مدة الملف!'}), 400

                trim_opts = ['-ss', str(start_sec)] # وقت البداية
                if end_time and end_time.strip():
                    end_sec = float(end_time)
                    if video_duration is not None and end_sec > video_duration:
                        logging.warning(f"End time {end_sec}s > duration {video_duration}s. Trimming till end.")
                        # لا نضيف -to, سيقص حتى النهاية
                    elif end_sec <= start_sec:
                        logging.warning(f"End time {end_sec}s <= start time {start_sec}s")
                        os.remove(downloaded_file_path)
                        return jsonify({'error': 'وقت النهاية يجب أن يكون أكبر من وقت البداية!'}), 400
                    else:
                        # استخدام -to هو الأكثر دقة للقص
                        trim_opts.extend(['-to', str(end_sec)])

            except ValueError:
                 logging.warning("Invalid start/end time format for trimming.")
                 os.remove(downloaded_file_path)
                 return jsonify({'error': 'تنسيق وقت البداية أو النهاية غير صالح.'}), 400


            # إنشاء اسم ملف جديد للملف المقصوص
            base, ext = os.path.splitext(os.path.basename(downloaded_file_path))
            # استخدام اسم آمن بناءً على العنوان الأصلي إن أمكن
            original_title = info.get('title', 'trimmed_file')
            safe_base_name = generate_safe_filename(original_title)
            trimmed_filename = f"{safe_base_name}_{secrets.token_hex(4)}_trimmed{ext}"
            trimmed_output_path = os.path.join(output_dir, trimmed_filename)
            logging.info(f"Output path for trimmed file: {trimmed_output_path}")


            # أمر ffmpeg للقص (استخدام -c copy أسرع إذا لم نغير الصيغة)
            # -avoid_negative_ts make_zero: لتجنب مشاكل timestamp السالبة
            ffmpeg_cmd = [
                ffmpeg_path,
                '-v', 'error', # تسجيل الأخطاء فقط
                '-i', downloaded_file_path, # الملف الأصلي المدخل
                *trim_opts,                 # خيارات وقت البداية/النهاية
                '-c', 'copy',               # نسخ الترميز (سريع جداً)
                '-avoid_negative_ts', 'make_zero', # معالجة timestamps
                '-y',                       # الكتابة فوق الملف إذا كان موجودًا
                trimmed_output_path         # اسم الملف الناتج
            ]

            logging.info(f"Running FFmpeg trim command: {' '.join(ffmpeg_cmd)}")
            try:
                # تشغيل أمر القص والتحقق من عدم وجود أخطاء
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True) # Capture output to check errors
                logging.info("FFmpeg trimming completed successfully.")

                # حذف الملف الأصلي غير المقصوص
                try:
                    os.remove(downloaded_file_path)
                    logging.info(f"Removed original untrimmed file: {downloaded_file_path}")
                except OSError as e:
                    logging.warning(f"Could not remove original file {downloaded_file_path}: {e}")

                final_output_path = trimmed_output_path # المسار النهائي هو الملف المقصوص

            except subprocess.CalledProcessError as e:
                logging.error(f"FFmpeg trimming failed! Command: {' '.join(e.cmd)}. Error: {e.stderr.decode()}")
                # محاولة حذف الملفات المؤقتة
                if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path)
                if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                return jsonify({'error': 'فشل قص الملف. تحقق من أوقات البداية والنهاية أو قد تكون الصيغة غير مدعومة للقص السريع.'}), 500
            except Exception as e:
                 logging.error(f"Unexpected error during trimming: {e}", exc_info=True)
                 if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path)
                 if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                 return jsonify({'error': 'حدث خطأ غير متوقع أثناء قص الملف.'}), 500


        # --- الخطوة النهائية: إرجاع اسم الملف للواجهة الأمامية ---
        final_filename = os.path.basename(final_output_path)
        logging.info(f"Download/Trim successful. Returning filename: {final_filename}")
        return jsonify({'success': True, 'filename': final_filename})

    except Exception as e:
        # Catch-all ل أي خطأ غير متوقع في العملية بأكملها
        logging.error(f"Major error in /download endpoint for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ عام أثناء عملية التنزيل. يرجى المحاولة مرة أخرى.'}), 500


# --- تعديل دالة تحميل الملف ---
@app.route('/downloads/<path:filename>')
def download_file(filename):
    logging.info(f"Received request to download file: {filename}")

    # تحديد المجلدات المحتملة
    possible_folders = [AUDIO_FOLDER, VIDEO_FOLDER]
    found_path = None

    # البحث عن الملف في المجلدين
    for folder in possible_folders:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            # التحقق الأمني (مهم جداً) - هل المسار الفعلي يبدأ بمسار المجلد المسموح به؟
            abs_folder_path = os.path.abspath(folder)
            abs_file_path = os.path.abspath(file_path)
            if abs_file_path.startswith(abs_folder_path):
                found_path = file_path
                directory_to_serve_from = folder
                logging.info(f"File found in: {directory_to_serve_from}")
                break # توقف عند العثور على الملف
            else:
                 # تسجيل محاولة وصول غير مصرح بها
                 logging.error(f"Security Alert: Attempt to access file outside allowed directory! Requested: {filename}, Resolved Path: {abs_file_path}, Allowed Folder: {abs_folder_path}")
                 return jsonify({'error': 'Access denied.'}), 403 # Forbidden

    if not found_path:
        logging.error(f"File not found in any specified directory: {filename}")
        return jsonify({'error': 'الملف المطلوب غير موجود أو تم حذفه.'}), 404 # Not Found

    try:
        logging.info(f"Sending file: {filename} from directory: {directory_to_serve_from}")
        # إرسال الملف للمستخدم كتنزيل (as_attachment=True)
        return send_from_directory(directory_to_serve_from, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error sending file {filename}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ أثناء إرسال الملف.'}), 500

# --- نهاية تعديل دالة تحميل الملف ---


@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error triggered: {e}", exc_info=True) # Log full traceback for 500 errors
    return jsonify({'error': 'حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى لاحقًا.'}), 500

if __name__ == '__main__':
    # اجعل التطبيق يستمع على كل الواجهات وعلى البورت المعطى من Render (أو 5000 افتراضي)
    # يجب أن يكون debug=False في الإنتاج
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask server on host 0.0.0.0, port {port}, debug=False")
    app.run(debug=False, host='0.0.0.0', port=port)