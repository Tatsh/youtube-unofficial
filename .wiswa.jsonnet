(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Access parts of your account unavailable through normal YouTube API access.',
  keywords: ['command line', 'youtube'],
  project_name: 'youtube-unofficial',
  version: '0.3.0',
  want_main: true,
  citation+: {
    'date-released': '2025-08-27',
  },
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
          'more-itertools': '^10.7.0',
          'yt-dlp-utils': '^0.0.5',
          beautifulsoup4: '^4.13.4',
          html5lib: '^1.1',
          requests: '2.32.3',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-beautifulsoup4': '>=4.12.0.20250204',
              'types-requests': '^2.31.0.20240106',
            },
          },
          tests+: {
            dependencies+: {
              'requests-mock': '^1.11.0',
            },
          },
        },
      },
    },
  },
  copilot: {
    intro: 'youtube-unofficial is a command line tool to access parts of your YouTube account that are not available through the normal YouTube API. It allows a user to manage subscriptions, playlists, and liked videos directly from the command line.',
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  social+: {
    mastodon+: { id: '109370961877277568' },
  },
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
