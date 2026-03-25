from flask import Flask, jsonify, request
import yt_dlp
import os
import traceback

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing id parameter'}), 400

    url = f'https://www.youtube.com/shorts/{video_id}'

    clients = ['ios', 'android_vr', 'tv_embedded']

    for client in clients:
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': [client],
                    }
                },
            }
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
                if video_url:
                    return jsonify({
                        'url': video_url,
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'client': client
                    })
        except Exception:
            continue

    return jsonify({'error': 'Could not extract video URL from any client'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
