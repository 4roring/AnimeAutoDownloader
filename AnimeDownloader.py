import os
import feedparser
import time
from requests import get as http_get
from qbittorrent import Client
from plexapi.server import PlexServer


def plex_sync():
    plex_url = "http://127.0.0.1:32400/"
    token = '4pp_Jz3uyK7LXZwVdgCR'
    plex = PlexServer(plex_url, token)
    movie = plex.library.section('영화')
    movie.update()


def download(download_url: str, download_path: str):
    torrent_url = 'http://127.0.0.1:8080/'
    torrent_id = '4roring'
    torrent_pwd = ''

    qb = Client(torrent_url)
    qb.login(torrent_id, torrent_pwd)

    response = http_get(download_url)

    qb.download_from_file(response.content, savepath=download_path)

    # 다운로드 상태 체크 (Polling)
    while True:
        qb_main_data = qb.sync_main_data()

        for torrent_info in qb_main_data['torrents']:
            if not 'downloading' == torrent_info['state']:
                break

        time.sleep(3.0)


    # 다운로드 완료 후 공유 삭제
    # 자막 다운로드


if __name__ == '__main__':
    url = 'https://nyaa.si/?page=rss&q=kamen+rider&c=0_0&f=0'
    episode_num = '36'
    # download_name = '[Erai-raws] SSSS.Dynazenon - {}'.format(episode_num)
    download_name = '[Hikounin-Raws] Kamen Rider Saber - {}'.format(episode_num)
    quality = ''

    download_path = 'D:/Movie/Kamen Rider Saber'

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    d = feedparser.parse(url)
    for e in d.entries:
        if -1 == e.title.find(download_name):
            continue

        if quality and -1 == e.title.find(quality):
            continue

        print('download title = ', e.title)
        # download(e.link, download_path)
        break

    plex_sync()
