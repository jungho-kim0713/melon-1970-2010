import urllib.request
import re
import json

# URL for the AJAX request that returns the chart list
list_url = 'https://www.melon.com/chart/age/list.htm?chartType=AG&chartGenre=KPOP&chartDate=1970'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

print("Fetching 1970s chart list...")
req = urllib.request.Request(list_url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # We need to extract: Song ID, Title, Artist
        # Usually inside:
        # <tr ...>
        # <div class="wrap_song_info">
        # <div class="ellipsis rank01"><span><a href="javascript:melon.play.playSong('1000002721',3054174);" title="새들처럼 재생">새들처럼</a></span></div>
        # <div class="ellipsis rank02"><a href="javascript:melon.link.goArtistDetail('1181');" title="송골매 - 페이지 이동">송골매</a></div>
        
        # A simpler way to get song id is to look for playSong('...', 'songId')
        # However, there can be multiple playSong calls.
        # Let's use regex to find the rows or the specific song structure.
        
        # Find all songIds using the goSongDetail or playSong
        # <a href="javascript:melon.link.goSongDetail('12345');"
        
        songs = []
        # Let's split by '<tr' to process each song row
        rows = html.split('<tr')[1:]
        
        for row in rows:
            # Extract song ID
            song_id_match = re.search(r'javascript:melon\.link\.goSongDetail\(\'(\d+)\'\)', row)
            if not song_id_match:
                continue
            song_id = song_id_match.group(1)
            
            # Extract title
            title_match = re.search(r'<div class="ellipsis rank01">.*?<a[^>]*>(.*?)</a>', row, re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Unknown"
            
            # Extract artist
            artist_match = re.search(r'<div class="ellipsis rank02">.*?<a[^>]*>(.*?)</a>', row, re.DOTALL)
            artist = artist_match.group(1).strip() if artist_match else "Unknown"
            
            # Remove HTML tags from title/artist just in case
            title = re.sub(r'<[^>]+>', '', title)
            artist = re.sub(r'<[^>]+>', '', artist)
            
            songs.append({
                'id': song_id,
                'title': title,
                'artist': artist
            })

        print(f"Found {len(songs)} songs.")
        
        # Let's fetch lyrics for the first 5 songs as a test
        results = []
        for song in songs[:5]:
            print(f"\nFetching lyrics for: {song['title']} - {song['artist']}")
            song_url = f"https://www.melon.com/song/detail.htm?songId={song['id']}"
            song_req = urllib.request.Request(song_url, headers=headers)
            
            try:
                with urllib.request.urlopen(song_req) as s_response:
                    s_html = s_response.read().decode('utf-8')
                    lyric_match = re.search(r'<div class="lyric" id="d_video_summary">(.*?)</div>', s_html, re.DOTALL)
                    
                    if lyric_match:
                        lyrics_html = lyric_match.group(1)
                        lyrics = re.sub(r'(?i)<br\s*/?>', '\n', lyrics_html)
                        lyrics = re.sub(r'<[^>]+>', '', lyrics)
                        lyrics = lyrics.strip()
                        song['lyrics'] = lyrics
                        print(f"-> Success! Length: {len(lyrics)}")
                    else:
                        song['lyrics'] = "Lyrics not found"
                        print("-> Lyrics not found")
            except Exception as e:
                print(f"-> Error fetching lyrics: {e}")
                song['lyrics'] = "Error"
                
            results.append(song)
            
        # Save to file
        with open('f:\\Kim_Jungho\\jungho_webapp\\통.통.통 교사연구회\\1970s_songs.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print("\nSaved first 5 songs to 1970s_songs.json")

except Exception as e:
    print('Error:', e)
