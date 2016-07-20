# tiroFinale
An <del>*INEFFICIENT*</del> (improved) and *INSECURE* python HTTP(S) proxy

The client-side program (*tiro*) requires OpenSSL and Python 3.x, and supports at least Windows and Linux.

The server-side program (*Finale*) requires Python 3.x, and supports at least [heroku](http://heroku.com) and MS Azure Web App.

![tirofinale](https://cloud.githubusercontent.com/assets/6646473/16940706/251b6fde-4dbe-11e6-9a1c-701e45aeb630.png)

[Official](http://bangumi.bilibili.com/anime/2539) Pronounciation: **踢咯，飞那里！**

## Demo

Windows binaries for tiro: [Releases](https://github.com/xmcp/tiroFinale/releases)

Finale server demo: `http://finale.herokuapp.com/finale` (password: `rdfzyjy`)

## Efficiency

Not using tiroFinale proxy: *LOAD: 3.46s*

![before](https://cloud.githubusercontent.com/assets/6646473/16955889/e033fc4c-4e08-11e6-9b18-f00bf75a5f50.png)

Using tiroFinale proxy (v2.5) from localhost: *LOAD: 4.95s*

![after](https://cloud.githubusercontent.com/assets/6646473/16955850/c6c0f666-4e08-11e6-9feb-7fd576c5cf44.png)


## Server (`finale`) Setup

1. Clone the repository, then `cd finale`
2. `python3 -m pip install -r requirements.txt`
3. `vi finale.py` and fill in your server's PASSWORD and PORT
4. `python3 ./finale.py`

## Client (`tiro`) Setup

1. Clone the repository, then `cd tiro`
2. `python3 -m pip install -r requirements.txt`
3. `vi ssl_config.py` and fill in your OpenSSL executable path (on Linux, just fill in `openssl`)
4. `vi finale_launcher.py` and fill in FINALE_URL and its PASSWORD
5. `python3 ./tiro_proxy.py`

## Todo-List

- [ ] Add GUI support for `tiro`
- [x] Fix the `Content-Length` related bug
- [x] Improve efficiency
- [x] Add `GFWList` support
- [x] Use wildcard SSL certificate if possible
- [ ] Network error handling and retransmission
- [ ] Showing statistics

## Special thanks to:

- [senko/tornado-proxy](https://github.com/senko/tornado-proxy)
- [python-simplecacher](https://github.com/Leryan/python-simplecacher)
- [Leryan/genssl](https://github.com/Leryan/genssl)
- [CaledoniaProject/GFWList](https://github.com/CaledoniaProject/GFWList)
