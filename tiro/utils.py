import ssl_config
import const

_psl=None
def normdomain(domain):
    from publicsuffix import PublicSuffixList
    global _psl

    if _psl is None:
        print('utils: loading public suffix list')
        _psl=PublicSuffixList(open(ssl_config.psl_filename, encoding='utf-8'))

    suf=_psl.get_public_suffix(domain)
    return domain if domain==suf else '*.%s'%suf

try:
    assert const.SET_SYSTEM_PROXY
    import winreg
except (ImportError,AssertionError):
    if const.SET_SYSTEM_PROXY: #then import failed
        print('utils: automatic proxy configuration failed')
    def set_proxy():
        pass
else:

    # do not touch. that's magic. more details about motherf**king windows registry:
    # http://blogs.msmvps.com/mickyj/blog/2013/10/31/programmatically-alter-automatically-detect-settings-in-ie-through-vbs/
    MAGIC_DEFAULT_CONNECTION_SETTINGS=b'F\x00\x00\x00\xab\x01\x00\x00\x03\x00\x00\x00\x0e\x00\x00\x00127.0.0.1:8848'\
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    MAGIC_SAVED_LEGACY_SETTINGS=b'F\x00\x00\x00\xb4\x01\x00\x00\x03\x00\x00\x00\x0e\x00\x00\x00127.0.0.1:8848\x00'\
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    def set_proxy():
        print('utils: setting system proxy')
        reg=winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
        key=winreg.OpenKey(reg,r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',0,winreg.KEY_ALL_ACCESS)

        fuckwindows=winreg.OpenKey(key,'Connections',0,winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(fuckwindows,'DefaultConnectionSettings',None,winreg.REG_BINARY,MAGIC_DEFAULT_CONNECTION_SETTINGS)
        winreg.SetValueEx(fuckwindows,'SavedLegacySettings',None,winreg.REG_BINARY,MAGIC_SAVED_LEGACY_SETTINGS)

        winreg.SetValueEx(key,'ProxyEnable',None,winreg.REG_DWORD,1)
        winreg.SetValueEx(key,'ProxyServer',None,winreg.REG_SZ,'127.0.0.1:8848')
        winreg.SetValueEx(key,'ProxyHttp1.1',None,winreg.REG_DWORD,1)
        winreg.SetValueEx(key,'ProxyOverride',None,winreg.REG_SZ,'<-loopback>')
        winreg.SetValueEx(key,'MigrateProxy',None,winreg.REG_DWORD,1)


        winreg.CloseKey(fuckwindows)
        winreg.CloseKey(key)
