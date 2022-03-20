import os
import dropbox
from dropbox import exceptions
from config import conf

dbx = dropbox.Dropbox(conf().DROPBOX_TOKEN)

root = '/raws'

def check_files(box_path, with_root=False):
    """ get list of files from db
    :param box_path: path to the folder on dropbox
    :param with_root[bool]: wether the box_path include root folder default False
    :return: list of the file(s) on the box_path
    """

    if with_root:
        box_path_fol = box_path
    else:
        box_path_fol = os.path.join(root, box_path)
    try:
        flist = dbx.files_list_folder(box_path_fol).entries
        entries = [e.name for e in flist]
    except Exception as e: #pylint: disable= broad-except
        print(e)
        entries = []
    return entries


def upload(file_path, box_path=None, use_conf=True):
    """ Upload file to dbx
    :param file_path: path to the file to upload
    :param box_path: path to save in dropbox
    :param use_conf: wether to use default configuration or just box_path
    :return: url to file
    """

    print('Uploading...')
    with open(file_path, 'rb') as f:
        fname = os.path.basename(f.name)
        if use_conf and box_path:
            box_path = os.path.join(root, box_path, fname)
        elif box_path:
            box_path = os.path.join(box_path, fname)
        else:
            box_path = os.path.join('Unknown', fname)
        # box_path = os.path.join(root, series_title, f.name)
        up = dbx.files_upload(f.read(), box_path,autorename=True)
    print('upload done!')
    return get_link(up.path_display)
    # return {
    #         'file_name': os.path.basename(file_path),
    #         'url': get_link(box_path, is_folder=False)
    #         }


def get_link(box_path, use_conf=True, is_folder=False):
    """get link for dbox file
    :param box_path: path to file in dropbox
    :param use_conf[bool]: wether to use default conf
    :param is_folder[bool]: wether the box path is file or folder
    :return: url to the specified folder or file
    """
    if use_conf:
        box_path = os.path.join(root, box_path)
    if is_folder:
        link = dbx.sharing_create_shared_link(box_path).url
    else:
        link = dbx.sharing_create_shared_link(box_path).url
    return {'name': os.path.basename(box_path), 'url': link}


def download(dbx_url, dl_path):
    try:
        link_meta = dbx.sharing_get_shared_link_metadata(dbx_url)
        file_name = link_meta.name
        print(file_name)
        fpath = os.path.join(dl_path,file_name)
        info = dbx.sharing_get_shared_link_file_to_file(fpath, dbx_url)
        result = 'success'

    except exceptions.ApiError as e:
        result = 'error'
        print(e)
        info = e
        fpath = None
    return result, info, fpath
