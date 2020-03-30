import pathlib
import string
import json
import time
import re

import urllib.request as request
import urllib.parse as parse

import configparser as parser
import progressbar as pbar


class LrcTools:

    def __init__(self, path):

        self.__path = path
        pass

    def __generate_compliant_file(self, _path: pathlib.Path):

        ''' 返回目录下符合条件的文件Path'''
        if _path.exists():
            # 同目录下对应的歌词文件
            patterns = ["**/*.flac", "**/*.mp3"]
            for pattern in patterns:

                for _file in _path.glob(pattern):

                    _file_lrc = _file.with_suffix(".lrc")
                    if not _file_lrc.exists():
                        yield _file_lrc
        pass

    def __generate_bgbar(self, title=""):

        return pbar.ProgressBar(widgets=[title, "[", pbar.Percentage(), pbar.Bar("▇"), "]"])

    def __request(self, url, data=None):

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://y.qq.com/portal/search.html",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/76.0.3809.100 Safari/537.36 "
        }

        _url = parse.quote_plus(url, safe=string.printable)
        _url = _url.replace("+", "%20")

        req = request.Request(url=_url, headers=headers)

        try:
            response = request.urlopen(req, data)
            return response
        except BaseException as e:
            print(e)
        pass

    def __query_sound_info(self, author, sound):

        result_json = self.__request(
            config['qq_music_api_url'].format(timetamp=int(float(time.time())), sound="{} {}".format(sound, author)))

        if result_json is not None:

            try:
                # 尝试将返回的数据解析成字符串
                json_text = result_json.read().decode("utf-8")
                json_text = json_text[json_text.find("{"): json_text.rfind("}") + 1]

                if bool(json_text and json_text.strip()):

                    data = json.loads(json_text)
                    for item in data["data"]["song"]["list"]:

                        signer, mid, name, title = item["singer"][0], item["mid"], item["name"], item["title"]

                        # 不要伴奏
                        if bool(re.match(".*(伴奏|demo|live)+", title)):
                            continue
                        if bool(title == sound or str(title).find(sound) != -1) and bool(
                                signer is None or str(signer["name"]).find(author) != -1):
                            return item

            except BaseException as e:

                print(e)
                return '-1'
                pass
        return '-1'
        pass

    def __download_lyric(self, path):

        file_name = re.sub(r"[0-9]|(.lrc)|(\.)", "", path.name)
        digest = file_name.split("-")

        if len(digest) > 1:
            author, sound = digest[0].strip(), digest[1].strip()
        else:
            author, sound = "", digest[0].strip()

        bar = self.__generate_bgbar("{} {}".format(author, sound))
        bar.start()
        bar.update(20)
        sound_info = self.__query_sound_info(author, sound)
        bar.update(30)

        if sound_info != '-1':
            data = self.__request(config["api_url"], data=parse.urlencode({"mid": sound_info["mid"]}).encode("UTF-8"))
            data = json.loads(json.load(data))
            bar.update(60)

            if data is not None:
                with open(path, 'wb') as file:
                    file.write(data["lrc"].encode('utf-8'))
                    pass
                bar.update(100)
            else:
                print("{} {} 没有找到歌词！".format(author, sound))
        else:
            print("{} {} 没有找到歌词！".format(author, sound))
        pass

    def list(self):

        '''显示需要下载歌词的歌曲列表'''
        iterable = self.__generate_compliant_file(pathlib.Path(self.__path))

        print("\n".join([str(i) for i in iterable]))
        return self
        pass

    def download(self):

        ''' 从输入的目录下查找没有歌词的歌曲，联网下载歌词。支持的格式（flac mp3）'''
        iterable = self.__generate_compliant_file(pathlib.Path(self.__path))
        self.__download(iterable)
        pass

    def __download(self, iterable):

        for file_path in iterable:
            self.__download_lyric(file_path)
        pass

    def __repair_sound(self, _sound, new_author):

        if bool(new_author and new_author.strip()):
            name = _sound.name
            name = name.replace(new_author, "").strip()
            new_name = "{} - {}".format(new_author, name)
            new_item = _sound.with_name(new_name)
            _sound.rename(new_item)

        return self
        pass

    def repair(self, author):

        self.__iterable = None
        '''修复歌曲正确的歌曲名称（作者 - 歌名），--author 歌曲作者 支持的歌曲格式 flac mp3 m4a'''
        source_dir = pathlib.Path(self.__path)
        patterns = ['**/*.flac', '**/*.mp3', '**/*.m4a']

        items = [item for item in [source_dir.glob(pattern) for pattern in patterns]]
        result = []

        for item in items:
            result.extend(item)

        bar = self.__generate_bgbar("Rename in ")

        for result_item in bar(result):

            if len(result_item.name.split(" - ")) <= 1:
                self.__repair_sound(result_item, author)

        return self

    pass

    def __str__(self):

        return 'jobDone'

    pass


pass

config = None

if __name__ == '__main__':

    config_path = pathlib.Path().cwd().joinpath("tools.ini")
    conn = parser.ConfigParser()
    conn.read(config_path, encoding='UTF-8')
    sections = conn.sections()

    config = dict(conn.items('lyricapi'))
    LrcTools('D:\Music\\test').list().repair('周杰伦').list().download()
    pass
