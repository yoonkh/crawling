
import requests
from bs4 import BeautifulSoup
import urllib.request

url_naver_webtoon_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
url_naver_webtoon_view_page = 'http://comic.naver.com/webtoon/detail.nhn'


def params_webtoon_episode_list(id, page):
    return {'titleId': id, 'page': page}


def params_webtoon_view_page(id, epi_num):
    return {'titleId': id, 'no': epi_num}


def get_html_from_url(url, params):
    '''해당 url주소 웹페이지의 HTML 태그를 텍스트로 반환'''
    response = requests.get(url, params=params)
    return (response.text)


class NaverWebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.all_episode_list = crawl_episode_page(self.webtoon_id, 1, 50)

    def crawl_page(self, page_num):
        episode_list = crawl_episode_page(self.webtoon_id, page_num, page_num)
        page_episode_list = []
        print('=========={}페이지 리스트=========='.format(str(page_num)))
        for episode in episode_list:
            episode.show_info
            page_episode_list.append(episode.title)
        print('')
        return page_episode_list

    def crawl_episode(self, episode_num=None):
        all_episode_list = self.all_episode_list
        if not episode_num:
            print('==========최신화 정보==========')
            all_episode_list[len(all_episode_list) - 1].show_info
            print(all_episode_list[len(all_episode_list) - 1].show_link)
            print('')
            return all_episode_list[len(all_episode_list) - 1].show_link
        print('=========={}화 정보=========='.format(episode_num))
        all_episode_list[episode_num - 1].show_info
        print(all_episode_list[episode_num - 1].show_link)
        print('')

    def crawl_all_episodes(self):
        all_episode_list = self.all_episode_list
        print('==========전체 리스트==========')
        for episode in all_episode_list:
            episode.show_info
        print('')
        return all_episode_list

    def crawl_episode_img(self, episode_num):
        crawl_img_list = episode_image_url(self.webtoon_id, episode_num)
        return crawl_img_list

    def save_episode_img(self, episode_num):
        save_image(self.webtoon_id, episode_num)


class Episode:
    def __init__(self, thumbnail, title, link, rating, date):
        self.thumbnail = thumbnail
        self.__title = title
        self.link = link
        self.rating = rating
        self.date = date

    @property
    def show_info(self):
        print('[ 제목:  {} ]  [ 평점:  {}  ]  [ 날짜:  {} ]'.format(self.title, self.rating, self.date))
        return [self.title, self.rating, self.date]

    @property
    def show_link(self):
        return ('http://comic.naver.com/'+self.link)

    @property
    def title(self):
        return self.__title

        # @property
        # def open(self):
        #     open self.show_link


def crawl_episode_page(id, a, b): # 웹툰 id와 파싱할 페이지 시작/끝 번호를 받아 episode class 인스턴스를 리스트에 넣어 반환
    episode_list = []  # 전체 episode class instance를 저장하기 위해 list 생성(초기화)
    cur_page_episode_list = []  # 해당 페이지에 있는 만화 정보를 episode class instance로 생성해 저장할 list 생성(초기화)

    for page_num in range(a, b + 1):  # a~b 페이지까지 순환
        html = get_html_from_url(url_naver_webtoon_episode_list, params_webtoon_episode_list(id, page_num))

        soup = BeautifulSoup(html, 'html.parser')
        table_view_list = soup.find('table', class_="viewList")
        table_view_list_tr = table_view_list.find_all('tr')

        before_cur_page_episode_list = cur_page_episode_list  # 다음 페이지로 넘어오면, cur_page_episode에는 전 페이지의 list가 남는다. 따라서 비교를 위해 before로 옮겨준다.
        cur_page_episode_list = []  # 다음 페이지로 넘어오면, cur_page_episode_list를 초기화시킨다.

        for episode in table_view_list_tr:
            if not episode.find('td', class_='title'):
                continue
            table_view_list_tr_episode = episode
            table_view_list_tr_episode_thumbnail = table_view_list_tr_episode.img['src']
            table_view_list_tr_episode_title = table_view_list_tr_episode.find('td', class_="title").a.text
            table_view_list_tr_episode_link = table_view_list_tr_episode.find('td', class_="title").a['href']
            table_view_list_tr_episode_rating = table_view_list_tr_episode.find('div', class_="rating_type").find(
                'strong').text
            table_view_list_tr_episode_num = table_view_list_tr_episode.find('td', class_="num").text
            cur_page_episode_list.extend([Episode(table_view_list_tr_episode_thumbnail, table_view_list_tr_episode_title,
                                                  table_view_list_tr_episode_link, table_view_list_tr_episode_rating,
                                                  table_view_list_tr_episode_num)])
            # print(cur_page_episode_list)

        if not page_num == a:  # 페이지 번호가 시작번호인 경우 페이지의 리스트를 비교할 before_cur_page_episode_list가 비어있기때문에 비교하지않는다.
            if not before_cur_page_episode_list[0].title == cur_page_episode_list[0].title:
                episode_list.extend(
                    cur_page_episode_list)  # 이전 페이지 첫 화의 제목과 이번 페이지 첫 화의 제목이 같지 않으면 cur_page_episode_list를 episode_list에 반환

            else:  # 이전 페이지 첫 화의 제목과 이번 페이지 첫 화의 제목이 같으면 cur_page_episode_list를 episode_list에 추가하지않고 break
                break
        else:
            episode_list.extend(cur_page_episode_list)  # 첫페이지의 리스트는 비교대상이 없으므로 바로 episode_list에 넣어준다

    episode_list.reverse()  # 모은 리스트를 1화가 앞이 오도록 정렬
    return episode_list


def episode_image_url(id, no):
    view_html = get_html_from_url(url_naver_webtoon_view_page, params_webtoon_view_page(id, no))
    soup = BeautifulSoup(view_html, 'html.parser')
    div_viewer = soup.find('div', class_="wt_viewer")
    img_url_tag = div_viewer.find_all('img')
    img_url_list = []
    for img_url in img_url_tag:
        img_url_list.append(img_url['src'])
    return img_url_list


def save_image(id, no):
    img_url_list = episode_image_url(id, no)
    img_num = 0
    for img_url in img_url_list:
        urllib.request.urlretrieve(
            img_url,
            "webtoon/{}_{}_{}.jpg".format(id, no, img_num))
        img_num += 1


gongnumman = NaverWebtoonCrawler('678499')  # 크롤러 class 인스턴스 생성
gongnumman.crawl_page(5) # 5페이지 리스트 출력
gongnumman.crawl_episode() #몇화인지 입력하지 않은 경우 최신화 정보 출력
gongnumman.crawl_episode(37) # 37화 정보 출력
gongnumman.crawl_all_episodes() # 전체 리스트 출력
print(gongnumman.crawl_episode_img(37)) # 37화 이미지 출력
# gongnumman.save_episode_img(37) #37화 이미지 저장