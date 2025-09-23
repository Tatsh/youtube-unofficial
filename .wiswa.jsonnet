local utils = import 'utils.libjsonnet';

{
  description: 'Access parts of your account unavailable through normal YouTube API access.',
  keywords: ['command line', 'youtube'],
  project_name: 'youtube-unofficial',
  version: '0.3.0',
  want_main: true,
  docs_conf+: {
    config+: {
      intersphinx_mapping+: {
        requests: ['https://requests.readthedocs.io/en/latest/', null],
      },
    },
  },
  security_policy_supported_versions: { '0.3.x': ':white_check_mark:' },
  pyproject+: {
    project+: {
      scripts: {
        youtube: 'youtube_unofficial.main:main',
      },
    },
    tool+: {
      local coverage_omit = [
        '*/typing/*.py',
        '__main__.py',
        'conftest.py',
        'tests.py',
        'tests/client/test_*.py',
        'tests/test_*.py',
      ],
      coverage+: {
        report+: {
          omit: coverage_omit,
        },
        run+: {
          omit: coverage_omit,
        },
      },
      poetry+: {
        dependencies+: {
          'more-itertools': utils.latestPypiPackageVersionCaret('more-itertools'),
          'yt-dlp-utils': utils.latestPypiPackageVersionCaret('yt-dlp-utils'),
          beautifulsoup4: utils.latestPypiPackageVersionCaret('beautifulsoup4'),
          html5lib: utils.latestPypiPackageVersionCaret('html5lib'),
          requests: utils.latestPypiPackageVersionCaret('requests'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-beautifulsoup4': utils.latestPypiPackageVersionCaret('types-beautifulsoup4'),
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
            },
          },
          tests+: {
            dependencies+: {
              'requests-mock': utils.latestPypiPackageVersionCaret('requests-mock'),
            },
          },
        },
      },
    },
  },
  copilot+: {
    intro: 'youtube-unofficial is a command line tool to access parts of your YouTube account that are not available through the normal YouTube API. It allows a user to manage subscriptions, playlists, and liked videos directly from the command line.',
  },
}
