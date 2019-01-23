# Python code to illustrate Sending mail with json-format attachments
# from your Gmail account

# libraries to be imported
import smtplib
import os
import asyncio
import time
import re
import json
import logging

from indy import crypto, did, wallet

from os.path import expanduser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# from .mail_transport import *
import mail_transport

class SecureMsg():
    async def encryptMsg(self, decrypted):
        with open(decrypted, 'rb') as f:
            msg = f.read()
        encrypted = await crypto.auth_crypt(self.wallet_handle, self.my_vk, self.their_vk, msg)
        # encrypted = await crypto.anon_crypt(their_vk, msg)
        print('encrypted = %s' % repr(encrypted))
        with open('encrypted.dat', 'wb') as f:
            f.write(bytes(encrypted))
        print('prepping %s' % msg)

#     # Step 6 code goes here, replacing the read() stub.
    async def decryptMsg(self, encrypted):
        decrypted = await crypto.auth_decrypt(self.wallet_handle, self.my_vk, encrypted)
        # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
        return (decrypted)
#
    async def init(self):
        me = 'Mailagent'.strip()
        self.wallet_config = '{"id": "%s-wallet"}' % me
        self.wallet_credentials = '{"key": "%s-wallet-key"}' % me

        # 1. Create Wallet and Get Wallet Handle
        try:
            await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
        except:
            pass
        self.wallet_handle = await wallet.open_wallet(self.wallet_config, self.wallet_credentials)
        print('wallet = %s' % self.wallet_handle)

        (self.my_did, self.my_vk) = await did.create_and_store_my_did(self.wallet_handle, "{}")
        print('my_did and verkey = %s %s' % (self.my_did, self.my_vk))
        did_vk = {}
        did_vk["did"] = self.my_did
        did_vk["my_vk"] = self.my_vk

        with open("start_connection.json", 'w') as outfile:
            json.dump(did_vk, outfile)

        self.their = input("Other party's DID and verkey? ").strip().split(' ')
        self.their_vk = self.their[1]
        return self.wallet_handle, self.my_did, self.my_vk, self.their[0], self.their[1]

    def __init__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.init())
            time.sleep(1)  # waiting for libindy thread complete
        except KeyboardInterrupt:
            print('')

def send(senderEmail, senderPwd, server, port, dest, fileName, subject):
    filename = fileName
    attachment = open(filename, "rb")

    # instance of MIMEMultipart
    m = MIMEMultipart()

        # attach the body with the msg instance
    m.attach(MIMEText('See attached file.', 'plain'))

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename=msg.ap")

    # attach the instance 'p' to instance 'msg'
    m.attach(p)

    # storing the senders email address.
    m['From'] = senderEmail  # TODO: get from config

    # storing the receivers email address
    m['To'] = dest

    # storing the subject
    m['Subject'] = subject

    # creates SMTP session
    s = smtplib.SMTP(server, port)

    # start TLS for security
    s.starttls()

    # Authentication (If you use your personal email, use your personal password instread of 'I only talk via email!')
    s.login(senderEmail, senderPwd)

    # sending the mail
    s.sendmail(senderEmail, dest, m.as_string())

    # terminating the session
    s.quit()

def fetch_msg(trans, svr, ssl, username, password, their_email):
    return trans.receive(svr, ssl, username, password, their_email)

def run(svr, ssl, username, password, their_email):
    incoming_email = None
    transport = None
    if not transport:
        transport = mail_transport.MailTransport()
    trans = transport
    logging.info('Agent started.')
    try:
        # while True:
        ###
        wc = fetch_msg(trans, svr, ssl, username, password, their_email)
        ###
        if wc:
            incoming_email = wc.msg
            print('incoming_email is:')
            print(incoming_email)
        else:
            time.sleep(2.0)
    except:
        logging.info('Agent stopped.')
    return incoming_email

def _get_config_from_cmdline():
    import argparse
    parser = argparse.ArgumentParser(description="Run a Hyperledger Indy agent that communicates by email.")
    parser.add_argument("--ll", metavar='LVL', default="DEBUG", help="log level (default=INFO)")
    args = parser.parse_args()
    return args

def _get_config_from_file():
    import configparser
    cfg = configparser.ConfigParser()
    cfg_path = home+'/.mailagent/config.ini'
    if os.path.isfile(cfg_path):
        cfg.read(home+'/.mailagent/config.ini')
    return cfg

def _apply_cfg(cfg, section, defaults):
    x = defaults
    if cfg and (cfg[section]):
        src = cfg[section]
        for key in src:
            x[key] = src[key]
    return x

def setUp():
    print ("securemsg")
    loop.run_until_complete(securemsg.encryptMsg('testFileToSend.json'))

def demo(imap):
    while True:
        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        if re.match(cmd, 'send'):
            print("here is where I set userInput - init")
            # This is to send email to the agent.
            # You can use your personal email
            send_to_agent('encrypted.dat', "encrypted msg")
        elif re.match(cmd, 'decrypt'):
            encrypted_msg = run(imap['server'], imap['ssl'], imap['username'], imap['password'], 'indyagent1@gmail.com')
            print(encrypted_msg[0])
            decrypted_msg = loop.run_until_complete(securemsg.decryptMsg(encrypted_msg))
            print(decrypted_msg)
            decrypted_msg_obj = json.loads(decrypted_msg[1].decode("utf-8"))
            print('decrypted_msg_obj is:  ')
            print(decrypted_msg_obj)
        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

_default_smtp_cfg = {
    'server': 'smtp.gmail.com',
    'username': 'your email',
    'password': 'find the password from the config file',
    'port': '587'
}

_default_imap_cfg = {
    'server': 'imap.gmail.com',
    'username': 'indyagent1@gmail.com',
    'password': 'invalid password',
    'ssl': '1',
    'port': '993'
}

loop = asyncio.get_event_loop()
home = expanduser("~")
args = _get_config_from_cmdline()
cfg = _get_config_from_file()
smtp_cfg = _apply_cfg(cfg, 'smtp2', _default_smtp_cfg)
imap_cfg = _apply_cfg(cfg, 'imap2', _default_imap_cfg)
securemsg = SecureMsg()
setUp()

def test_all():
    loop = asyncio.get_event_loop()
    home = expanduser("~")
    args = _get_config_from_cmdline()
    cfg = _get_config_from_file()
    smtp_cfg = _apply_cfg(cfg, 'smtp2', _default_smtp_cfg)
    imap_cfg = _apply_cfg(cfg, 'imap2', _default_imap_cfg)
    securemsg = SecureMsg()
    setUp()

def send_to_agent(filePath, email_subject):
    send(cfg['smtp2']['username'], cfg['smtp2']['password'], cfg['smtp2']['server'], cfg['smtp2']['port'], 'indyagent1@gmail.com', filePath, email_subject)

async def create():
    client = "test"
    wallet_config = '{"id": "%s-wallet"}' % client
    wallet_credentials = '{"key": "%s-wallet-key"}' % client
    opened = False

    # 1. Create Wallet and Get Wallet Handle
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        opened = True
        (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
        print('my_did and verkey = %s %s' % (my_did, my_vk))
    except Exception as e:
        print("Wallet already created", e)
        pass
    if not opened:
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)

    print('wallet = %s' % wallet_handle)

    meta = await did.list_my_dids_with_meta(wallet_handle)
    print(meta)
    home = expanduser("~")
    filePath = home + '/.indy_client/wallet/test-wallet'

    zipPath = shutil.make_archive('wallet', 'zip', filePath)
    return zipPath

# send_to_agent()
while True:
    demo(imap_cfg)
