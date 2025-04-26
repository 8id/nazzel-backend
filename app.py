from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp as youtube_dl
import os
import logging
import shutil
import validators
import secrets
import string
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'downloads'
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
ALLOWED_PLATFORMS = ['youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'facebook.com']
SECRET_KEY = secrets.token_hex(16)
app.config['SECRET_KEY'] = SECRET_KEY
# --- مسار ملف الكوكيز لـ Instagram ---
INSTAGRAM_COOKIE_PATH = "/etc/secrets/instagram_cookies.txt"
# ------------------------------------

# Create directories if they don't exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
logging.info(f"Ensured directories exist: {VIDEO_FOLDER}, {AUDIO_FOLDER}")

# Helper Functions
def is_valid_url(url):
    """Validates if the URL is a valid URL and from supported platforms."""
    if not url: return False
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
    filename = ''.join(c for c in title if c in safe_chars).replace(' ', '_')
    filename = "_".join(filter(None, filename.split('.')))
    max_len = 100
    if len(filename) > max_len: filename = filename[:max_len]
    return filename.strip('._ ')

@app.route('/')
def home():
    logging.info("Serving home page template.")
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form.get('url')
    mode = request.form.get('mode', 'video')
    logging.info(f"Received /preview request for URL: {url}, Mode: {mode}")

    if not url:
         logging.warning("Preview request received without URL.")
         return jsonify({'error': 'الرجاء إدخال رابط!'}), 400
    if not is_valid_url(url):
        logging.warning(f"Preview request with invalid/unsupported URL: {url}")
        return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400

    try:
        ydl_opts = {
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'extract_flat': 'in_playlist', 'forcejson': True, 'noplaylist': True,
            'ignoreerrors': True, 'socket_timeout': 15,
        }

        is_instagram = 'instagram.com' in url
        cookie_file_exists = os.path.exists(INSTAGRAM_COOKIE_PATH)

        if is_instagram:
            if cookie_file_exists:
                logging.info(f"Instagram URL (initial info). Using cookies from: {INSTAGRAM_COOKIE_PATH}")
                # --- التعديل: استخدام cookiesfrombrowser بدلاً من cookiefile ---
                ydl_opts['cookiesfrombrowser'] = ('firefox', INSTAGRAM_COOKIE_PATH)
                # --------------------------------------------------------
            else:
                logging.warning(f"Instagram URL (initial info) but cookie file not found at {INSTAGRAM_COOKIE_PATH}.")

        logging.info(f"Extracting initial info for {url} with options: {ydl_opts}")
        info = None
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info: raise youtube_dl.utils.DownloadError("Failed to extract information, info is empty.")
        except youtube_dl.utils.DownloadError as e:
            # ... (معالجة الأخطاء كما كانت) ...
            logging.error(f"yt-dlp info extraction failed for {url}: {e}")
            error_msg = 'فشل استخراج معلومات الفيديو. قد يكون الفيديو غير متاح، خاص، يتطلب تسجيل الدخول أو تم الوصول لحد الطلبات.'
            if 'private' in str(e).lower(): error_msg = 'الفيديو خاص ولا يمكن الوصول إليه.'
            elif 'unavailable' in str(e).lower(): error_msg = 'الفيديو غير متوفر.'
            elif 'login required' in str(e).lower(): error_msg = 'هذا المحتوى يتطلب تسجيل الدخول (قد تحتاج لتحديث الكوكيز).'
            elif 'rate limit' in str(e).lower(): error_msg = 'تم الوصول لحد الطلبات المسموح به لهذه المنصة. حاول لاحقاً.'
            return jsonify({'error': error_msg}), 400
        except Exception as e:
            logging.error(f"Unexpected error during initial info extraction for {url}: {e}", exc_info=True)
            return jsonify({'error': 'حدث خطأ غير متوقع أثناء استخراج المعلومات.'}), 500

        title = info.get('title', 'غير متوفر')
        duration = info.get('duration')
        thumbnail = info.get('thumbnail') or info.get('thumbnails', [{}])[0].get('url')

        ydl_opts_formats = {
             'quiet': True, 'no_warnings': True, 'noplaylist': True,
             'ignoreerrors': True, 'socket_timeout': 15,
        }
        if is_instagram:
            if cookie_file_exists:
                logging.info(f"Using Instagram cookies for format extraction.")
                # --- التعديل: استخدام cookiesfrombrowser بدلاً من cookiefile ---
                ydl_opts_formats['cookiesfrombrowser'] = ('firefox', INSTAGRAM_COOKIE_PATH)
                # --------------------------------------------------------
            else:
                logging.warning(f"Cookie file not found for Instagram format extraction.")

        logging.info(f"Extracting formats for {url}...")
        formats = []
        try:
             with youtube_dl.YoutubeDL(ydl_opts_formats) as ydl_formats:
                  info_with_formats = ydl_formats.extract_info(url, download=False)
                  if info_with_formats: formats = info_with_formats.get('formats', [])
                  else: logging.warning(f"Second info extraction returned empty for {url}.")
        except youtube_dl.utils.DownloadError as e:
             # ... (معالجة الأخطاء كما كانت) ...
             logging.error(f"Failed to get formats for {url}: {e}")
             if is_instagram and not cookie_file_exists: pass
             elif 'login required' in str(e).lower() or 'rate limit' in str(e).lower(): pass
             else: return jsonify({'error': 'فشل في الحصول على جودات الفيديو المتاحة.'}), 500
        except Exception as e:
             logging.error(f"Unexpected error during format extraction for {url}: {e}", exc_info=True)

        if mode == 'audio':
             logging.info(f"Preview mode 'audio' for {url}. Sending audio-only option.")
             return jsonify({
                'title': title, 'duration': duration or 0, 'thumbnail': thumbnail or '',
                'qualities': [('bestaudio/best', 'صوت فقط')], 'mode': mode
             })

        # ... (باقي كود فلترة الجودات وإرجاع النتيجة كما كان) ...
        unique_qualities = {}
        if formats:
            for f in formats:
                 height = f.get('height')
                 format_id = f.get('format_id')
                 if f.get('vcodec') != 'none' and height and format_id:
                     is_preferred = f.get('acodec') != 'none' and f.get('ext') == 'mp4'
                     current_best_tbr = unique_qualities.get(height, {}).get('tbr', -1)
                     current_is_preferred = unique_qualities.get(height, {}).get('preferred', False)
                     new_tbr = f.get('tbr') or f.get('vbr') or f.get('abr') or 0
                     if height not in unique_qualities or \
                        (is_preferred and not current_is_preferred) or \
                        (is_preferred == current_is_preferred and new_tbr > current_best_tbr):
                           unique_qualities[height] = {'id': format_id, 'label': str(height), 'tbr': new_tbr, 'preferred': is_preferred}
        else:
             logging.warning(f"No formats found for {url}. Cannot provide quality options.")

        qualities_tuples = sorted([(q['id'], q['label']) for q in unique_qualities.values()], key=lambda item: int(item[1]), reverse=True)
        logging.info(f"Preview mode 'video' for {url}. Found qualities: {qualities_tuples}")
        return jsonify({'title': title, 'duration': duration or 0, 'thumbnail': thumbnail or '', 'qualities': qualities_tuples, 'mode': mode })

    except Exception as e:
        logging.error(f"General error in /preview for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ غير متوقع أثناء المعاينة. يرجى المحاولة مرة أخرى.'}), 500


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality')
    audio_only_str = request.form.get('audio_only', 'false').lower()
    audio_only = audio_only_str == 'true'
    mode = request.form.get('mode')
    start_time = request.form.get('start_time', '0')
    end_time = request.form.get('end_time')

    logging.info(f"Received /download request for URL: {url}, Quality: {quality}, AudioOnly: {audio_only}, Mode: {mode}, Start: {start_time}, End: {end_time}")

    if not url or not quality:
         logging.warning("Download request missing URL or Quality.")
         return jsonify({'error': 'بيانات الطلب غير كاملة (الرابط أو الجودة مفقودة).'}), 400
    if not is_valid_url(url):
        logging.warning(f"Download request with invalid/unsupported URL: {url}")
        return jsonify({'error': 'الرابط غير صالح أو غير مدعوم!'}), 400

    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        logging.error("FFmpeg not found in PATH!")
        return jsonify({'error': 'خطأ في إعدادات الخادم: FFmpeg غير موجود.'}), 500

    output_dir = AUDIO_FOLDER if audio_only else VIDEO_FOLDER
    logging.info(f"Output directory set to: {output_dir}")
    temp_filename_pattern = os.path.join(output_dir, f"download_{secrets.token_hex(8)}.%(ext)s")

    try:
        ydl_opts = {
            'outtmpl': temp_filename_pattern, 'ffmpeg_location': ffmpeg_path,
            'quiet': True, 'no_warnings': True, 'encoding': 'utf-8',
            'noplaylist': True, 'noprogress': True,
            'postprocessor_args': {'ffmpeg': ['-v', 'error']},
            'format': None, 'socket_timeout': 30, 'retries': 3,
        }

        # --- التعديل: استخدام cookiesfrombrowser لـ Instagram في التحميل ---
        is_instagram = 'instagram.com' in url
        cookie_file_exists = os.path.exists(INSTAGRAM_COOKIE_PATH)

        if is_instagram:
            if cookie_file_exists:
                logging.info(f"Instagram URL detected for download. Using cookies from: {INSTAGRAM_COOKIE_PATH}")
                ydl_opts['cookiesfrombrowser'] = ('firefox', INSTAGRAM_COOKIE_PATH) # <-- التغيير هنا
            else:
                logging.error(f"Instagram URL detected for download but cookie file not found at {INSTAGRAM_COOKIE_PATH}.")
                return jsonify({'error': 'فشل التحميل من انستغرام، قد يتطلب الأمر كوكيز صالحة على الخادم.'}), 403
        # -----------------------------------------------------------

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
                # ... (باقي منطق العثور على الملف المحمل كما كان) ...
                filename_in_info = ydl.prepare_filename(info)
                if filename_in_info.lower().endswith(f'.{final_file_ext}') and os.path.exists(filename_in_info):
                    downloaded_file_path = filename_in_info
                else:
                    logging.warning(f"Filename from info ({filename_in_info}) doesn't match expected extension .{final_file_ext} or doesn't exist. Searching directory.")
                    list_of_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
                    if not list_of_files: raise FileNotFoundError("No files found in output directory after download attempt.")
                    possible_files = [f for f in list_of_files if f.lower().endswith(f'.{final_file_ext}')]
                    if possible_files: latest_file = max(possible_files, key=os.path.getctime); downloaded_file_path = latest_file
                    else: latest_file = max(list_of_files, key=os.path.getctime); logging.warning(f"Could not find file with extension .{final_file_ext}. Using latest file found: {latest_file}"); downloaded_file_path = latest_file
                if not downloaded_file_path or not os.path.exists(downloaded_file_path): raise FileNotFoundError(f"Could not determine or find the final downloaded file.")
                logging.info(f"Download successful. File path identified: {downloaded_file_path}")

            except youtube_dl.utils.DownloadError as e:
                 # ... (معالجة الأخطاء كما كانت) ...
                 logging.error(f"yt-dlp download/processing failed for {url}: {e}")
                 error_msg = 'فشل تنزيل أو معالجة الملف. قد يكون المحتوى محمياً، غير متاح بهذه الجودة، يتطلب كوكيز صالحة، أو تم الوصول لحد الطلبات.'
                 return jsonify({'error': error_msg}), 500
            except FileNotFoundError as e:
                 logging.error(f"File handling error after download for {url}: {e}")
                 return jsonify({'error': 'خطأ في التعامل مع الملفات بعد التنزيل.'}), 500
            except Exception as e:
                logging.error(f"Unexpected error during yt-dlp processing for {url}: {e}", exc_info=True)
                return jsonify({'error': 'حدث خطأ غير متوقع أثناء التنزيل.'}), 500

        final_output_path = downloaded_file_path

        if mode == 'trim' and info and (start_time != '0' or end_time):
            # ... (منطق القص يبقى كما هو) ...
            logging.info(f"Trimming requested: Start={start_time}s, End={end_time}s")
            video_duration = info.get('duration')
            try:
                start_sec = float(start_time)
                if video_duration is not None and start_sec >= video_duration:
                    logging.warning(f"Start time {start_sec}s >= duration {video_duration}s")
                    os.remove(downloaded_file_path)
                    return jsonify({'error': 'وقت البداية يتجاوز مدة الملف!'}), 400
                trim_opts = ['-ss', str(start_sec)]
                if end_time and end_time.strip():
                    end_sec = float(end_time)
                    if video_duration is not None and end_sec > video_duration: logging.warning(f"End time {end_sec}s > duration {video_duration}s. Trimming till end.")
                    elif end_sec <= start_sec: logging.warning(f"End time {end_sec}s <= start time {start_sec}s"); os.remove(downloaded_file_path); return jsonify({'error': 'وقت النهاية يجب أن يكون أكبر من وقت البداية!'}), 400
                    else: trim_opts.extend(['-to', str(end_sec)])
            except ValueError:
                 logging.warning("Invalid start/end time format for trimming."); os.remove(downloaded_file_path); return jsonify({'error': 'تنسيق وقت البداية أو النهاية غير صالح.'}), 400

            original_title = info.get('title', 'trimmed_file')
            safe_base_name = generate_safe_filename(original_title)
            base, ext = os.path.splitext(os.path.basename(downloaded_file_path))
            trimmed_filename = f"{safe_base_name}_{secrets.token_hex(4)}_trimmed{ext}"
            trimmed_output_path = os.path.join(output_dir, trimmed_filename)
            logging.info(f"Output path for trimmed file: {trimmed_output_path}")
            ffmpeg_cmd = [ffmpeg_path, '-v', 'error', '-i', downloaded_file_path, *trim_opts, '-c', 'copy', '-avoid_negative_ts', 'make_zero', '-y', trimmed_output_path]
            logging.info(f"Running FFmpeg trim command: {' '.join(ffmpeg_cmd)}")
            try:
                result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
                logging.info("FFmpeg trimming completed successfully.")
                if result.stderr: logging.warning(f"FFmpeg stderr (trim success): {result.stderr}")
                try: os.remove(downloaded_file_path); logging.info(f"Removed original untrimmed file: {downloaded_file_path}")
                except OSError as e: logging.warning(f"Could not remove original file {downloaded_file_path}: {e}")
                final_output_path = trimmed_output_path
            except subprocess.CalledProcessError as e:
                logging.error(f"FFmpeg trimming failed! Command: {' '.join(e.cmd)}. Stderr: {e.stderr}")
                if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path)
                if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                return jsonify({'error': 'فشل قص الملف. تحقق من الأوقات أو قد تكون الصيغة غير مدعومة للقص السريع.'}), 500
            except Exception as e:
                 logging.error(f"Unexpected error during trimming: {e}", exc_info=True)
                 if os.path.exists(downloaded_file_path): os.remove(downloaded_file_path)
                 if os.path.exists(trimmed_output_path): os.remove(trimmed_output_path)
                 return jsonify({'error': 'حدث خطأ غير متوقع أثناء قص الملف.'}), 500

        final_filename = os.path.basename(final_output_path)
        logging.info(f"Operation successful. Returning filename: {final_filename}")
        return jsonify({'success': True, 'filename': final_filename})

    except Exception as e:
        logging.error(f"Major error in /download endpoint for {url}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ عام أثناء عملية التنزيل. يرجى المحاولة مرة أخرى.'}), 500


# ... (باقي الكود download_file, internal_server_error, if __name__ == '__main__' يبقى كما هو) ...

@app.route('/downloads/<path:filename>')
def download_file(filename):
    logging.info(f"Received request to download file: {filename}")
    possible_folders = [AUDIO_FOLDER, VIDEO_FOLDER]
    found_path = None
    directory_to_serve_from = None

    for folder in possible_folders:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            abs_folder_path = os.path.abspath(folder)
            abs_file_path = os.path.abspath(file_path)
            if abs_file_path.startswith(abs_folder_path):
                found_path = file_path
                directory_to_serve_from = folder
                logging.info(f"File found in: {directory_to_serve_from}")
                break
            else:
                 logging.error(f"Security Alert: Attempt to access file outside allowed directory! Req: {filename}, Path: {abs_file_path}, Allowed: {abs_folder_path}")
                 return jsonify({'error': 'Access denied.'}), 403

    if not found_path:
        logging.error(f"File not found in any specified directory: {filename}")
        return jsonify({'error': 'الملف المطلوب غير موجود أو تم حذفه.'}), 404

    try:
        logging.info(f"Sending file: {filename} from directory: {directory_to_serve_from}")
        return send_from_directory(directory_to_serve_from, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error sending file {filename}: {e}", exc_info=True)
        return jsonify({'error': 'حدث خطأ أثناء إرسال الملف.'}), 500


@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error triggered: {e}", exc_info=True)
    return jsonify({'error': 'حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى لاحقًا.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask server on host 0.0.0.0, port {port}, debug=False")
    app.run(debug=False, host='0.0.0.0', port=port)