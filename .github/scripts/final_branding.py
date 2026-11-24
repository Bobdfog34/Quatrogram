#!/usr/bin/env python3
"""Финальная очистка брендинга перед сборкой APK.

Заменяет剩余 вхождения слов Telegram/telesrv/TELEGRAM/Telesrv на Quatrogram
только в пользовательских строках (значения <string>, Java/Kotlin string
literals). Package names org.telegram.* и имена ресурсов R.string.* не трогает.
"""
import os
import re
from pathlib import Path

ROOT = Path('.')
APP_NAME = os.environ.get('APP_DISPLAY_NAME', 'Quatrogram')

PAIRS = [
    ('telegram.org', 'litgram.net'),
    ('Telegram.org', 'Litgram.net'),
    ('telegram.me', 'litgram.net'),
    ('telegram.dog', 'litgram.net'),
    ('quatrogram.net', 'litgram.net'),
    ('Quatrogram.net', 'Litgram.net'),
    ('t.me', 'litgram.net'),
    ('telesrv.net', 'litgram.net'),
    ('Telesrv', APP_NAME),
    ('telesrv', APP_NAME.lower()),
    ('QUATROGRAM', APP_NAME.upper()),
    ('Quatrogram', APP_NAME),
    ('quatrogram', APP_NAME.lower()),
    ('TELEGRAM', APP_NAME.upper()),
    ('Telegram', APP_NAME),
    ('telegram', APP_NAME.lower()),
]

RES_DIRS = list(ROOT.glob('TMessagesProj*/src/main/res'))
JAVA_DIRS = list(ROOT.glob('TMessagesProj*/src/main/java'))


def brand_value(value):
    for old, new in PAIRS:
        value = value.replace(old, new)
    return value


def patch_strings_xml(path):
    text = path.read_text(encoding='utf-8')
    original = text

    def repl(m):
        return m.group(1) + brand_value(m.group(2)) + m.group(3)

    text = re.sub(r'(<string\b[^>]*>)(.*?)(</string>)', repl, text, flags=re.S)
    text = re.sub(r'(<item\b[^>]*>)(.*?)(</item>)', repl, text, flags=re.S)
    # AppName विशेष — гарантируем, что AppName = Quatrogram
    text = re.sub(
        r'(<string name="AppName">)[^<]*(</string>)',
        lambda m: m.group(1) + APP_NAME + m.group(2),
        text,
    )

    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f'patched strings: {path}')


def patch_java_literals(path):
    text = path.read_text(encoding='utf-8')
    original = text

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
        # Resource-name literals used by LocaleController.formatString — не UI.
        if re.fullmatch(r'"[A-Za-z][A-Za-z0-9_]*"', literal_text) and re.match(r'\s*,\s*R\.string\.', text[j:]):
            out.append(literal_text)
        else:
            out.append(brand_value(literal_text))
        i = j

    new_text = ''.join(out)
    if new_text != original:
        path.write_text(new_text, encoding='utf-8')
        print(f'patched literals: {path}')


changed = 0
for res_dir in RES_DIRS:
    for values_dir in res_dir.glob('values*'):
        for f in values_dir.glob('*.xml'):
            patch_strings_xml(f)
            changed += 1

for java_dir in JAVA_DIRS:
    for f in java_dir.rglob('*'):
        if f.is_file() and f.suffix.lower() in ('.java', '.kt'):
            patch_java_literals(f)
            changed += 1

print(f'Final branding cleanup: {changed} files patched.')
