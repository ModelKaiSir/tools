from tools import util


def readme(_message):
    readme_path = util.get_desktop_path() + '\\readme.txt'

    with open(readme_path, 'w', encoding='utf-8') as file:
        file.writelines(_message)

    return readme_path
    pass


def replace_class(*args, **kwargs):
    """
    生成class替换文件
    :param args 查找class的完整package路径
    """
    # to dir
    root = kwargs.get("root")
    package = None
    _group = {}
    for source in args:

        assert source is not None, "package is Null!"
        tags = source.split(".")
        if len(tags) == 1:
            assert package is not None, f"无效的包路径 {source}"
            package.append(source)
            tags = package

        dirs, name = tags[:-1], tags[-1]
        # save package
        package = dirs
        child = '\\'.join(dirs)
        root_path = f"{root}\\{child}"

        _files = util.find_file(root_path, name, "class")

        for _f in _files:
            _file_map = {_f: "\\".join(_f.parts[-2:])}
            _group.update({"\\".join(package): _file_map})

    # pack readme
    for _i, k in enumerate(_group):
        template = "{path}" if kwargs.get("template") is None else kwargs.get("template")
        _group.get(k).update({readme(template.format(path=k)): "readme.txt"})
        file_name = f"替换{_i}.zip" if _i != 0 else "替换.zip"
        util.pack_zip(*zip(_group.get(k).items()), path=util.get_desktop_path(), name=file_name)
    pass
