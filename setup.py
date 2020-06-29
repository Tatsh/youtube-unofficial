from setuptools import setup

setup(name='youtube-unofficial',
      version='0.2.0',
      author='Andrew Udvare',
      author_email='audvare@gmail.com',
      packages=('youtube_unofficial', ),
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
           ('youtube-clear-favorites = youtube_unofficial.scripts:'
            'clear_favorites'),
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
           ('youtube-remove-history-entry = youtube_unofficial.'
            'scripts:remove_history_entry')]
      })
