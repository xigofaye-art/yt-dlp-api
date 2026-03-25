from flask import Flask, jsonify, request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing id parameter'}), 400

    url = f'https://www.youtube.com/watch?v={video_id}'

    for client in ['ios', 'tv_embedded', 'web_creator']:
        ydl_opts = {
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': [client],
                }
            },
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                if not video_url:
                    formats = info.get('formats', [])
                    for f in formats:
                        if f.get('ext') == 'mp4' and f.get('url'):
                            video_url = f['url']
                            break
                if video_url:
                    return jsonify({
                        'url': video_url,
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'client': client
                    })
        except Exception:
            continue

    return jsonify({'error': 'All clients failed to extract video URL'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

保存后等 Zeabur 自动重新部署（约 2 分钟），再测试：
```
https://faye0430.zeabur.app/download?id=EIIPbN4ZVG8
