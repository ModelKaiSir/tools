import hashlib


class EncryptedTool:

    def __init__(self):
        self.result = dict()
        pass

    def md5(self, *args, **kwargs):

        ''' 支持计算多个
        默认对输入的字符串进行计算MD5
        --File标识输入的为文件地址 将对文件进行计算md5 '''
        for item in args:

            generate = hashlib.md5()

            if kwargs.get("File"):
                with open(item, mode='rb') as file:

                    for line in file:
                        generate.update(line)
                    pass

                self.result.update({item: generate.hexdigest()})

            else:
                generate.update(item.encode('UTF-8'))
                self.result.update({item: generate.hexdigest()})

        return self
        pass

    def __str__(self):

        for k, v in self.result.items():
            print("{} : {}".format(k, v))

        Util.copy_text("\n".join(["{} : {}".format(k, v) for k, v in self.result.items()]))
        return "copy success"

    pass


pass

Util = None
