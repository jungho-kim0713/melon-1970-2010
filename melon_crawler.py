import sys
import io
import time
import json
import csv
import urllib.request
import os
from bs4 import BeautifulSoup

# 콘솔 출력 시 인코딩 문제 방지 및 실시간 출력(line_buffering) 적용
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 수집할 연대 설정 (1970년대 ~ 2010년대) - 2020년대는 멜론 연대별(AG) 차트 미제공으로 제외
DECADES = [1970, 1980, 1990, 2000, 2010]
CSV_FILENAME = 'melon_all_decades_lyrics.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def load_existing_progress(filepath):
    """기존 수집된 CSV 파일에서 성공한 가사 데이터를 불러옵니다."""
    existing_lyrics = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lyrics = row.get('lyrics', '').strip()
                    # 수집 실패했거나 내용이 없는 경우는 제외 (다시 수집해야 하므로)
                    if lyrics and "수집 실패" not in lyrics:
                        existing_lyrics[row['id']] = lyrics
        except Exception as e:
            print(f"기존 파일 읽기 오류: {e}")
    return existing_lyrics

def get_chart_list(decade):
    """특정 연대의 멜론 K-POP 차트 100곡 목록을 가져옵니다."""
    url = f'https://www.melon.com/chart/age/list.htm?chartType=AG&chartGenre=KPOP&chartDate={decade}'
    req = urllib.request.Request(url, headers=HEADERS)
    
    songs = []
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            rows = soup.find_all('tr')
            for row in rows:
                checkbox = row.find('input', {'name': 'input_check'})
                if not checkbox: continue
                
                song_id = checkbox.get('value')
                if not song_id: continue
                    
                title_div = row.find('div', class_='ellipsis rank01')
                title_a = title_div.find('a') if title_div else None
                title = title_a.get_text(strip=True) if title_a else "Unknown"
                
                artist_div = row.find('div', class_='ellipsis rank02')
                artist_a = artist_div.find('a') if artist_div else None
                artist = artist_a.get_text(strip=True) if artist_a else "Unknown"
                
                songs.append({
                    'decade': decade,
                    'id': song_id,
                    'title': title,
                    'artist': artist,
                    'lyrics': ""
                })
    except Exception as e:
        print(f"차트 목록 가져오기 에러 ({decade}년대): {e}")
        
    return songs

def get_lyrics(song_id):
    """song_id를 기반으로 멜론 곡 상세 페이지에서 가사를 추출합니다."""
    url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
    req = urllib.request.Request(url, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            lyrics_div = soup.find('div', id='d_video_summary')
            if lyrics_div:
                # <br> 태그를 실제 줄바꿈(\n)으로 변경
                for br in lyrics_div.find_all('br'):
                    br.replace_with('\n')
                lyrics = lyrics_div.get_text().strip()
                return lyrics
            return "가사 없음"
    except urllib.error.HTTPError as e:
        if e.code == 406:
            print(f"  -> [차단됨] 멜론 서버에서 IP를 임시 차단했습니다 (406 오류).")
        else:
            print(f"  -> HTTP 오류 (ID: {song_id}): {e}")
        return "수집 실패"
    except Exception as e:
        print(f"  -> 가사 가져오기 에러 (ID: {song_id}): {e}")
        return "수집 실패"

def main():
    print("멜론 연대별 가사 크롤링을 시작합니다...")
    
    # 1. 기존 진행 상황 불러오기
    existing_lyrics = load_existing_progress(CSV_FILENAME)
    if existing_lyrics:
        print(f"✅ 기존에 성공적으로 수집된 {len(existing_lyrics)}곡의 가사를 확인했습니다. 이어서 수집합니다.")
    else:
        print("새로운 수집을 시작합니다.")
        
    all_results = []
    
    for decade in DECADES:
        print(f"\n[{decade}년대] 차트 목록 확인 중...")
        songs = get_chart_list(decade)
        
        for i, song in enumerate(songs):
            song_id = song['id']
            
            # 2. 이미 수집된 곡이면 스킵하고 기존 데이터 사용
            if song_id in existing_lyrics:
                print(f"[{decade}년대 {i+1}/{len(songs)}] 이미 수집됨: {song['title']} - {song['artist']}")
                song['lyrics'] = existing_lyrics[song_id]
            else:
                # 새로운 곡인 경우에만 멜론 서버에 요청
                print(f"[{decade}년대 {i+1}/{len(songs)}] 새 가사 수집 중: {song['title']} - {song['artist']}")
                song['lyrics'] = get_lyrics(song_id)
                
                # 수집이 실패(406 등)했다면 그 곡까지만 저장하고 중단 여부를 고민할 수도 있으나
                # 일단 끝까지 진행하도록 둡니다.
                
                # 서버 과부하 및 차단 방지를 위한 딜레이를 5초로 증가
                time.sleep(5)
            
            all_results.append(song)
            
        # 연대별 중간 저장 (JSON)
        decade_filename = f'melon_{decade}s_lyrics.json'
        with open(decade_filename, 'w', encoding='utf-8') as f:
            json.dump(songs, f, ensure_ascii=False, indent=2)
            
        # 매 연대가 끝날 때마다 전체 CSV도 업데이트 (수집 중 중단되어도 저장되도록)
        with open(CSV_FILENAME, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['decade', 'id', 'title', 'artist', 'lyrics']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
            
        # 전체 JSON 파일도 업데이트
        json_filename = CSV_FILENAME.replace('.csv', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
            
    print("\n모든 수집 프로세스가 완료되었습니다!")
    print(f"최종 데이터: {CSV_FILENAME}")

if __name__ == "__main__":
    main()
