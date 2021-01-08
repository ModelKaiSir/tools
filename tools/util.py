import win32api
import win32con
import win32clipboard as clip
import zipfile as zip
import os
import logging


def get_desktop_path() -> str:
    """return System Desktop Path"""
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders', 0,
                              win32con.KEY_READ)
    return win32api.RegQueryValueEx(key, 'Desktop')[0]


def copy_text(text):
    """COPY TEXT TO CLIPBOARD"""
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardText(text)
    clip.CloseClipboard()


def copy_file(file):
    """COPY FILE TO CLIPBOARD"""
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(win32con.CF_DIF, file)
    clip.CloseClipboard()


def pack_zip(*args, **kwargs):
    def remove(_zip_path):

        try:

            logger.info(f"remove exists file {_zip_path}")
            os.remove(_zip_path)
        except FileNotFoundError as _e:

            logger.error(_e, exc_info=1)
            pass
        pass

    """打包到zip kwargs: 
    name 压缩包名
    path 压缩包存放路径
    args 打包的内容 ((path, dir), (path, dir) ...)"""
    try:

        zip_path = fr"{kwargs['path']}\{kwargs['name']}"

        logger.info(f"package zip to {zip_path}")

        exists = os.path.exists(zip_path)
        remove(zip_path) if exists else None

        with zip.ZipFile(zip_path, "a") as z:

            for arg in args:
                for p, d in arg:
                    z.write(p, d, compress_type=zip.ZIP_DEFLATED)
    except BaseException as e:

        logger.error(e, exc_info=1)
        pass
    pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    readme_path = get_desktop_path() + "\\" + 'test.txt'

    with open(readme_path, 'a', encoding='utf-8') as file:
        file.writelines("test")

    pack_zip(((readme_path, "test.txt"), (readme_path, "a\\test.txt")), path=get_desktop_path(), name="test.zip")
    pass
