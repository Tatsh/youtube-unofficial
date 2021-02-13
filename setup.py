from setuptools import setup, find_packages

setup(name='youtube-unofficial',
      version='0.2.0',
      author='Andrew Udvare',
      author_email='audvare@gmail.com',
      packages=find_packages(),
      url='https://github.com/Tatsh/youtube-unofficial',
      license='LICENSE.txt',
      description='Access parts of your account unavailable through normal '
      'YouTube API access.',
      long_description='Access parts of your account unavailable through '
      'normal YouTube API access. Use at your own risk.',
      install_requires=('beautifulsoup4>=4.3.2', 'html5lib>=0.999',
                        'requests>=2.6.0'),
      python_requires='~=3.6',
      entry_points={
          'console_scripts':
          [('youtube-clear-history = youtube_unofficial.scripts:'
            'clear_watch_history'),
           ('youtube-clear-search-history = youtube_unofficial.scripts:'
            'clear_search_history'),
           ('youtube-clear-watch-later = youtube_unofficial.scripts:'
            'clear_watch_later'),
           ('youtube-toggle-search-history = youtube_unofficial.scripts:'
            'toggle_search_history'),
           ('youtube-toggle-watch-history = youtube_unofficial.scripts:'
            'toggle_watch_history'),
           ('youtube-print-watch-later-ids = youtube_unofficial.scripts:'
            'print_watchlater_ids'),
           ('youtube-print-playlist-ids = youtube_unofficial.scripts:'
            'print_playlist_ids'),
           ('youtube-remove-watch-later-setvideoid = youtube_unofficial.'
            'scripts:remove_watchlater_setvideoid'),
           ('youtube-remove-setvideoid = youtube_unofficial.'
            'scripts:remove_setvideoid'),
           ('youtube-print-history-ids = youtube_unofficial.'
            'scripts:print_history_ids'),
           ('youtube-remove-history-entries = youtube_unofficial.'
            'scripts:remove_history_entries'),
           'ytdl-history = youtube_unofficial.downloaders:download_history',
           ('ytdl-watch-later = youtube_unofficial.downloaders:'
            'download_watch_later'),
           'ytdl-playlist = youtube_unofficial.downloaders:download_playlist',
           'ytdl-liked = youtube_unofficial.downloaders:download_liked']
      })
