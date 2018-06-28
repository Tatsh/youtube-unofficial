from setuptools import setup

setup(
    name='youtube-unofficial',
    version='0.1.0',
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
        'youtube-dl>=2017.7.9',
    ],
    entry_points={
        'console_scripts': [
            ('youtube-clear-history = youtube_unofficial.scripts:'
             'clear_watch_history'),
            ('youtube-clear-watch-later = youtube_unofficial.scripts:'
             'clear_watch_later'),
            ('youtube-clear-favorites = youtube_unofficial.scripts:'
             'clear_favorites'),
        ]
    }
)
