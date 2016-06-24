from distutils.core import setup

setup(
    name='youtube-unofficial',
    version='0.0.1',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=['youtube_unofficial'],
    url='https://github.com/Tatsh/youtube-unofficial',
    license='LICENSE.txt',
    description='Access parts of your account unavailable through normal '
                'YouTube API access.',
    long_description='Access parts of your account unavailable through '
                     'normal YouTube API access. Use at your own risk.',
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'html5lib>=0.999',
        'requests>=2.6.0',
        'six>=1.10.0',
    ],
    entry_points={
        'console_scripts': [
            ('youtube-clear-history = youtube_unofficial.scripts:'
             'clear_watch_history'),
        ]
    }
)