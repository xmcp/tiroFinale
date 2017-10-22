#coding=utf-8
from const import OPENSSL_BIN

default_openssl_bins=[
    OPENSSL_BIN,
    r'openssl',
    r'"openssl/openssl.exe"',
    r'"C:/Program Files/Git/mingw32/bin/openssl.exe"',
    r'"C:/Program Files (x86)/Git/mingw32/bin/openssl.exe"',
]
validity_days=3650
key_dir='_generated_keys'
psl_filename='ssl_stuff/public_suffix_list.dat'

ca_key_file='ssl_stuff/tiroFinale_CA.ca.key'
ca_crt_file='ssl_stuff/tiroFinale_CA.ca.crt'
ca_pem_file='ssl_stuff/tiroFinale_CA.ca.pem'
ca_serial_file='ssl_stuff/serial'
ca_openssl_config='ssl_stuff/openssl.template.cnf'

subj_country='CN'
subj_state='DO_NOT_TRUST'
subj_locality='DO_NOT_TRUST'
subj_organization='tiroFinale'
subj_email='tiro@fina.le'
subj_ounit='tiroFinale'