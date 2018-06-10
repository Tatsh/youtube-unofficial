# New way to edit playlists

`POST https://www.youtube.com/service_ajax?name=playlistEditEndpoint`

headers:

```
x-spf-previous: https://www.youtube.com/playlist?list=LIST ID
x-spf-referer: https://www.youtube.com/playlist?list=LIST ID
x-youtube-client-name: 1
x-youtube-client-version: 2.20180313
x-youtube-identity-token: base64 string
x-youtube-page-cl: numeric
x-youtube-page-label: youtube.ytfe.desktop_20180312_10_RC1
x-youtube-variants-checksum: b73691560cc45174815c326ccc08a0ee
```

data:

```
sej: {"clickTrackingParams":"base64 string","commandMetadata":{"webCommandMetadata":{"url":"/service_ajax","sendPost":true}},"playlistEditEndpoint":{"playlistId":"playlist ID","actions":[{"setVideoId":"[A-F0-9]+","action":"ACTION_REMOVE_VIDEO"}],"params":"CAE%3D","clientActions":[{"playlistRemoveVideosAction":{"setVideoIds":["[A-F0-9]+"]}}]}}
csn: comes from window.getPageData().data.csn
session_token: base64 string
```

# `sej`


```yaml
clickTrackingParams: base64 string
commandMetadata:
    webCommandMetadata:
        url: /service_ajax
        sendPost: true
playlistEditEndpoint:
    playlistId: playlist ID
    actions:
        - setVideoId: ??
          action: ACTION_REMOVE_VIDEO
    params: CAE%3D ??
    clientActions:
        - playlistRemoveVideosAction:
            setVideoIds: [] same as actions[].setVideoIds above
```

`onTap_` in `desktop_polyer.js` -> `this.data.serviceEndpoint`
`sendServiceRequestAction(a)` in `desktop_polymer.js`
`requestDataForServiceEndPoint(a, b)` in `desktop_polymer.js`

Parse `window['ytInitialData']` JSON. Has the setVideoId values (first page only?)
