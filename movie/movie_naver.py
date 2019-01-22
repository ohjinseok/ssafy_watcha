# 영진위에서 얻은 영화명을 바탕으로 
# 네이버 영화 검색 API를 통해 추가 데이터 수집
# 요청 : 영화명
# 영진위 영화 대표코드, 영화 썸네일 이미지의 URL, 하이퍼텍스트 link, 유저 평점
# movie_naver.csv 저장

import requests, os, csv, shutil

url = "https://openapi.naver.com/v1/search/movie.json"
naverCId = os.getenv("NAVER_CID")
naverCS = os.getenv("NAVER_CS")
# url + query={}

headers = {
        "X-Naver-Client-Id": naverCId,
        "X-Naver-Client-Secret": naverCS
}

def get_movie_naver(movieNm):
    res = requests.get(f"{url}?query={movieNm}", headers=headers)
    movieNaver = res.json().get('items')[0]
    return movieNaver

def saveCsvMN(movieNaver):
    movieCd = get_movieCd(movieNaver)
    exists = os.path.exists('movie_naver.csv')

    if exists:
        with open('movie_naver.csv', 'r', newline='', encoding = 'utf-8') as csvfile:
            csvReader = csv.DictReader(csvfile)
            data = [row for row in csvReader]
        
    with open('movie_naver.csv', 'w', newline='', encoding = 'utf-8') as csvfile:
        fieldnames = ['movie_code', 'image_url', 'htlink', 'rate']
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvWriter.writeheader()
        for row in data:
                csvWriter.writerow(row)
        csvWriter.writerow({'movie_code': movieCd, 'image_url': movieNaver['image'], 'htlink': movieNaver['link'], 'rate': movieNaver['userRating']})

def get_image(movieNaver):
    res = requests.get(movieNaver['image'], stream=True)
    movieCd = get_movieCd(movieNaver)
    with open(f'../image/{movieCd}.jpg', 'wb') as f:
        shutil.copyfileobj(res.raw, f)

def get_movieCd(movieNaver):
    movieCd = ""
    with open('movie.csv', 'r', encoding = 'utf-8') as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            if row['movie_name_ko'] == movieNaver['title'][3:-4]:
                movieCd = row['movie_code']
    return movieCd

def get_naver_csv():
    movie_list = []
    with open('boxoffice.csv', 'r', newline='', encoding = 'utf-8') as csvfile:
        csvReader = csv.DictReader(csvfile)
        movie_list = [row['title'] for row in csvReader]

    for i in movie_list:
        saveCsvMN(get_movie_naver(i))
        get_image(get_movie_naver(i))

if __name__ == '__main__':
    get_naver_csv()