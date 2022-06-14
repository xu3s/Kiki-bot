import re
from urllib.parse import urljoin
from html import unescape
from comiccrawler.episode import Episode
from bs4 import BeautifulSoup as bsoup

domain = ['www.baozimh.com', 'www.webmota.com']
name = "Baozimh"


def get_title(html,url):
    base = bsoup(html, 'html.parser')
    title = base.find('h1',class_='comics-detail__title').text
    return title
    # return re.search('<h1 class="comics-detail__title"(.+?)>(.+?)</h1>',html).group(2)


def get_episodes(html,url):

    base = bsoup(html, 'html.parser')
    episodes = base.find_all('a', class_='comics-chapters__item')
    episodes.reverse()
    result = []
    for ep in episodes:
        ep_title = ep.text
        if ep_title in [x.title for x in result]:
            continue
        ep_url = urljoin(url,ep['href'])
        result.append(Episode(
            title=ep_title,
            url=ep_url))
    result.reverse()
    return result

    # COMMENT THIS OUT FOR FUTURE REFERENCE
    # ____________________
    # episodes = re.findall('<a href="/user/page_direct?(.+?)"(.+?)class="comics-chapters__item(.+?)>(.+?)<span(.+?)>(.+?)</span></div></a></div>',html)
    # episodes.reverse()
    # result = []
    # for ep in episodes:
    #     ep_title = ep[5]
    #     if ep_title in [x.title for x in result]:
    #         continue
    #     ep_url = urljoin(url,f'/user/page_direct{unescape(ep[0])}')
    #     result.append(Episode(title=ep_title,
    #         url=ep_url))
    # result.reverse()
    # return result


def get_images(html,url):

    base = bsoup(html, 'html.parser')
    imgs = base.find_all('amp-img', class_='comic-contain__item')
    # imgs = [img[0] for img in re.findall('<noscript><img src="(.+?)" alt=(.+?)></noscript>', html)]
    return [img['src'] for img in imgs]

def debug(file):

    with open(file) as f:
        html = f.read()

    print(get_images(html=html, url='url'))

if __name__ == '__main__':
    debug('test/baoziimg-14-06-2022.html')
