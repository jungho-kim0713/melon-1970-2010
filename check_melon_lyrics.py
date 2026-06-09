import urllib.request
import re

url = 'https://www.melon.com/song/detail.htm?songId=732512'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # Look for the lyrics element
        match = re.search(r'<div class="lyric" id="d_video_summary">(.*?)</div>', html, re.DOTALL)
        if match:
            lyrics_html = match.group(1)
            # Replace <br> tags and strip whitespace
            lyrics = re.sub(r'(?i)<br\s*/?>', '\n', lyrics_html)
            lyrics = re.sub(r'<[^>]+>', '', lyrics) # remove other tags
            lyrics = lyrics.strip()
            
            with open('f:\\Kim_Jungho\\jungho_webapp\\통.통.통 교사연구회\\lyrics_output.txt', 'w', encoding='utf-8') as f:
                f.write(lyrics)
            print('Lyrics saved to lyrics_output.txt')
except Exception as e:
    print('Error:', e)
