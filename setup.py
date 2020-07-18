from setuptools import setup, find_packages

setup(
    name='tools',
    version='1.3',
    keywords='tools',

    url="None",
    author="qiuKai",
    author_email="None",
    description="TechTrans Development Tools",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",

    install_requires=['cx_Oracle>=7.3.0', 'pywin32', 'qrcode', 'fire',
                      'progressbar'],
    # 添加这个选项，在windows下Python目录的scripts下生成exe文件
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        'tools = tools.tools_run:main',
    ]},
    zip_safe=False
)
