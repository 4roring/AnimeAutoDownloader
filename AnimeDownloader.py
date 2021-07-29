import os
import feedparser
import time
import yaml
from requests import get as http_get
from qbittorrent import Client
from plexapi.server import PlexServer


def plex_sync():
    plex_url = "http://127.0.0.1:32400/"
    token = '4pp_Jz3uyK7LXZwVdgCR'
    plex = PlexServer(plex_url, token)
    movie = plex.library.section('영화')
    movie.update()
    print('Plex Server Sync Complete')


def download(download_url: str, download_path: str):
    torrent_url = 'http://127.0.0.1:8080/'
    torrent_id = '4roring'
    torrent_pwd = ''

    # QBTorrent

    qb = Client(torrent_url)
    qb.login(torrent_id, torrent_pwd)

    response = http_get(download_url)

    qb.download_from_file(response.content, savepath=download_path)

    # 다운로드 상태 체크 (Polling)
    while True:
        qb_main_data = qb.sync_main_data()

        time.sleep(1)

        torrents: dict = qb_main_data['torrents']
        if not torrents:
            break

        for hash_key, torrent in torrents.items():
            current_state = torrent['state']
            if 'completed' == current_state or 'stalledUP' == current_state:
                qb.delete([hash_key])
                break

        time.sleep(3.0)

    # 자막 다운로드


if __name__ == '__main__':
    with open('getter_arc.yaml', 'r') as file:
        down_info = yaml.load(file, Loader=yaml.FullLoader)
        print(down_info)

    keyword = down_info['keyword']
    quality = ''
    episode_num = str(down_info['episode']).zfill(2)
    download_name = down_info['download_name'].format(episode_num)
    download_path = down_info['download_path']

    url = f'https://nyaa.si/?page=rss&q={keyword}&c=0_0&f=0'

    # keyword = 'tensei+slime'
    # download_name = '[SSA] Tensei shitara Slime Datta Ken - {} [1080p]'.format(episode_num)
    # download_name = '[Erai-raws] Digimon Adventure (2020) - {}'.format(episode_num)

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    d = feedparser.parse(url)
    for e in d.entries:
        if -1 == e.title.find(download_name):
            continue

        if quality and -1 == e.title.find(quality):
            continue

        print('download title = ', e.title)
        download(e.link, download_path)
        break

    plex_sync()
