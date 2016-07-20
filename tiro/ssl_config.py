#coding=utf-8

openssl_bin=r'"openssl/openssl.exe"'
validity_days=365
key_dir='_generated_keys'
psl_filename='ssl_stuff/public_suffix_list.dat'

ca_key_file='ssl_stuff/tiroFinale_CA.ca.key'
ca_crt_file='ssl_stuff/tiroFinale_CA.ca.crt'
ca_pem_file='ssl_stuff/tiroFinale_CA.ca.pem'
ca_serial_file='ssl_stuff/serial'
ca_openssl_config='ssl_stuff/openssl.cnf'

subj_country='CN'
subj_state='DO_NOT_TRUST'
subj_locality='DO_NOT_TRUST'
subj_organization='tiroFinale'
subj_email='tiro@fina.le'
subj_ounit='tiroFinale'