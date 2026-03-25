from flask import Flask, jsonify, request
import yt_dlp
import os

app = Flask(__name__)

COOKIES_FILE = '/app/cookies.txt'

@app.route('/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing id parameter'}), 400

    url = f'https://www.youtube.com/watch?v={video_id}'

    ydl_opts = {
        'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'cookiefile': COOKIES_FILE,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            video_url = None
            for f in sorted(formats, key=lambda x: x.get('height') or 0, reverse=True):
                if f.get('ext') == 'mp4' and f.get('url') and f.get('height'):
                    video_url = f['url']
                    break
            if not video_url:
                video_url = info.get('url')
            return jsonify({
                'url': video_url,
                'title': info.get('title'),
                'duration': info.get('duration')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
