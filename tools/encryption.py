import hashlib


def md5(*args, **kwargs):
    """
    md5加密
    :param args 加密内容
    :param kwargs 配置
    """
    r = {}
    for _input in args:
        generate = hashlib.md5()

        if kwargs.get("File"):
            with open(_input, mode='rb') as file:

                for line in file:
                    generate.update(line)
                pass

            r.update({_input: generate.hexdigest()})

        else:
            generate.update(_input.encode('UTF-8'))
            r.update({_input: generate.hexdigest()})

    return r
    pass

# content
# print(md5("test1", "test2"))
# file
# print(md5("D:/LOCAL_SQL.txt", File=1))
