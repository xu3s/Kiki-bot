# std libs
import os
import io
import re
import imghdr
import zipfile
# import tempfile
import pathlib
import shutil

# 3rd party libs
from PIL import Image, JpegImagePlugin as jip
import filetype


bname = os.path.basename
splext = os.path.splitext

def natural_key(text):
    stoi = lambda t: int(t) if t.isdigit() else t
    return [stoi(c) for c in re.split(r'(\d+)', text)]

def stitch(images:list, vertical: bool = True, quality: int = 100,custname=None) -> io.BytesIO:
    """ Stitch images
    :images: list of file path or a file object
      The file object must implement file.read, file.seek
      and file.tell methods, and be opened in binary mode.
    :vertical[boolean]: True = vertical, False = horizontal.
      default: True
    :quality: integer value for image quality from 1-100
    """

    img_obj = {}
    width = []
    height = []
    # box = {'w':[],'h':[]}
    # im_mode = []
    misc ={'im_mode':[], 'im_format':[]}
    misc['im_format'] = [imghdr.what(im) for im in images]
    misc['im_format'] = max(misc['im_format'], key=misc['im_format'].count)

    # print(images)
    for img in images:
        if isinstance(img, str):
            file_name = os.path.splitext(img)[0]
        elif isinstance(img, (io.BytesIO, zipfile.ZipExtFile)):
            file_name = os.path.splitext(img.name)[0]
        else:
            continue
        img_obj[file_name] = Image.open(img)
        misc['im_mode'].append(img_obj[file_name].mode)
        width.append(img_obj[file_name].size[0])
        height.append(img_obj[file_name].size[1])

    if vertical:
        res_width, res_height = max(width), sum(height)
    else:
        res_width, res_height = sum(width), max(height)

    misc['im_mode'] = max(misc['im_mode'], key=misc['im_mode'].count)

    result = Image.new(misc['im_mode'], (res_width, res_height),
            color=(255, 255, 255) if misc['im_mode'] != 'L' else (255))
    start_val = 0
    for img in img_obj.values():
        result.paste(img, box=(0, start_val) if vertical else (start_val, 0))
        start_val = sum((start_val, img.size[1])) if vertical else sum(
            (start_val, img.size[0]))
    print(start_val)

    io_bytes = io.BytesIO()
    if custname:
        npath = list(img_obj.keys())[0]
        io_bytes.name = os.path.join(os.path.dirname(npath),
                'stitched', f'{custname}.{misc["im_format"]}')
    else:
        name_list = [os.path.join(os.path.dirname(p),
            'stitched', os.path.basename(p)) for p in img_obj]
        io_bytes.name = f'{name_list[0]}--{os.path.basename(name_list[-1])}.{misc["im_format"]}' if len(
                name_list) > 1 else f'{name_list[0]}.{misc["im_format"]}'
    result.save(io_bytes, format=misc['im_format'], quality=quality,
                    subsampling=jip.get_sampling(list(img_obj)[0]))
    io_bytes.seek(0)

    return io_bytes


def folder_stitch(path:pathlib.PurePath, **kwargs):
        # vertical:bool=True,max_stitch:int=3, quality:int=100, r:bool=False):
    '''Stitch image in folder.
    :param vertical[bool]: [True] stitch vertical or horizontal.
    :param max_stitch[int]: [3] max image to stitch.
    :param custom[list]: [None] custom list of file to stitch, it overides max_stitch.
    :param quality[int]: [100] image quality.
    :param r[bool]: [False] if specified it will stitch image recursively
        inside the folder
    '''
    vertical = kwargs.pop('vertical',True)
    max_stitch = kwargs.pop('max_stitch',3)
    custom = kwargs.pop('custom',None)
    quality = kwargs.pop('quality',100)
    r = kwargs.pop('r',False)

    path_content = sorted(os.listdir(os.path.abspath(path)), key=natural_key)
    # print(path_content)
    images = []

    for content in path_content:
        abspath = os.path.join(os.path.abspath(path), content)
        if os.path.isdir(abspath) and r:
            print(f'processing folder {abspath} because r is set to True')
            folder_stitch(abspath, vertical, max_stitch, quality, r)

        if os.path.isfile(abspath) and filetype.is_image(abspath):
        # content.endswith(('jpg','jpeg')):
            print(f'{content} added to list')
            images.append(abspath)

    print(f'{images}\n{len(images)}')
    if custom and len(images) > 1:
        for x in custom:
            result = stitch([img for img in images if splext(bname(img))[0] in x])
            os.makedirs(os.path.dirname(result.name),exist_ok=True)
            with open(result.name, 'wb') as f:
                f.write(result.getvalue())
            result.close()

    if not custom and len(images) > 1:
        for x in range(0, len(images), max_stitch):
            result = stitch(images[x:x+max_stitch])
            os.makedirs(os.path.dirname(result.name),exist_ok=True)
            with open(result.name, 'wb') as f:
                f.write(result.getvalue())
            result.close()
    if len(images) <= 1:
        if len(images) == 1:
            os.makedirs(f'{os.path.dirname(images[0])}/stitched',exist_ok=True)
            shutil.copy(images[0],
                    os.path.join(os.path.dirname(images[0]),'stitched',bname(images[0])))
        print('there is less than 1 image file detected so skipping it')


