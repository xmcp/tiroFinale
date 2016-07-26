#coding=utf-8

## basic settings

PROXY_PORT = 8848
FINALE_URL = 'http://127.0.0.1:4446/finale'
PASSWORD = 'rdfzyjy'
TIMEOUT = 30 # in seconds
OPENSSL_BIN = None # for who prefers a custom openssl executable
PORTAL_PORT = 8844

## optimizations

CHUNKSIZE = 64*1024
# the response streams are sent back in chunks.
# do not edit unless you know what you are doing, as a large chunksize will increase TTFB.

POOLSIZE = 100
# tiro uses requests's connection pool mechanism.
# improve concurrency but will consume more RAM.

SSL_WILDCARD = True
# tiro ssl module will sign wildcard ssl certificate for sub-domains.
# turn on for better efficiency. turn off if you encounter ssl certificate errors.

COMPRESS_THRESHOLD = 32*1024
# tiro uses gzip to compress large Finale request data.
# increase the threshold for better upload speed. decrease the threshold for shorter TTFB.

GFWLIST_ENABLED = False
# tiro will use GFWList to determine whether to use Finale proxy or make the request directly.
# experimental. do not enable unless you are really confident about GFWList.

REUSE_SESSION = True
# tiro will reuse the requests sessions of direct requests.
# recommended. DRAMATICALLY improve efficiency, but have potential security vulnerability.

## internal arguments

_TEST_URL = 'http://example.com/not_exist/tiro_finale_test.page'
_PORTAL_CALLBACK = '___callback_tf_proxy_running'