#coding=utf-8

## basic settings
# you can also change Finale settings in the web portal

PROXY_PORT = 8848
PORTAL_PORT = 8844
FINALE_URL = 'http://127.0.0.1:4446/finale'
PASSWORD = 'rdfzyjy'
TIMEOUT = 15 # in seconds
OPENSSL_BIN = None # for who prefers a custom openssl executable
SET_SYSTEM_PROXY = True # automatically proxy configuration on Windows
SHOW_INTRO = True # automatically showing the intro page after startup

## optimizations
# designed for advanced users. change it at your own risk.

CHUNKSIZE = 64*1024
# the response streams are sent back in chunks.
# a small chunksize will limit download speed; a large chunksize will increase TTFB.

POOLSIZE = 128
# tiro uses requests's connection pool mechanism and tornado's thread pool mechanism.
# a bigger poolsize will improve concurrency but will consume more RAM.

SSL_WILDCARD = True
# tiro ssl module will sign wildcard ssl certificate for sub-domains.
# turn on for better efficiency. turn off if you encounter ssl certificate errors.

COMPRESS_THRESHOLD = 32*1024
# tiro uses gzip to compress large Finale request data.
# increase the threshold for better upload speed. decrease the threshold for shorter TTFB.

PROXY_MODE = 2
# 0: Completely Direct / 1: Jaô-Shingan™ Technique (experimental) / 2: Completely Finale
# for mode 1, tiro will redirect websites with connection problems to the Finale server.

REUSE_SESSION = True
# tiro will reuse the requests sessions of direct requests.
# recommended. DRAMATICALLY improve efficiency, but have potential security vulnerability.

## internal arguments
# undocumented. DO NOT CHANGE unless you know exactly what your are doing.

TEST_URL = 'http://example.com/not_exist/tiro_finale_test.page'
PORTAL_CALLBACK = '___callback_tf_proxy_running'