def zip_stitch(zfp, **kwargs):
    '''Stitch image in zipfile.
    :param vertical[bool]: [True] stitch vertical or horizontal.
    :param max_stitch[int]: [3] max image to stitch.
    :param custom[list]: [None] custom list of file to stitch, it overides max_stitch.
    :param quality[int]: [100] image quality.
    :param r[bool]: [False] if specified it will stitch image recursively
        inside the folder
    '''

    vertical = kwargs.pop('vertical',True)
    max_stitch = kwargs.pop('max_stitch',3)
    custom = kwargs.pop('custom',None)
    quality = kwargs.pop('quality',100)
    # r = kwargs.pop('r',False)
    zfl = kwargs.pop('zfl', get_zfl(zfp))

    with zipfile.ZipFile(zfp, 'a', zipfile.ZIP_DEFLATED) as zf:
        for fol in zfl.keys():
            images = zfl[fol]
            itername = 0
            if custom and len(images) > 1:
                for clist in custom.values():
                    for c in clist:
                        if not c:
                            continue
                        itername = f'{int(itername)+1:03d}'
                        result = stitch(
                                [zf.open(imp,'r') for imp in images if imp in c],
                                vertical=vertical, quality=quality, custname=itername)
                        zf.writestr(result.name, result.getvalue())

            elif not custom and len(images) > 1:
                for x in range(0, len(images), max_stitch):
                    itername = f'{int(itername)+1:03d}'
                    result = stitch(
                            [zf.open(imp,'r') for imp in images[x:x+max_stitch]],
                                vertical=vertical, quality=quality,
                                custname=itername)
                    zf.writestr(result.name, result.getvalue())
            elif len(images) <= 1:
                print('only 1 image or less found')



def get_zfl(zfp) -> dict:
    with zipfile.ZipFile(zfp,'r', zipfile.ZIP_DEFLATED) as zf:
        zfl = sorted([im.filename for im in zf.filelist if not im.is_dir()], key=natural_key)
        fol_list = []
        for im in zf.filelist:
            imd = os.path.dirname(im.filename)
            if imd in fol_list:
                continue
            fol_list.append(imd)
        fol_list.reverse()
        res = {}
        reres = []
        for fol in fol_list:
            res[fol] = []
            for file in zfl:
                if file.startswith(fol) and file not in reres and filetype.is_image(zf.open(file)):
                    res[fol].append(file)
            reres.extend(res[fol])

        return {x:res[x] for x in reversed(res.keys()) if res[x]}



def chan_gen(strnum):
    """ Generate chapter number from format 1,3-4,6
    or something like that
    :return: list of number [1,3,4,6]
    """
    strnum = str(strnum).strip().replace(' ', '')
    if "," in strnum:
        a = strnum.split(',')
    else:
        a = [strnum]
    result = []
    for x in a:
        if '-' in x:
            xr = x.split('-')
            for b in range(int(xr[0]), int(xr[1])+1):
                if str(b) not in result:
                    result.append(str(b))
            continue
        if str(x) not in result:
            result.append(str(x))
    return result

def analyzer(p, vertical:bool=True, max_stitch:int=3, quality:int=100, r:bool=False):
    """ Analyze the args
    """

    if isinstance(p, list):
        exists = sorted([d for d in p if os.path.exists(d)], key=natural_key)
        images = []
        link = [l for l in p if l not in exists] # we just assume that
        # the data in p that doesnt exist as link/url
        for data in exists:
            if os.path.isdir(data):
                folder_stitch(data, vertical, max_stitch, quality, r)

            if os.path.isfile(data) and data.endswith(('jpg','jpeg')):
                images.append(data)
            if zipfile.is_zipfile(data):
                zip_stitch(data)

        if link is not None:
            print(f'there is {len(link)} assumed link/url ignored')
        if len(images) > 1:
            image_stitch(images)

    if os.path.isdir(p):
        folder_stitch(p, vertical, max_stitch, quality, r)

    if zipfile.is_zipfile(p):
        zip_stitch(p, vertical, max_stitch, quality, r)
    else:
        print('unsupported yet!')



if __name__ == "__main__":

    print('its a module?')
