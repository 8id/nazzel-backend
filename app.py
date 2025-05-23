# --- استيرادات ومقدمة الملف كما هي ---
from flask import Flask, request, render_template, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import yt_dlp as youtube_dl
import os
import logging
import shutil
import validators
import secrets
import string
import subprocess
import requests
from urllib.parse import urlparse
# -------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'downloads'
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
ALLOWED_PLATFORMS = ['youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'facebook.com']
SECRET_KEY = secrets.token_hex(16)
app.config['SECRET_KEY'] = SECRET_KEY
INSTAGRAM_COOKIE_PATH = "/tmp/instagram_cookies.txt"
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
logging.info(f"Ensured directories exist: {VIDEO_FOLDER}, {AUDIO_FOLDER}")

# --- الدوال المساعدة (is_valid_url, generate_safe_filename) تبقى كما هي ---
def is_valid_url(url):
    if not url: return False
    if not validators.url(url):
        logging.warning(f"Invalid URL format: {url}")
        return False
    is_allowed = any(platform in url for platform in ALLOWED_PLATFORMS)
    if not is_allowed:
        logging.warning(f"URL from unsupported platform: {url}")
    return is_allowed

def generate_safe_filename(title):
    safe_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in title if c in safe_chars).replace(' ', '_')
    filename = "_".join(filter(None, filename.split('.')))
    max_len = 100
    if len(filename) > max_len: filename = filename[:max_len]
    return filename.strip('._ ')

@app.route('/')
def home():
    logging.info("Serving home page template.")
    return render_template('index.html')

