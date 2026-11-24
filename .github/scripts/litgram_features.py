#!/usr/bin/env python3
"""Litgram onboarding and custom-tab strings for the Android client."""
import re
from pathlib import Path

VALUES = {
    "values/strings.xml": {
        "Page1Title": "Litgram",
        "Page2Message": "**Litgram** delivers messages faster than any other application, with NFT gifts.",
        "ClientSettings": "Litgram custom",
        "ClientSettingsInfo": "NEW \u00b7 NFT gifts and appearance",
        "ClientSettingsNFTGifts": "NFT bubbles around the profile",
        "ClientSettingsNFTGiftsInfo": "Pinned gifts float in bubbles around the avatar. Turn off for classic profile view.",
    },
    "values-ru/strings.xml": {
        "Page1Title": "Litgram",
        "Page2Message": "**Litgram** \u2014 \u0441\u0430\u043c\u044b\u0439 \u0431\u044b\u0441\u0442\u0440\u044b\u0439 \u043c\u0435\u0441\u0441\u0435\u043d\u0434\u0436\u0435\u0440 \u0441 NFT-\u043f\u043e\u0434\u0430\u0440\u043a\u0430\u043c\u0438.",
        "ClientSettings": "Litgram \u043a\u0430\u0441\u0442\u043e\u043c",
        "ClientSettingsInfo": "NEW \u00b7 NFT-\u043f\u043e\u0434\u0430\u0440\u043a\u0438 \u0438 \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435",
        "ClientSettingsNFTGifts": "NFT-\u043f\u0443\u0437\u044b\u0440\u0438 \u0432\u043e\u043a\u0440\u0443\u0433 \u043f\u0440\u043e\u0444\u0438\u043b\u044f",
        "ClientSettingsNFTGiftsInfo": "\u0417\u0430\u043a\u0440\u0435\u043f\u043b\u0451\u043d\u043d\u044b\u0435 \u043f\u043e\u0434\u0430\u0440\u043a\u0438 \u043b\u0435\u0442\u0430\u044e\u0442 \u043f\u0443\u0437\u044b\u0440\u044f\u043c\u0438 \u0432\u043e\u043a\u0440\u0443\u0433 \u0430\u0432\u0430\u0442\u0430\u0440\u0430. \u0412\u044b\u043a\u043b\u044e\u0447\u0438\u0442\u0435, \u0447\u0442\u043e\u0431\u044b \u0432\u0435\u0440\u043d\u0443\u0442\u044c \u043a\u043b\u0430\u0441\u0441\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0432\u0438\u0434.",
    },
}

root = Path("TMessagesProj/src/main/res")
for rel, values in VALUES.items():
    path = root / rel
    if not path.exists():
        print("missing", path)
        continue
    text = path.read_text(encoding="utf-8")
    for name, value in values.items():
        pattern = re.compile(r'(<string name="' + re.escape(name) + r'">)(.*?)(</string>)', re.S)
        if pattern.search(text):
            text = pattern.sub(lambda m: m.group(1) + value + m.group(2), text, count=1)
        else:
            text = text.replace("</resources>", '    <string name="%s">%s</string>\n</resources>' % (name, value))
    path.write_text(text, encoding="utf-8")
    print("patched", path)
