
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

