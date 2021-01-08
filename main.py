import fire
from tools import util
from tools.techtrans import clock
from tools.techtrans import format
import logging


class ToolsMenu:

    def clock(self, tag="JIANDAOYUN"):
        clock.clock(tag)

    pass

    def format_sql(self, **kwargs):

        path = kwargs["path"] if kwargs.get("path") else format.DEFAULT_HANDLE_PATH
        logger.debug(kwargs)
        logger.debug(path)

        if kwargs.get("copy"):

            logger.info("copy3333333")
            util.copy_text("".join(format.format_sql()))
        elif kwargs.get("override"):

            logger.info("override33333333333")
            with open(path, mode="w", encoding="utf-8") as w:
                w.writelines(format.format_sql(sql_path=path))
                pass

        pass


def run():
    fire.Fire(ToolsMenu)
    pass


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    ToolsMenu().format_sql(override=1)
