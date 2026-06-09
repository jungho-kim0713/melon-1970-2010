import urllib.request
import re

url = 'https://www.melon.com/chart/age/index.htm?chartType=AG&chartGenre=KPOP&chartDate=1960'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        matches = re.findall(r'javascript:melon\.link\.goSongDetail\(\'(\d+)\'\)', html)
        
        if matches:
            print('Found song IDs! Count:', len(matches))
            print('First 10:', matches[:10])
            
            titles = re.findall(r'<div class="ellipsis rank01">.*?<a[^>]*>(.*?)</a>', html, re.DOTALL)
            print('Found titles! Count:', len(titles))
            for i in range(min(5, len(titles))):
                print(f'{matches[i] if i < len(matches) else "?"} : {titles[i].strip()}')
        else:
            print('No song IDs found. The list might be loaded via AJAX.')
            
            # Let's search for any AJAX URLs in the HTML
            ajax_urls = re.findall(r'/chart/age/list\.htm\?[^\"\']*', html)
            if ajax_urls:
                print('Found AJAX URLs:')
                print(ajax_urls[:5])
            
except Exception as e:
    print('Error:', e)
