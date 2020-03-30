import re


def format_sqL_safesttr():
    return "/", "--"
    pass


def check_sttr(sttr):
    safe_sttrs = format_sqL_safesttr()
    for _sttr in safe_sttrs:

        if _sttr == sttr or sttr.startswith(_sttr):
            return True

    return False


def format_sql():
    sql_data_file = r"D:\Developments\Document\sqlDatas.txt"
    sql = None
    with open(sql_data_file, encoding='utf-8') as file:
        sql = "".join(file.readlines())
        pass

    if sql is not None:

        _result = re.split(r"(\n)(\n)", sql)
        should_breakline = lambda k: k if k == "" else "\n"

        for _sql in _result:
            if _sql == '\n' and len(_sql) <= 1:
                continue

            if not check_sttr(_sql):
                print("/*<SQL>*/{}{}{}/*</SQL>*/".format(should_breakline(_sql[0]), _sql, should_breakline(_sql[-1])))
            else:
                print(_sql)
    pass


format_sql()
