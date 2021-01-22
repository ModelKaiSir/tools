from setuptools import setup, find_packages

setup(
    name='tools',
    version='2.2.1',
    keywords='tools',

    url="None",
    author="qiuKai",
    author_email="None",
    description="TechTrans Development Tools",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",

    install_requires=['cx_Oracle>=7.3.0', 'pymssql','pywin32', 'qrcode', 'fire','progressbar', 'selenium'],
    # 添加这个选项，在windows下Python目录的scripts下生成exe文件
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        'tools = tools.__execute:run',
    ]},
    zip_safe=False
)
