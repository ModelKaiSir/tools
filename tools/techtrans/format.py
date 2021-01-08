import re
from tools import util

DEFAULT_HANDLE_PATH = util.get_desktop_path() + r"\sql.txt"


def format_sql(sql_path=DEFAULT_HANDLE_PATH):
    """格式化sql脚本, 某些安全字符不会格式化，比如 / -- GO
    :param sql_path 默认为桌面的sql.txt"""
    safe_str = ["/", "--", "GO", "\n"]

    def check_str(_str):

        for s in safe_str:

            if s.lower() == _str.lower() or _str.startswith(s):
                return True

        return False
        pass

    def get_sql(_sql_lines):

        r = []
        for l in _sql_lines:

            if check_str(l):
                if len(r) == 0:
                    yield l
                else:
                    yield "".join(r)
                    r.clear()
            else:
                r.append(l)

        yield "".join(r)

    def breaks(_k):

        if _k == "":
            return _k
        else:
            return "\n"

    r = []
    with open(sql_path, encoding='utf-8') as file:

        for _sql in get_sql(file.readlines()):

            if _sql != "":

                __sql = _sql.strip()
                if check_str(__sql):
                    r.append(__sql)
                else:
                    k = __sql[0]
                    r.append(f"/*<SQL>*/{breaks(k)}{_sql.strip()}{breaks(k)}/*</SQL>*/")
        pass

    return r
    pass


if __name__ == '__main__':
    format_sql()
