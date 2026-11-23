#!/usr/bin/env python3
"""Finalize the imported Telegram Android source for Quatrogram.

Runs inside the import workflow after the gramsrv patch commits are applied.
Everything configurable comes from repository variables / workflow env.
"""
import os
import re
from pathlib import Path

ROOT = Path('src')
CONFIG = Path('config/.github')

VERSION = os.environ.get('APP_VERSION_NAME', '13.3.1')
VERSION_CODE = os.environ.get('APP_VERSION_CODE', '7310')
APP_NAME = os.environ.get('APP_DISPLAY_NAME', 'Quatrogram')
HOST = os.environ.get('SERVER_HOST', '10.172.61.102')
PORT = os.environ.get('SERVER_PORT', '2398')
DC_ID = os.environ.get('DC_ID', '2')
DOMAIN = os.environ.get('LINK_DOMAIN', 'telesrv.net')
FINGERPRINT = os.environ.get('SERVER_RSA_FINGERPRINT', '0x9dbe5a4c45febeff')
KEY_FILE = CONFIG / 'server-rsa.pub'


def read(path):
    return path.read_text(encoding='utf-8')


def write(path, text):
    path.write_text(text, encoding='utf-8')


def brace_end(text, open_pos):
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError('Unbalanced braces')


def replace_function(text, signature_prefix, new_body):
    start = text.index(signature_prefix)
    open_pos = text.index('{', start)
    end = brace_end(text, open_pos)
    return text[:start] + new_body + text[end:]


# 1. Version metadata -------------------------------------------------------
gradle_props = ROOT / 'gradle.properties'
s = read(gradle_props)
s = re.sub(r'^APP_VERSION_NAME=.*$', 'APP_VERSION_NAME=' + VERSION, s, flags=re.M)
s = re.sub(r'^APP_VERSION_CODE=.*$', 'APP_VERSION_CODE=' + VERSION_CODE, s, flags=re.M)
write(gradle_props, s)
print('version:', VERSION, VERSION_CODE)

# 2. App display name -------------------------------------------------------
for f in ROOT.glob('TMessagesProj*/src/main/res/values*/strings.xml'):
    s = read(f)
    s2 = re.sub(r'(<string name="AppName">)[^<]*(</string>)',
                lambda m: m.group(1) + APP_NAME + m.group(2), s)
    if s2 != s:
        write(f, s2)
        print('app name:', f)

# 3. Link domain (the gramsrv patch uses telesrv.net) -----------------------
escaped_domain = DOMAIN.replace('.', r'\\.')
for pattern in ('TMessagesProj*/src/**/*.java', 'TMessagesProj*/src/**/*.xml',
                'TMessagesProj*/src/**/*.kt'):
    for f in ROOT.glob(pattern):
        if not f.is_file():
            continue
        try:
            s = read(f)
        except UnicodeDecodeError:
            continue
        o = s
        s = s.replace('telesrv.net', DOMAIN)
        s = s.replace('telesrv\\.net', escaped_domain)
        s = s.replace('https://t.me/', 'https://' + DOMAIN + '/')
        s = s.replace('http://t.me/', 'http://' + DOMAIN + '/')
        s = s.replace('telegram.me', DOMAIN)
        s = s.replace('telegram.dog', DOMAIN)
        s = s.replace(r't\\.me', escaped_domain)
        if 't.me' in s:
            s = re.sub(r'(?<![A-Za-z0-9_./])t\.me(?![A-Za-z0-9_/])', DOMAIN, s)
        if s != o:
            write(f, s)

# 4. Lock the client to one datacenter --------------------------------------
cm = ROOT / 'TMessagesProj/jni/tgnet/ConnectionsManager.cpp'
s = read(cm)

init_dc = f'''void ConnectionsManager::initDatacenters() {{
    Datacenter *datacenter;
    auto iter = datacenters.find({DC_ID});
    if (iter == datacenters.end()) {{
        datacenter = new Datacenter(instanceNum, {DC_ID});
        datacenters[{DC_ID}] = datacenter;
    }} else {{
        datacenter = iter->second;
    }}

    std::vector<TcpAddress> localAddresses;
    localAddresses.push_back(TcpAddress("{HOST}", {PORT}, TcpAddressFlagStatic, ""));
    datacenter->replaceAddresses(localAddresses, 0);
}}
'''
s = replace_function(s, 'void ConnectionsManager::initDatacenters()', init_dc)

# switchBackend must switch to our DC, not DC 1
try:
    sw_start = s.index('void ConnectionsManager::switchBackend(')
    sw_open = s.index('{', sw_start)
    sw_end = brace_end(s, sw_open)
    sw = s[sw_start:sw_end]
    sw = sw.replace('currentDatacenterId = 1;', 'currentDatacenterId = ' + DC_ID + ';')
    s = s[:sw_start] + sw + s[sw_end:]
except ValueError:
    print('WARNING: switchBackend not found')

# Never accept datacenter lists from the server or saved config
try:
    upd_start = s.index('void ConnectionsManager::updateDcSettings(')
    upd_open = s.index('{', upd_start)
    s = s[:upd_open + 1] + '\n    return; // Quatrogram: endpoint is locked to the bundled server\n' + s[upd_open + 1:]
except ValueError:
    print('WARNING: updateDcSettings not found')

write(cm, s)
print('server locked to', HOST, PORT, 'DC', DC_ID)

# 5. Baked RSA bootstrap key ------------------------------------------------
pem = KEY_FILE.read_text(encoding='utf-8').strip()
c_key = pem.replace('\r\n', '\n').replace('\n', '\\n')
key_block = (
    'if (serverPublicKeys.empty()) {\n'
    '                serverPublicKeys.emplace_back("' + c_key + '");\n'
    '                serverPublicKeysFingerprints.push_back(' + FINGERPRINT + ');\n'
    '            }'
)
hs = ROOT / 'TMessagesProj/jni/tgnet/Handshake.cpp'
s = read(hs)
start = s.index('if (serverPublicKeys.empty()) {')
end = brace_end(s, s.index('{', start))
s = s[:start] + key_block + s[end:]
write(hs, s)
print('RSA key installed, fingerprint', FINGERPRINT)

print('Finalize complete.')
