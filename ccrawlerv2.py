import os
import sys
# import asyncio
import shutil
import tempfile
# import gofileio
import uptobox
from comiccrawler.mission import Mission
from comiccrawler.analyzer import Analyzer
from comiccrawler.crawler import download


class Manga:
    ''' Manga'''
    def __init__(self,ctx=None):
        self.mission = None
        self.ctx = ctx

    def manga(self, url):
        try:
            self.mission = Mission(url=url)
            Analyzer(self.mission).analyze()
            print(self.mission.title)
            # print(self.mission.episodes)
        except Exception as e: # pylint: disable=broad-except
            print(f'failed in parsing url: {url}')
            print(e)
            return f'Failed to parse {url}, Please check the url or check if the site is supported!'
        return None


    def mdownload(self, chapter):

        try:
            dbx_files = uptobox.check_files(self.mission.title)
        except Exception as e:#pylint: disable= broad-except
            print('no file or folder ???\n',e)
            dbx_files = []

        init_state = self.mission.state
        for ep in self.mission.episodes:
            ep.skip = True
        for n, ep in enumerate(self.mission.episodes, 0):
            # for c in chapter:
            if n in chapter and f'{ep.title}.zip' not in dbx_files:
                ep.skip = False

                with tempfile.TemporaryDirectory() as tempdir:
                    try:
                        download(self.mission, tempdir)

                        for chf in os.listdir(tempdir):
                            print(chf)
                            tempzip = os.path.join(tempdir,ep.title)
                            shutil.make_archive(
                                    tempzip, 'zip',
                                    os.path.join(tempdir,chf))
                            print(os.listdir(os.path.join(tempdir, chf)))
                        print(os.listdir(tempdir))
                        if os.path.exists(f'{tempzip}.zip'):
                            retry = 0
                            while True:
                                try:
                                    uped = uptobox.upload(
                                        f'{tempzip}.zip',
                                        box_path=self.mission.title)
                                    dlink = f'File Name: {uped["name"]}\nDownload Url: {uped["url"]}'
                                    break

                                except Exception as e:
                                    print(f'ripper error attemp {retry}: {e}')
                                    if retry >= 5:
                                        dlink = {
                                                'status': 'error',
                                                'error': e,
                                                'info': f'Failed in uploading to dropbox ({ep.title})'
                                                }
                                        break
                                    retry += 1

                            # fjson = asyncio.run(gofileio.upload(f'{tempzip}.zip'))
                            # if fjson['status'] == 'ok':
                            #     dlink = f"File Name: {fjson['filename']}\nDownload Page: {fjson['dl_page']}\nDirect link: {fjson['direct_dl']}" # pylint: disable=C0301
                            # else:
                            #     dlink = fjson
                    except Exception as e: #pylint: disable=broad-except
                        print(e)
                        print(f'download failed: {ep.title}')
                        dlink = {
                                'status': 'error',
                                'error': e,
                                'info': f'Failed to download {ep.title}'
                                }

                ep.skip = True
                self.mission.state = init_state
                yield dlink

            elif n in chapter and f'{ep.title}.zip' in dbx_files:
                ugl = uptobox.get_link(os.path.join(
                    self.mission.title,
                    f'{ep.title}.zip'
                    ))
                yield f'File Name: {ugl["name"]}\nDownload Url: {ugl["url"]}'

if __name__ == '__main__':
    link = 'https://manga.bilibili.com/detail/mc29562?from=manga_index'
    print(Manga().manga(link))
