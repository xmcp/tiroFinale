# tiroFinale
An INEFFICIENT and INSECURE python HTTP(S) proxy

![tirofinale](https://cloud.githubusercontent.com/assets/6646473/16940706/251b6fde-4dbe-11e6-9a1c-701e45aeb630.png)

## Server(`finale`) Setup

1. `cd finale`
2. `python3 -m pip install -r requirements.txt`
3. `vi finale.py` and fill in your PASSWORD and PORT
4. `python3 ./finaly.py`

## Client(`tiro`) Setup

1. `cd tiro`
2. `python3 -m pip install -r requirements.txt`
3. `vi ssl_config.py` and fill in your OpenSSH executable path
4. `vi finale_launcher.py` and fill in the server's FINALE_URL and PASSWORD 
4. `python3 ./tiro_proxy.py`

## Todo-List

- Add GUI support for `tiro`
- Fix the `Content-Length` related bug
- Improve efficiency
