from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests
from fake_useragent import UserAgent
from lxml import etree
import codecs

# 唱片抽象類別
class Album(ABC):
 
    def __init__(self, item):
        self.item = item  # 傳入值 第一次為歌手 第二次為歌曲字串
 
    @abstractmethod
    def get_albums_dic(self):
        pass
    def get_song_list(self):
        pass
    def get_the_best_albums(self):
        pass


class Discogs(Album):
    def get_albums_dic(self):
        page_q = 1
        herf_lst = []
        main_dic = {}

        # make a fake user
        ua = UserAgent()
        headers = {'User-Agent': ua.random }
        
        # search_url = 'https://www.discogs.com/search/?limit=100&q=' + self.singer + '&type=release'
        # resp = requests.get(search_url, headers= headers)
        # soup = BeautifulSoup(resp.content,"html.parser")

        
        url = 'https://www.discogs.com/search/?q=' + self.item + '&type=release'
        resp = requests.get(url, headers= headers)
        soup = BeautifulSoup(resp.content,"html.parser")

        # get herf for each albums
        for a in soup.find_all('a',class_='search_result_title' ,href= True):
            herf_lst.append(a['href'])


        # # get all songs in each albums and save in main_dic
        for i in herf_lst:
            value = []
            try:
                album_url = 'https://www.discogs.com/' + i
                resp = requests.get(album_url, headers= headers)
                soup = BeautifulSoup(resp.content,"html.parser")
                dom = etree.HTML(str(soup))
                date = soup.find('time')
                if date == None:
                    date='None'
                else:
                    date = date['datetime']
                key = dom.xpath('//*[@id="page"]/div[1]/div[2]/div/h1//text()')[-1] + '-' + date

                for a in soup.find_all('span', class_='trackTitle_CTKp4'):
                    value.append(a.text)

                main_dic[key] = value
            except:
                pass
       
        return main_dic 

    def get_song_list(self, main_dic, songs_lst=[]):
        for i, v in main_dic.items():
            for song in v:
                if song not in songs_lst:
                    songs_lst.append(song)
        
        songs_lst = '⭐️ 歌曲清單如下:'+ '\n\n' +'\n'.join(songs_lst[:30]) +'\n\n' +'上面是我們為你列出一些知名歌曲\n當然也可以輸入其他你想要的歌曲😉'
    
        return songs_lst
    
    
    def get_the_best_albums(self, main_dic):
        count = []
        best_albums = []
        input_lst = self.item.split()
        max_indexes = []
        for i, v in main_dic.items():
            common_elements_len = len(set(input_lst).intersection(set(v)))
            count.append(common_elements_len)
        max_value = max(count)
        
        if max_value == 0:
            best_albums = ' 😖我們找不到你輸入的歌曲\n 請重新再試一次'
        else:
            for i, value in enumerate(count):
                if value == max_value:
                    max_indexes.append(i)
            for i in max_indexes:
                best_album = list(main_dic.keys())[i]
                best_albums.append(best_album)
            best_albums = '✨我們為你推薦的專輯如下:'+ '\n' +'\n' + '\n'.join(best_albums)
        return best_albums

