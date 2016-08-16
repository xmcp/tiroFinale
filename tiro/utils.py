import ssl_config

_psl=None
def normdomain(domain):
    from publicsuffix import PublicSuffixList
    global _psl

    if _psl is None:
        print('utils: loading public suffix list')
        _psl=PublicSuffixList(open(ssl_config.psl_filename, encoding='utf-8'))

    suf=_psl.get_public_suffix(domain)
    return domain if domain==suf else '*.%s'%suf