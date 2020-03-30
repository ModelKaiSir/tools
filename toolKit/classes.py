import os
import re
import zipfile as zip


class ReplaceTool:

    def __init__(self, suffix):

        self.__cache = {}
        self.suffix = "class" if suffix is None else suffix  # 默认文件后缀为class
        self.__zip_name_it = None
        pass

    def __get_classes(self, root_path, packages):
        # a.b.c.i,n,j
        # packages = [a.b.c.i, a.b.c.n, a.b.c.j]
        _result = []
        for package in packages:

            package_child = package.split(".")
            _path = "{}{}.{}".format(root_path, "\\".join(i for i in package_child), self.suffix)

            if os.path.isfile(_path):

                # 具体目录
                detail_path, last_name = "\\".join(i for i in package_child[:-1]), package_child[-1:]
                # 如果整个目录不是一个文件夹则lastName就是要查找的文件名
                _path = "{}{}".format(root_path, detail_path)

                for i in self.__find_file(_path, last_name[0]):
                    _result.append(i)
            else:

                # 查找所有文件
                for i in self.__find_file(_path, "", True):
                    _result.append(i)
                pass

        self.__pack_zip(_path.replace(root_path, "classes\\"), _path, _result)

        pass

    def __generate_zip_name(self):

        index = 0
        while True:
            result = "替换{}.zip".format(index if index > 0 else "")
            index += 1
            yield result
        pass

    def __generate_readme(self, code_path):

        readme_path = config['generate_zip_path'] + 'readMe.txt'

        with open(readme_path, 'a', encoding='utf-8') as file:
            file.writelines(config['comment'].format(path=code_path))

        return readme_path
        pass

    def __remove(self, file):

        try:

            os.remove(file)
        except FileNotFoundError:
            pass

        pass

    def __pack_zip(self, code_path, path, result):

        zip_name = next(self.__zip_name_it)
        zip_path = config['generate_zip_path'] + zip_name

        print(zip_path)
        self.__remove(zip_path)

        readme = self.__generate_readme(code_path)
        _folder = path.split("\\")[-1:][0]

        with zip.ZipFile(zip_path, "a") as z:
            for r in result:
                _F = "{}/{}".format(path, r[r.rfind("\\") + 1:])
                print("{}\\{}".format(_folder, r))
                z.write(_F, "{}\\{}".format(_folder, r), compress_type=zip.ZIP_DEFLATED)

        with zip.ZipFile(zip_path, "a") as z2:
            z2.write(readme, "path.txt", compress_type=zip.ZIP_DEFLATED)
            pass

        # 删除readme
        self.__remove(readme)
        pass

    def __find_file(self, root_path, file_name, find_all=False):

        regex = r'(' + file_name + ').*(\.' + self.suffix + ')$'
        # 读取path下面所有文件，并进行正则过滤
        for file in os.listdir(root_path):

            if os.path.isdir(file):
                for child in os.listdir(file):
                    self.__find_file(child, file_name, find_all)
            else:
                if find_all:
                    yield file
                elif re.match(regex, file) is not None:
                    yield file

        pass

    def zip(self, *args, **kwargs):

        """ 生成替换文件 *args代表需要查找的class包名 **kwargs代表项目路径 -pos-path = 手动输入 -pos = POS61 | POS65 为使用预设的路径"""
        try:
            path = config[kwargs.get("pos")] if kwargs.get("pos") is not None else kwargs.get("pos_path")

            self.__cache.update({path: args})
            return self
        except KeyError:
            print("找到不到{}的预设值。".format(kwargs.get("pos")))
            return self
        pass

    def __str__(self):

        self.__zip_name_it = self.__generate_zip_name()
        for k, v in self.__cache.items():

            for item in v:
                packages = []
                splits = item.split(".")
                if item.find(",") != -1:

                    prefix = ".".join(splits[:-1])
                    suffix = splits[-1]
                    packages = ["{}.{}".format(prefix, v) for v in suffix.split(",")]
                else:
                    packages.append(item)

                self.__get_classes(k, packages)

        return 'JobDone'


pass

config = None

if __name__ == '__main__':

    pass
