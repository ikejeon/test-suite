import os
import asyncio
from os.path import expanduser

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

def _get_config_from_cmdline():
    import argparse
    parser = argparse.ArgumentParser(description="Run a Hyperledger Indy agent that communicates by email.")
    parser.add_argument("--ll", metavar='LVL', default="DEBUG", help="log level (default=INFO)")
    args = parser.parse_args()
    return args

def _get_config_from_file(home):
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

# def set_up_all():
loop = asyncio.get_event_loop()
home = expanduser("~")
cfg = _get_config_from_file(home)
smtp_cfg = _apply_cfg(cfg, 'smtp2', _default_smtp_cfg)
imap_cfg = _apply_cfg(cfg, 'imap2', _default_imap_cfg)
wallet_email_subject = "test-wallet"
    # return loop, home, args, cfg, smtp_cfg, imap_cfg, securemsg, zipPath, wallet_email_subject
