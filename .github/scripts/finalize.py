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
HOST = os.environ.get('SERVER_HOST', '89.169.12.230')
PORT = os.environ.get('SERVER_PORT', '2398')
DC_ID = os.environ.get('DC_ID', '2')
DOMAIN = os.environ.get('LINK_DOMAIN', 'quatrogram.net')
FINGERPRINT = os.environ.get('SERVER_RSA_FINGERPRINT', '0xc37f20620ef9f5ac')
KEY_FILE = CONFIG / 'config' / 'server-rsa.pub'


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


def patch_once(text, old, new, label):
    if old not in text:
        print('WARNING: pattern not found:', label)
        return text
    print('patched:', label)
    return text.replace(old, new, 1)


# Replacements are applied to user-visible text only. Java package/class names
# (org.telegram.*) are deliberately left untouched: renaming them would break
# the entire build.
PAIRS = [
    ('telegram.org', DOMAIN),
    ('Telegram.org', DOMAIN),
    ('telegram.me', DOMAIN),
    ('telegram.dog', DOMAIN),
    (r't\.me', DOMAIN.replace('.', r'\.')),
    ('t.me', DOMAIN),
    ('telesrv.net', DOMAIN),
    (r'telesrv\.net', DOMAIN.replace('.', r'\.')),
    ('Telegram', APP_NAME),
    ('TELEGRAM', APP_NAME.upper()),
    ('Telesrv', APP_NAME),
    ('telesrv', APP_NAME.lower()),
]


def apply_pairs(value):
    for old, new in PAIRS:
        value = value.replace(old, new)
    return value


def patch_string_resources(text):
    """Only change the *values* of string resources, never their names."""
    def repl(m):
        return m.group(1) + apply_pairs(m.group(2)) + m.group(3)

    text = re.sub(r'(<string\b[^>]*>)(.*?)(</string>)', repl, text, flags=re.S)
    text = re.sub(r'(<item\b[^>]*>)(.*?)(</item>)', repl, text, flags=re.S)
    return text


