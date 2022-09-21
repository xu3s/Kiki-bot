

from comiccrawler.episode import Episode

domain = ['kuaikan.com']
name = 'Kuaikan grabber'
rest_analyzer = 5


def get_title(html, url):
    pass

def grabhandler(grab_method, url, **kwargs):

    if grab_method.__name__ == 'grabhtml':

