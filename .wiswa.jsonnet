local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Access parts of your account unavailable through normal YouTube API access.',
  keywords: ['command line', 'youtube'],
  project_name: 'youtube-unofficial',
  version: '0.3.1',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.youtube-unofficial' },
  docs_conf+: {
    config+: {
      intersphinx_mapping+: {
        requests: ['https://requests.readthedocs.io/en/latest/', null],
      },
    },
  },
  security_policy_supported_versions: { '0.3.x': ':white_check_mark:' },
  tests_pyproject+: {
    tool+: {
      ruff+: {
        lint+: {
          'extend-ignore'+: ['RUF029'],
        },
      },
    },
  },
  flatpak+: { command: 'youtube' },
  snapcraft+: {
    apps+: {
      'youtube-unofficial'+: {
        command: 'bin/youtube',
      },
    },
  },
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
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          'more-itertools': utils.latestPypiPackageVersionCaret('more-itertools'),
          'yt-dlp-utils': {
            extras: ['asyncio'],
            version: utils.latestPypiPackageVersionCaret('yt-dlp-utils'),
          },
          beautifulsoup4: utils.latestPypiPackageVersionCaret('beautifulsoup4'),
          html5lib: utils.latestPypiPackageVersionCaret('html5lib'),
          'niquests-cache': utils.latestPypiPackageVersionCaret('niquests-cache'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-beautifulsoup4': utils.latestPypiPackageVersionCaret('types-beautifulsoup4'),
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
            },
          },
          tests+: {},
        },
      },
      uv+: {
        'exclude-newer-package'+: {
          'niquests-cache': false,
        },
      },
    },
  },
}