def patch_java_literals(text):
    """Replace brand words inside double-quoted Java/Kotlin/XML literals."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != '"':
            out.append(text[i])
            i += 1
            continue
        j = i + 1
        literal = ['"']
        while j < n:
            if text[j] == '\\' and j + 1 < n:
                literal.append(text[j:j + 2])
                j += 2
                continue
            if text[j] == '"':
                literal.append('"')
                j += 1
                break
            literal.append(text[j])
            j += 1
        literal_text = ''.join(literal)
        # Resource-name literals used by LocaleController.formatString
        # must stay in sync with R.string.<name>; they are not UI text.
        if (re.fullmatch(r'"[A-Za-z][A-Za-z0-9_]*"', literal_text)
                and re.match(r'\s*,\s*R\.string\.', text[j:])):
            out.append(literal_text)
        else:
            out.append(apply_pairs(literal_text))
        i = j
    return ''.join(out)


# 1. Version metadata -------------------------------------------------------
gradle_props = ROOT / 'gradle.properties'
s = read(gradle_props)
s = re.sub(r'^APP_VERSION_NAME=.*$', 'APP_VERSION_NAME=' + VERSION, s, flags=re.M)
s = re.sub(r'^APP_VERSION_CODE=.*$', 'APP_VERSION_CODE=' + VERSION_CODE, s, flags=re.M)
write(gradle_props, s)
print('version:', VERSION, VERSION_CODE)

# 2. Branding: every visible string, on the login screen and everywhere else -
resource_files = 0
for f in ROOT.glob('TMessagesProj*/src/main/res/values*/strings.xml'):
    s = read(f)
    s2 = patch_string_resources(s)
    s2 = re.sub(r'(<string name="AppName">)[^<]*(</string>)',
                lambda m: m.group(1) + APP_NAME + m.group(2), s2)
    if s2 != s:
        write(f, s2)
        resource_files += 1
print('branding: string resources updated in', resource_files, 'files')

code_files = 0
for pattern in ('TMessagesProj*/src/**/*.java', 'TMessagesProj*/src/**/*.kt',
                'TMessagesProj*/src/main/res/**/*.xml'):
    for f in ROOT.glob(pattern):
        if not f.is_file() or f.name == 'strings.xml':
            continue
        try:
            s = read(f)
        except UnicodeDecodeError:
            continue
        s2 = patch_java_literals(s)
        if s2 != s:
            write(f, s2)
            code_files += 1
print('branding: literals updated in', code_files, 'code/xml files')

# Older branding passes rewrote the R.string identifier itself.
# Restore it: the resource value is already branded, its name is internal.
for pattern in ('TMessagesProj*/src/**/*.java', 'TMessagesProj*/src/**/*.kt'):
    for f in ROOT.glob(pattern):
        if not f.is_file():
            continue
        try:
            s = read(f)
        except UnicodeDecodeError:
            continue
        s2 = s.replace('R.string.QuatrogramVersion', 'R.string.TelegramVersion')
        if s2 != s:
            write(f, s2)

# 3. Center the app name in the action bar ---------------------------------
ab = ROOT / 'TMessagesProj/src/main/java/org/telegram/ui/ActionBar/ActionBar.java'
s = read(ab)
centered = (
    '            titleTextView[0].setText(lastTitle = value);\n'
    '            if ("' + APP_NAME + '".contentEquals(value)) {\n'
    '                isCenterTitle = true;\n'
    '                centerTitleAndGlass = true;\n'
    '                titleTextView[0].setGravity(Gravity.CENTER);\n'
    '                requestLayout();\n'
    '            }'
)
s = patch_once(s, '            titleTextView[0].setText(lastTitle = value);', centered,
               'centered action bar title')
write(ab, s)

# 4. Wallets enabled for everyone ------------------------------------------
agc = ROOT / 'TMessagesProj/src/main/java/org/telegram/messenger/AppGlobalConfig.java'
s = read(agc)
s, count = re.subn(
    r'private ConfigBoolean ofBoolean\(String name, boolean defaultValue\) \{.*?\n    \}',
    'private ConfigBoolean ofBoolean(String name, boolean defaultValue) {\n'
    '        boolean forcedWallets = "wallet_available".equals(name);\n'
    '        ConfigBoolean configBoolean = new ConfigBoolean(name, forcedWallets ? true : defaultValue);\n'
    '        if (!forcedWallets) {\n'
    '            map.put(name, configBoolean.handler);\n'
    '        }\n'
    '\n'
    '        return configBoolean;\n'
    '    }',
    s, count=1, flags=re.S)
print('wallets: ofBoolean patched' if count else 'WARNING: ofBoolean not found')
write(agc, s)

# 5. Always show Gram and Stars balance cards in profiles -------------------
profile = ROOT / 'TMessagesProj/src/main/java/org/telegram/ui/ProfileActivity.java'
s = read(profile)
s = patch_once(
    s,
    'import org.telegram.tgnet.tl.TL_stars;',
    'import org.telegram.tgnet.tl.TL_stars;\nimport org.telegram.tgnet.tl.TL_wallet;',
    'TL_wallet import')
s = patch_once(
    s,
    '        hasBalance = userId != 0 && userInfo != null && userInfo.wallet_card != null\n'
    '                && (imageUpdater == null || myProfile);',
    '        hasBalance = userId != 0 && (imageUpdater == null || myProfile);\n'
    '        if (hasBalance) {\n'
    '            if (userInfo == null) {\n'
    '                userInfo = new TLRPC.UserFull();\n'
    '            }\n'
    '            if (userInfo.wallet_card == null) {\n'
    '                userInfo.wallet_card = new TL_wallet.card();\n'
    '                userInfo.wallet_card.balance = 0;\n'
    '            }\n'
    '        }',
    'always-on Gram card')
s = patch_once(
    s,
    '                balanceView.setBalance(userInfo.wallet_card.balance);',
    '                balanceView.setBalance(userInfo != null && userInfo.wallet_card != null ? userInfo.wallet_card.balance : 0);',
    'safe Gram balance')
s = patch_once(
    s,
    '                boolean divider = false;\n'
    '                if (user != null && user.bot) {\n'
    '                    if (userInfo != null && userInfo.can_view_revenue && BotStarsController.getInstance(currentAccount).getTONBalance(userId) > 0) {\n'
    '                        botTonBalanceRow = rowCount++;\n'
    '                    }\n'
    '                    if (BotStarsController.getInstance(currentAccount).getBotStarsBalance(userId).amount > 0 || BotStarsController.getInstance(currentAccount).hasTransactions(userId)) {\n'
    '                        botStarsBalanceRow = rowCount++;\n'
    '                    }\n'
    '                }',
    '                boolean divider = false;\n'
    '                if (user != null && user.bot) {\n'
    '                    if (userInfo != null && userInfo.can_view_revenue && BotStarsController.getInstance(currentAccount).getTONBalance(userId) > 0) {\n'
    '                        botTonBalanceRow = rowCount++;\n'
    '                    }\n'
    '                }\n'
    '                if (user != null && !UserObject.isService(user.id)) {\n'
    '                    botStarsBalanceRow = rowCount++;\n'
    '                }',
    'always-on Stars row')
s = patch_once(
    s,
    '                    } else if (position == botStarsBalanceRow) {\n'
    '                        final TL_stars.StarsAmount stars_balance = BotStarsController.getInstance(currentAccount).getBotStarsBalance(userId);\n'
    '                        SpannableStringBuilder ssb = new SpannableStringBuilder();\n'
    '                        if (stars_balance.amount > 0) {\n'
    '                            ssb.append("XTR ").append(formatStarsAmountShort(stars_balance));\n'
    '                        }',
    '                    } else if (position == botStarsBalanceRow) {\n'
    '                        final TL_stars.StarsAmount stars_balance = BotStarsController.getInstance(currentAccount).getBotStarsBalance(userId);\n'
    '                        SpannableStringBuilder ssb = new SpannableStringBuilder();\n'
    '                        ssb.append("XTR ").append(formatStarsAmountShort(stars_balance));',
    'show zero Stars balance')
write(profile, s)

# 6. Lock the client to one datacenter --------------------------------------
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

try:
    sw_start = s.index('void ConnectionsManager::switchBackend(')
    sw_open = s.index('{', sw_start)
    sw_end = brace_end(s, sw_open)
    sw = s[sw_start:sw_end]
    sw = sw.replace('currentDatacenterId = 1;', 'currentDatacenterId = ' + DC_ID + ';')
    s = s[:sw_start] + sw + s[sw_end:]
except ValueError:
    print('WARNING: switchBackend not found')

try:
    upd_start = s.index('void ConnectionsManager::updateDcSettings(')
    upd_open = s.index('{', upd_start)
    s = s[:upd_open + 1] + '\n    return; // Quatrogram: endpoint is locked to the bundled server\n' + s[upd_open + 1:]
except ValueError:
    print('WARNING: updateDcSettings not found')

write(cm, s)
print('server locked to', HOST, PORT, 'DC', DC_ID)

# 7. Baked RSA bootstrap key -------------------------------------------------
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
