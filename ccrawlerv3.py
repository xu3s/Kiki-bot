import os
import shutil
import tempfile
# import gofileio
from worker import create_worker
from comiccrawler.mission import Mission
from comiccrawler.analyzer import Analyzer
from comiccrawler.crawler import download
import uptobox


def safe_download(mission,savepath):
    err = None
    def target():
        try:
            download(mission, savepath)
        except Exception as e:
            nonlocal err
            err = e
    w = create_worker(target,parent=False)
    w.start()
    w.join()
    if err:
        raise err

class Manga:
    ''' Manga'''
    def __init__(self,url):
        self.url = url
        self.mission = Mission(url=url)

    def manga(self):
        try:
            Analyzer(self.mission).analyze()
            print(self.mission.title)
        except Exception as e: # pylint: disable=broad-except
            print(f'failed in parsing url: {self.url}')
            print(e)
            return f'''
Failed to parse {self.url}, Please check the url or check if the site is supported!'''
        return None


    def mdownload(self, to_dl:list):
        self.mission:Mission

        cf = uptobox.check_files(os.path.join('/raws',self.mission.title))
        if cf['status'] == 'ok':
            dbx_files = cf['entries']
        else:
            print(f'error \n{cf["info"]}')
            dbx_files = cf['entries']

        init_state = self.mission.state
        for ep in self.mission.episodes:
            ep.skip = True
        for n, ep in enumerate(self.mission.episodes, 0):
            if n in to_dl and f'{ep.title}.zip' not in dbx_files:
                ep.skip = False
                with tempfile.TemporaryDirectory() as tempdir:
                    print(f'tempdir: {tempdir}')
                    try:
                        safe_download(self.mission, tempdir)
                    except Exception as e:
                        print(f'download exception: {e}\n\n')
                        yield {
                                'status': 'error',
                                'info': f'error while downloading {ep.title}({n})'
                                }
                        continue
                    shutil.make_archive(os.path.join(tempdir,ep.title),
                            'zip',
                            os.path.join(tempdir,self.mission.title))

                    uped = uptobox.upload(
                            os.path.join(tempdir,
                            f'{ep.title}.zip'),
                            box_path=os.path.join(
                                '/raws', self.mission.title))
                    yield uped
                ep.skip = True
                self.mission.state = init_state

            elif n in to_dl and f'{ep.title}.zip' in dbx_files:
                ugl = uptobox.get_link(os.path.join(
                    '/raws',
                    self.mission.title,
                    f'{ep.title}.zip'
                    ))
                yield ugl