# --- دالة image_proxy تبقى كما هي ---
@app.route('/image-proxy')
def image_proxy():
    image_url = request.args.get('url')
    if not image_url: return jsonify({'error': 'Missing image URL parameter'}), 400
    try:
        parsed_url = urlparse(image_url)
        allowed_domains = ['cdninstagram.com', 'fbcdn.net', 'googleusercontent.com', 'ggpht.com','tiktokcdn.com', 'tiktokcdn-us.com', 'ibyteimg.com', 'tiktok.com' ]
        hostname = parsed_url.hostname
        if not hostname or not any(hostname.endswith(domain) for domain in allowed_domains):
            logging.warning(f"Image proxy request blocked for disallowed domain: {hostname} from URL {image_url}")
            return jsonify({'error': 'Disallowed domain for image proxy'}), 403
    except Exception as e:
        logging.error(f"Error parsing image URL for proxy: {image_url} - {e}")
        return jsonify({'error': 'Invalid image URL format'}), 400
    logging.info(f"Proxying image from: {image_url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(image_url, stream=True, timeout=15, headers=headers)
        res.raise_for_status()
        content_type = res.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
             logging.warning(f"Proxy blocked non-image content type: {content_type} from {image_url}")
             return jsonify({'error': 'Invalid content type'}), 400
        return Response(stream_with_context(res.iter_content(chunk_size=8192)), content_type=content_type)
    except requests.exceptions.Timeout:
         logging.error(f"Timeout fetching image via proxy: {image_url}")
         return jsonify({'error': 'Timeout fetching image from origin'}), 504
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching image via proxy: {e}")
        status_code = 502
        if hasattr(e, 'response') and e.response is not None: status_code = e.response.status_code if e.response.status_code >= 400 else 502
        return jsonify({'error': f'Failed to fetch image from origin: {e}'}), status_code
    except Exception as e:
         logging.error(f"Unexpected error in image proxy: {e}", exc_info=True)
         return jsonify({'error': 'Unexpected error in image proxy'}), 500

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url')
    mode = request.form.get('mode', 'video')
    logging.info(f"Raw Preview Request Data - URL: {request.form.get('url')}, Mode: {request.form.get('mode')}") # للتصحيح
    logging.info(f"Parsed Preview Request - URL: {url}, Mode: {mode}")

    if not url:
         logging.warning("Preview request received without URL.")
         return jsonify({'error': 'الرجاء إدخال رابط!'}), 400

    is_youtube = 'youtube.com' in url or 'youtu.be' in url # التحقق إذا كان يوتيوب
    valid = is_valid_url(url)
    logging.info(f"URL validation result for {url}: {valid}")

    if not valid:
        logging.warning(f"Preview request with invalid/unsupported URL after check: {url}")
        return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400

    try:
        # ... (إعدادات ydl_opts كما كانت) ...
        ydl_opts = {
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'extract_flat': 'in_playlist', 'forcejson': True, 'noplaylist': True,
            'ignoreerrors': True, 'socket_timeout': 15,
        }
        is_instagram = 'instagram.com' in url
        cookie_file_exists = os.path.exists(INSTAGRAM_COOKIE_PATH)
        if is_instagram and cookie_file_exists:
             logging.info(f"Instagram URL (initial info). Using cookies from: {INSTAGRAM_COOKIE_PATH}")
             ydl_opts['cookiefile'] = INSTAGRAM_COOKIE_PATH
        elif is_instagram: logging.warning(f"Instagram URL (initial info) but cookie file not found at {INSTAGRAM_COOKIE_PATH}.")

        logging.info(f"Extracting initial info for {url} with options: {ydl_opts}")
        info = None
        try:
            ydl_opts['socket_timeout'] = 20
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info: raise youtube_dl.utils.DownloadError("Failed to extract information, info is empty.")
        # --- تعديل معالجة خطأ yt-dlp ---
        except youtube_dl.utils.DownloadError as e:
            logging.error(f"yt-dlp info extraction failed for {url}: {e}")
            error_msg = 'فشل استخراج معلومات الفيديو.' # رسالة عامة
            youtube_specific = False
            str_e = str(e).lower()
            # التحقق من الكلمات الدالة على خطأ الوصول
            if 'unavailable' in str_e or 'private' in str_e or 'login required' in str_e or 'rate limit' in str_e:
                 error_msg += ' قد يكون الفيديو غير متاح، خاص، يتطلب تسجيل الدخول أو تم الوصول لحد الطلبات.'
                 if is_youtube: # إذا كان الخطأ ليوتيوب ومن هذا النوع
                      youtube_specific = True
            # يمكنك إضافة المزيد من التحققات هنا لأنواع أخطاء أخرى إذا لزم الأمر
            return jsonify({'error': error_msg, 'youtube_specific_error': youtube_specific}), 400 # إرجاع 400 وإضافة العلامة
        # ---------------------------------
        except Exception as e:
            logging.error(f"Unexpected error during initial info extraction for {url}: {e}", exc_info=True)
            return jsonify({'error': 'حدث خطأ غير متوقع أثناء استخراج المعلومات.'}), 500

        # ... (باقي الكود لاستخراج الصيغ وعرض النتيجة يبقى كما هو تقريبًا) ...
        # ... مع التأكد من استخدام المسار المؤقت للكوكيز إذا كان إنستغرام ...
        title = info.get('title', 'غير متوفر')
        duration = info.get('duration')
        thumbnail = info.get('thumbnail') or info.get('thumbnails', [{}])[-1].get('url')

        ydl_opts_formats = {
             'quiet': True, 'no_warnings': True, 'noplaylist': True,
             'ignoreerrors': True, 'socket_timeout': 15,
        }
        if is_instagram and cookie_file_exists:
            logging.info(f"Using Instagram cookies for format extraction from: {INSTAGRAM_COOKIE_PATH}")
            ydl_opts_formats['cookiefile'] = INSTAGRAM_COOKIE_PATH

        logging.info(f"Extracting formats for {url}...")
        formats = []
        # ... (منطق استخراج الصيغ ومعالجة أخطائه يبقى كما هو) ...
        try:
             ydl_opts_formats['socket_timeout'] = 20
             with youtube_dl.YoutubeDL(ydl_opts_formats) as ydl_formats:
                  info_with_formats = ydl_formats.extract_info(url, download=False)
                  if info_with_formats: formats = info_with_formats.get('formats', [])
                  else: logging.warning(f"Second info extraction returned empty for {url}.")
        except youtube_dl.utils.DownloadError as e:
             logging.error(f"Failed to get formats for {url}: {e}")
             # لا داعي لإرجاع خطأ هنا إذا فشل استخراج الصيغ فقط، قد تكون المعلومات الأساسية كافية
        except Exception as e:
             logging.error(f"Unexpected error during format extraction for {url}: {e}", exc_info=True)

        if mode == 'audio':
             return jsonify({'title': title, 'duration': duration or 0, 'thumbnail': thumbnail or '', 'qualities': [('bestaudio/best', 'صوت فقط')], 'mode': mode})

        unique_qualities = {}
        # ... (منطق فلترة الجودات كما كان) ...
        if formats:
            for f in formats:
                 height = f.get('height')
                 format_id = f.get('format_id')
                 if f.get('vcodec') != 'none' and height and format_id:
                     is_preferred = f.get('acodec') != 'none' and f.get('ext') == 'mp4'
                     current_best_tbr = unique_qualities.get(height, {}).get('tbr', -1)
                     current_is_preferred = unique_qualities.get(height, {}).get('preferred', False)
                     new_tbr = f.get('tbr') or f.get('vbr') or f.get('abr') or 0
                     if height not in unique_qualities or (is_preferred and not current_is_preferred) or (is_preferred == current_is_preferred and new_tbr > current_best_tbr):
                           unique_qualities[height] = {'id': format_id, 'label': str(height), 'tbr': new_tbr, 'preferred': is_preferred}
        else: logging.warning(f"No formats found for {url}. Cannot provide quality options.")
        qualities_tuples = sorted([(q['id'], q['label']) for q in unique_qualities.values()], key=lambda item: int(item[1]), reverse=True)

        logging.info(f"Preview mode 'video' for {url}. Found qualities: {qualities_tuples}")
        return jsonify({'title': title, 'duration': duration or 0, 'thumbnail': thumbnail or '', 'qualities': qualities_tuples, 'mode': mode })

    except Exception as e:
        logging.error(f"General error in /preview for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ غير متوقع أثناء المعاينة. يرجى المحاولة مرة أخرى.'}), 500


@app.route('/download', methods=['POST'])
def download():
    # ... (بداية الدالة والتحقق من المدخلات كما كانت) ...
    url = request.form.get('url')
    quality = request.form.get('quality')
    audio_only_str = request.form.get('audio_only', 'false').lower()
    audio_only = audio_only_str == 'true'
    mode = request.form.get('mode')
    start_time = request.form.get('start_time', '0')
    end_time = request.form.get('end_time')
    logging.info(f"Received /download request for URL: {url}, Quality: {quality}, AudioOnly: {audio_only}, Mode: {mode}, Start: {start_time}, End: {end_time}")
    if not url or not quality: return jsonify({'error': 'بيانات الطلب غير كاملة (الرابط أو الجودة مفقودة).'}), 400
    is_youtube = 'youtube.com' in url or 'youtu.be' in url # التحقق إذا كان يوتيوب
    if not is_valid_url(url): return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path: return jsonify({'error': 'خطأ في إعدادات الخادم: FFmpeg غير موجود.'}), 500
    output_dir = AUDIO_FOLDER if audio_only else VIDEO_FOLDER
    logging.info(f"Output directory set to: {output_dir}")
    temp_filename_pattern = os.path.join(output_dir, f"download_{secrets.token_hex(8)}.%(ext)s")

    try:
        # ... (إعدادات ydl_opts كما كانت) ...
        ydl_opts = {
            'outtmpl': temp_filename_pattern, 'ffmpeg_location': ffmpeg_path,
            'quiet': True, 'no_warnings': True, 'encoding': 'utf-8',
            'noplaylist': True, 'noprogress': True,
            'postprocessor_args': {'ffmpeg': ['-v', 'error']},
            'format': None, 'socket_timeout': 60, 'retries': 3,
        }
        is_instagram = 'instagram.com' in url
        cookie_file_exists = os.path.exists(INSTAGRAM_COOKIE_PATH)
        if is_instagram and cookie_file_exists:
            logging.info(f"Instagram URL detected for download. Using cookies from: {INSTAGRAM_COOKIE_PATH}")
            ydl_opts['cookiefile'] = INSTAGRAM_COOKIE_PATH
        elif is_instagram:
            logging.error(f"Instagram URL detected for download but cookie file not found at {INSTAGRAM_COOKIE_PATH}.")
            return jsonify({'error': 'فشل التحميل من انستغرام، قد يتطلب الأمر كوكيز صالحة على الخادم.'}), 403

        # ... (تحديد صيغة التحميل final_file_ext كما كان) ...
        if audio_only:
            logging.info("Setting options for audio download.")
            ydl_opts.update({'format': 'bestaudio/best', 'extract_audio': True, 'audio_format': 'mp3','audio_quality': 0, 'keep_video': False, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]})
            final_file_ext = 'mp3'
        else:
            logging.info(f"Setting options for video download, quality: {quality}")
            ydl_opts.update({'format': f"{quality}+bestaudio/best", 'merge_output_format': 'mp4'})
            final_file_ext = 'mp4'

        logging.info(f"Starting download/processing for {url} with final options: {ydl_opts}")
        downloaded_file_path = None
        info = None
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                if not info: raise youtube_dl.utils.DownloadError("extract_info returned empty.")
                # ... (منطق العثور على الملف المحمل كما كان) ...
                filename_in_info = ydl.prepare_filename(info)
                if filename_in_info.lower().endswith(f'.{final_file_ext}') and os.path.exists(filename_in_info): downloaded_file_path = filename_in_info
                else:
                    logging.warning(f"Filename from info ({filename_in_info}) doesn't match expected extension .{final_file_ext} or doesn't exist. Searching directory.")
                    list_of_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
                    if not list_of_files: raise FileNotFoundError("No files found in output directory after download attempt.")
                    possible_files = [f for f in list_of_files if f.lower().endswith(f'.{final_file_ext}')]
                    if possible_files: latest_file = max(possible_files, key=os.path.getctime); downloaded_file_path = latest_file
                    else: latest_file = max(list_of_files, key=os.path.getctime); logging.warning(f"Could not find file with extension .{final_file_ext}. Using latest file found: {latest_file}"); downloaded_file_path = latest_file
                if not downloaded_file_path or not os.path.exists(downloaded_file_path): raise FileNotFoundError(f"Could not determine or find the final downloaded file.")
                logging.info(f"Download successful. File path identified: {downloaded_file_path}")

            # --- تعديل معالجة خطأ yt-dlp ---
            except youtube_dl.utils.DownloadError as e:
                 logging.error(f"yt-dlp download/processing failed for {url}: {e}")
                 error_msg = 'فشل تنزيل أو معالجة الملف.'
                 youtube_specific = False
                 str_e = str(e).lower()
                 if 'unavailable' in str_e or 'private' in str_e or 'login required' in str_e or 'rate limit' in str_e:
                     error_msg += ' قد يكون المحتوى محمياً، غير متاح بهذه الجودة، يتطلب كوكيز صالحة، أو تم الوصول لحد الطلبات.'
                     if is_youtube: youtube_specific = True
                 # يمكنك تخصيص الرسالة أكثر هنا إذا أردت
                 return jsonify({'error': error_msg, 'youtube_specific_error': youtube_specific}), 500 # إرجاع 500 للخطأ الداخلي وإضافة العلامة
            # ---------------------------------
            except FileNotFoundError as e:
                 logging.error(f"File handling error after download for {url}: {e}")
                 return jsonify({'error': 'خطأ في التعامل مع الملفات بعد التنزيل.'}), 500
            except Exception as e:
                logging.error(f"Unexpected error during yt-dlp processing for {url}: {e}", exc_info=True)
                return jsonify({'error': 'حدث خطأ غير متوقع أثناء التنزيل.'}), 500

        # ... (باقي الكود للقص وإرجاع اسم الملف كما كان) ...
        final_output_path = downloaded_file_path
        if mode == 'trim' and info and (start_time != '0' or end_time):
            logging.info(f"Trimming requested: Start={start_time}s, End={end_time}s")
            # ... (منطق القص المفصل كما كان) ...
            # ... (معالجة أخطاء القص كما كانت) ...
            video_duration = info.get('duration')
            try:
                start_sec = float(start_time)
                if video_duration is not None and start_sec >= video_duration: logging.warning(f"Start time {start_sec}s >= duration {video_duration}s"); os.remove(downloaded_file_path); return jsonify({'error': 'وقت البداية يتجاوز مدة الملف!'}), 400
                trim_opts = ['-ss', str(start_sec)]
                if end_time and end_time.strip():
                    end_sec = float(end_time)
                    if video_duration is not None and end_sec > video_duration: logging.warning(f"End time {end_sec}s > duration {video_duration}s. Trimming till end.")
                    elif end_sec <= start_sec: logging.warning(f"End time {end_sec}s <= start time {start_sec}s"); os.remove(downloaded_file_path); return jsonify({'error': 'وقت النهاية يجب أن يكون أكبر من وقت البداية!'}), 400
                    else: trim_opts.extend(['-to', str(end_sec)])
            except ValueError: logging.warning("Invalid start/end time format for trimming."); os.remove(downloaded_file_path); return jsonify({'error': 'تنسيق وقت البداية أو النهاية غير صالح.'}), 400
            original_title = info.get('title', 'trimmed_file')
            safe_base_name = generate_safe_filename(original_title)
            base, ext = os.path.splitext(os.path.basename(downloaded_file_path))
            trimmed_filename = f"{safe_base_name}_{secrets.token_hex(4)}_trimmed{ext}"
            trimmed_output_path = os.path.join(output_dir, trimmed_filename)
            logging.info(f"Output path for trimmed file: {trimmed_output_path}")
            ffmpeg_cmd = [ffmpeg_path, '-v', 'error', '-i', downloaded_file_path, *trim_opts, '-c', 'copy', '-avoid_negative_ts', 'make_zero', '-y', trimmed_output_path]
            logging.info(f"Running FFmpeg trim command: {' '.join(ffmpeg_cmd)}")
            try:
                result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True); logging.info("FFmpeg trimming completed successfully.");
                if result.stderr: logging.warning(f"FFmpeg stderr (trim success): {result.stderr}")
                try: os.remove(downloaded_file_path); logging.info(f"Removed original untrimmed file: {downloaded_file_path}")
                except OSError as e: logging.warning(f"Could not remove original file {downloaded_file_path}: {e}")
                final_output_path = trimmed_output_path
            except subprocess.CalledProcessError as e:
                logging.error(f"FFmpeg trimming failed! Command: {' '.join(e.cmd)}. Stderr: {e.stderr}")
                if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path);
                if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                return jsonify({'error': 'فشل قص الملف. تحقق من الأوقات أو قد تكون الصيغة غير مدعومة للقص السريع.'}), 500
            except Exception as e:
                 logging.error(f"Unexpected error during trimming: {e}", exc_info=True)
                 if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path);
                 if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                 return jsonify({'error': 'حدث خطأ غير متوقع أثناء قص الملف.'}), 500

        final_filename = os.path.basename(final_output_path)
        logging.info(f"Operation successful. Returning filename: {final_filename}")
        return jsonify({'success': True, 'filename': final_filename})

    except Exception as e:
        logging.error(f"Major error in /download endpoint for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ عام أثناء عملية التنزيل. يرجى المحاولة مرة أخرى.'}), 500

# --- download_file, internal_server_error, if __name__ == '__main__' تبقى كما هي ---
@app.route('/downloads/<path:filename>')
def download_file(filename):
    logging.info(f"Received request to download file: {filename}")
    possible_folders = [AUDIO_FOLDER, VIDEO_FOLDER]
    found_path = None; directory_to_serve_from = None
    for folder in possible_folders:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            abs_folder_path = os.path.abspath(folder); abs_file_path = os.path.abspath(file_path)
            if abs_file_path.startswith(abs_folder_path):
                found_path = file_path; directory_to_serve_from = folder; logging.info(f"File found in: {directory_to_serve_from}"); break
            else: logging.error(f"Security Alert: Path {abs_file_path} not in allowed {abs_folder_path}"); return jsonify({'error': 'Access denied.'}), 403
    if not found_path: logging.error(f"File not found in any specified directory: {filename}"); return jsonify({'error': 'الملف المطلوب غير موجود أو تم حذفه.'}), 404
    try:
        logging.info(f"Sending file: {filename} from directory: {directory_to_serve_from}")
        return send_from_directory(directory_to_serve_from, filename, as_attachment=True)
    except Exception as e: logging.error(f"Error sending file {filename}: {e}", exc_info=True); return jsonify({'error': 'حدث خطأ أثناء إرسال الملف.'}), 500

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error triggered: {e}", exc_info=True)
    return jsonify({'error': 'حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى لاحقًا.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask server on host 0.0.0.0, port {port}, debug=False")
    app.run(debug=False, host='0.0.0.0', port=port)