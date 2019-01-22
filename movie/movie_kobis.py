import requests, os, csv, datetime

# date = yyyymmdd
# api request URL + key=~~&targetDt=date&weekGb=0

kobis_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest"
kobis_key = os.getenv("KOBIS_KEY")

def getMovieInfo(movieCd):
    res = requests.get(f"{kobis_url}/movie/searchMovieInfo.json?key={kobis_key}&movieCd={movieCd}")
    movieInfo = res.json().get('movieInfoResult').get('movieInfo')
    return movieInfo

def getWeeklyBO(targetDt):
    res = requests.get(f"{kobis_url}/boxoffice/searchWeeklyBoxOfficeList.json?key={kobis_key}&targetDt={targetDt}&weekGb=0")
    BOlist = res.json().get('boxOfficeResult').get('weeklyBoxOfficeList')
    return BOlist

def saveCsvInfo(movie):
    genres = [genre['genreNm'] for genre in movie['genres']]
    actors = []
    for i in range(3):
        if(len(movie['actors']) < i + 1):
            actors.append('')
        else:
            actors.append(movie['actors'][i]['peopleNm'])

    data = []
    exists = os.path.exists('movie.csv')
    if exists:
        with open('movie.csv', 'r', newline='', encoding = 'utf-8') as csvfile:
            csvReader = csv.DictReader(csvfile)
            data = [row for row in csvReader]
  
    with open('movie.csv', 'w', newline = '', encoding = 'utf-8') as csvfile:
        fieldnames = ['movie_code', 'movie_name_ko', 'movie_name_en', 'movie_name_og', 'prdt_year', 'genres', 'directors', 'watch_grade_nm', 'actor1', 'actor2', 'actor3']
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvWriter.writeheader()
        for row in data:
            csvWriter.writerow(row)
 
        csvWriter.writerow({'movie_code': movie['movieCd'], 'movie_name_ko': movie['movieNm'], 'movie_name_en': movie['movieNmEn'], 'movie_name_og': movie['movieNmOg'],
        'prdt_year': movie['openDt'][0:4], 'genres': '/'.join(genres), 'directors': movie['directors'][0]['peopleNm'],'watch_grade_nm': movie['audits'][0]['watchGradeNm'], 
        'actor1': actors[0], 'actor2': actors[1], 'actor3': actors[2]})   

def saveCsvBO(BOlist, targetDt):
    data = []
    exists = os.path.exists('boxoffice.csv')
    if exists:
        with open('boxoffice.csv', 'r', newline='', encoding = 'utf-8') as csvfile:
            csvReader = csv.DictReader(csvfile)
            movie_list = [movie['movieCd'] for movie in BOlist]
            data = [row for row in csvReader if not row['movie_code'] in movie_list]

    with open('boxoffice.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['movie_code', 'title', 'audience', 'recorded_at']
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvWriter.writeheader()
        for row in data:
            csvWriter.writerow(row)
        for movie in BOlist:
            csvWriter.writerow({'movie_code': movie['movieCd'], 'title': movie['movieNm'], 'audience': movie['audiAcc'], 'recorded_at': targetDt})

def get_10weeks(targetDt):
    for i in range(1, 11):
        date = datetime.datetime.strptime(targetDt,"%Y%m%d")
        date = date - datetime.timedelta(days=70-7*i)
        bolist = getWeeklyBO(date.strftime("%Y%m%d"))
        saveCsvBO(bolist, date.strftime("%Y%m%d"))

def info_10weeks():
    movie_list = []
    with open('boxoffice.csv', 'r', newline='', encoding = 'utf-8') as csvfile:
        csvReader = csv.DictReader(csvfile)
        movie_list = [row['movie_code'] for row in csvReader]

    for i in movie_list:
        saveCsvInfo(getMovieInfo(i))

if __name__ == '__main__':
    get_10weeks('20190113')
    info_10weeks()