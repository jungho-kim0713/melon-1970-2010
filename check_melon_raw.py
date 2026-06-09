import urllib.request

url = 'https://www.melon.com/chart/age/list.htm?chartType=AG&chartGenre=KPOP&chartDate=1970'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        with open('f:\\Kim_Jungho\\jungho_webapp\\통.통.통 교사연구회\\1970_raw.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Length:", len(html))
        print("First 500 chars:", html[:500])
except Exception as e:
    print('Error:', e)
