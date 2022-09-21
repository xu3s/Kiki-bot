import os
import dropbox
from dropbox import exceptions
from config import conf

dbx = dropbox.Dropbox(conf().DROPBOX_TOKEN)


def check_files(box_path) -> dict:
    """ get list of files from db
    :param box_path: path to the folder on dropbox
    :return: list of file(s) in the box_path
    """

    try:
        flist = dbx.files_list_folder(box_path).entries
        entries = [e.name for e in flist]
        status = 'ok'
        info = None
    except exceptions.ApiError as e:
        status = 'error'
        info = e.error
        entries = []
    return {
            'status': status,
            'entries': entries,
            'info': info
            }


def upload(path, box_path=None) -> dict:
    """ Upload file to dbx
    :param path: path to the file or folder to upload
    :param box_path: path to save in dropbox
    """

    print('Uploading...')
    # TODO: upload content from folder if path is directory
    if os.path.isdir(path):
        pass
    retry = 0
    while True:
        try:
            with open(path, 'rb') as f:
                fname = os.path.basename(f.name)
                if box_path:
                    box_path = os.path.join(box_path, fname)
                else:
                    box_path = os.path.join('/Unknown', fname)
                up = dbx.files_upload(f.read(), box_path,autorename=True)
                print('upload done!')
                return get_link(up.path_display)
        except exceptions.ApiError as e:
            if retry < 3:
                print(f'upload failed: {retry} time(s)')
                retry += 1
                continue
            return {'status': 'error',
                    'info': e.error
                    }


def get_link(box_path) -> dict:
    """get link for dbox file
    :param box_path: path to file in dropbox
    """
    try:
        link = dbx.sharing_create_shared_link(box_path)
        return {
                'status': 'ok',
                'name': os.path.basename(link.path),
                'url': link.url
                }
    except exceptions.ApiError as e:
        return {
                'status': 'error',
                'info': e.error
                }


def download(dbx_url, dl_path) -> dict:
    '''Download file from dropbox
    :param dbx_url: dropbox shared link
    :param dl_path: path to save in local
    '''

    try:
        link_meta = dbx.sharing_get_shared_link_metadata(dbx_url)
        file_name = link_meta.name
        print(file_name)
        fpath = os.path.join(dl_path,file_name)
        info = dbx.sharing_get_shared_link_file_to_file(fpath, dbx_url)
        status = 'ok'

    except exceptions.ApiError as e:
        status = 'error'
        info = e.error
        fpath = None
    return {
            'status': status,
            'fp': fpath,
            'info': info
            }

#def delete_batch(path):
#    entries =
#    dbx.files_delete_batch(entries)
