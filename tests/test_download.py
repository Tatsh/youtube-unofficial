from __future__ import annotations

from typing import TYPE_CHECKING, cast

from youtube_unofficial.download import download_page
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    import niquests


@pytest.mark.anyio
async def test_download_page_text(mocker: MockerFixture) -> None:
    mock_resp = mocker.MagicMock()
    mock_resp.text = '  <html></html>  '
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_session = mocker.AsyncMock()
    mock_session.headers = {'User-Agent': 'test'}
    mock_session.request.return_value = mock_resp
    sess = cast('niquests.AsyncSession', mock_session)
    result = await download_page(sess, 'https://example.com', return_json=False)
    assert result == '<html></html>'
    mock_session.request.assert_called_once()


@pytest.mark.anyio
async def test_download_page_text_empty(mocker: MockerFixture) -> None:
    mock_resp = mocker.MagicMock()
    mock_resp.text = None
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_session = mocker.AsyncMock()
    mock_session.headers = {}
    mock_session.request.return_value = mock_resp
    sess = cast('niquests.AsyncSession', mock_session)
    result = await download_page(sess, 'https://example.com', return_json=False)
    assert not result


@pytest.mark.anyio
async def test_download_page_json(mocker: MockerFixture) -> None:
    expected = {'key': 'value'}
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = expected
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_session = mocker.AsyncMock()
    mock_session.headers = {}
    mock_session.request.return_value = mock_resp
    sess = cast('niquests.AsyncSession', mock_session)
    result = await download_page(sess, 'https://example.com', return_json=True)
    assert result == expected


@pytest.mark.anyio
async def test_download_page_merges_headers(mocker: MockerFixture) -> None:
    mock_resp = mocker.MagicMock()
    mock_resp.text = 'ok'
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_session = mocker.AsyncMock()
    mock_session.headers = {'Accept-Encoding': 'gzip', 'User-Agent': 'test'}
    mock_session.request.return_value = mock_resp
    sess = cast('niquests.AsyncSession', mock_session)
    await download_page(sess, 'https://example.com', return_json=False, headers={'X-Custom': 'val'})
    call_kwargs = mock_session.request.call_args
    passed_headers = call_kwargs.kwargs['headers']
    assert 'Accept-Encoding' not in passed_headers
    assert passed_headers['X-Custom'] == 'val'
    assert passed_headers['User-Agent'] == 'test'
