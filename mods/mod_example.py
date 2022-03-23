"""
This is an example to show how to write a comiccrawler module.

"""

import re
from urllib.parse import urljoin
from comiccrawler.episode import Episode

# The header used in grabber method. Optional.
header = {}

# The cookies. Optional.
cookie = {}

# Match domain. Support sub-domain, which means "example.com" will match
# "*.example.com"
domain = ["www.example.com", "comic.example.com"]

# Module name
name = "Example"

# With noepfolder = True, Comic Crawler won't generate subfolder for each
# episode. Optional, default to False.
noepfolder = False

# If False then setup the referer header automatically to mimic browser behavior.
# If True then disable this behavior.
# Default: False
no_referer = True

# Wait 5 seconds before downloading another image. Optional, default to 0.
rest = 5

# Wait 5 seconds before analyzing the next page in the analyzer. Optional,
# default to 0.
rest_analyze = 5

# User settings which could be modified from setting.ini. The keys are
# case-sensitive.
#
# After loading the module, the config dictionary would be converted into
# a ConfigParser section data object so you can e.g. call
# config.getboolean("use_large_image") directly.
#
# Optional.
config = {
    # The config value can only be str
    "use_largest_image": "true",

    # These special config starting with `cookie__` will be automatically
    # used when grabbing html or image.
    "cookie_user": "user-default-value",
    "cookie_hash": "hash-default-value"
}

def load_config():
    """This function will be called each time the config reloads. Optional.
    """
    pass

def get_title(html, url):
    """Return mission title.

    The title would be used in saving filepath, so be sure to avoid
    duplicated title.
    """
    return re.search("<h1 id='title'>(.+?)</h1>", html).group(1)

def get_episodes(html, url):
    """Return episode list.

    The episode list should be sorted by date, oldest first.
    If is a multi-page list, specify the URL of the next page in
    get_next_page. Comic Crawler would grab the next page and call this
    function again.
    """
    match_list = re.findall("<a href='(.+?)'>(.+?)</a>", html)
    return [Episode(title, urljoin(url, ep_url))
            for ep_url, title in match_list]

def get_images(html, url):
    """Get the URL of all images.

    The return value could be:

    -  A list of image.
    -  A generator yielding image.
    -  An image, when there is only one image on the current page.

    Comic Crawler treats following types as an image:

    -  str - the URL of the image
    -  callable - return a URL when called
    -  comiccrawler.core.Image - use it to provide customized filename.

    While receiving the value, it is converted to an Image instance. See ``comiccrawler.core.Image.create()``.

    If the episode has multi-pages, uses get_next_page to change page.

    Use generator in caution! If the generator raises any error between
    two images, next call to the generator will always result in
    StopIteration, which means that Comic Crawler will think it had crawled
    all images and navigate to next page. If you have to call grabhtml()
    for each image (i.e. it may raise HTTPError), use a list of
    callback instead!
    """
    return re.findall("<img src='(.+?)'>", html)

def get_next_page(html, url):
    """Return the URL of the next page."""
    match = re.search("<a id='nextpage' href='(.+?)'>next</a>", html)
    if match:
        return match.group(1)

def redirecthandler(response, crawler):
    """Downloader will call this hook if redirect happens during downloading
    an image. Sometimes services redirects users to an unexpected URL. You
    can check it here.
    """
    if response.url.endswith("404.jpg"):
        raise Exception("Something went wrong")

def errorhandler(error, crawler):
    """Downloader will call errorhandler if there is an error happened when
    downloading image. Normally you can just ignore this function.
    """
    pass

def imagehandler(ext, b):
    """If this function exists, Comic Crawler will call it before writing
    the image to disk. This allow the module to modify the image after
    the download.

    @ext  str, file extension, including ".". (e.g. ".jpg")
    @b    The bytes object of the image.

    It should return a (modified_ext, modified_b) tuple.
    """
    return (ext, b)

def grabhandler(grab_method, url, **kwargs):
    """Called when the crawler is going to make a web request. Use this hook
    to override the default grabber behavior.

    @grab_method  function, could be ``grabhtml`` or ``grabimg``.
    @url          str, request URL.
    @kwargs       other arguments that will be passed to grabber.

    By returning ``None``
    """
    if "/api/" in URL:
        kwargs["headers"] = {"some-api-header": "some-value"}
        return grab_method(url, **kwargs)
