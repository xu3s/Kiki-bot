import re
from urllib.parse import urljoin
from html import unescape
from comiccrawler.episode import Episode

domain = ['www.baozimh.com', 'www.webmota.com']
name = "Baozimh"


def get_title(html,url):
    return re.search('<h1 class="comics-detail__title"(.+?)>(.+?)</h1>',html).group(2)


def get_episodes(html,url):

    episodes = re.findall('<a href="/user/page_direct?(.+?)"(.+?)class="comics-chapters__item(.+?)>(.+?)<span(.+?)>(.+?)</span></div></a></div>',html)
    episodes.reverse()
    result = []
    for ep in episodes:
        ep_title = ep[5]
        if ep_title in [x.title for x in result]:
            continue
        ep_url = urljoin(url,f'/user/page_direct{unescape(ep[0])}')
        result.append(Episode(title=ep_title,
            url=ep_url))
    result.reverse()
    return result


def get_images(html,url):

    imgs = [img[0] for img in re.findall('<noscript><img src="(.+?)" alt=(.+?)></noscript>', html)]
    return imgs
