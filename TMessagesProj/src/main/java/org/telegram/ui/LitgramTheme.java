package org.telegram.ui;

import android.content.Context;
import android.util.SparseIntArray;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.ui.ActionBar.Theme;

public class LitgramTheme {

    public static final String PREFS = "litgram";
    public static final String KEY_RED_THEME = "redTheme";
    public static final int RED = 0xFFE53935;
    public static final int RED_TEXT = 0xFFD32F2F;

    public static boolean isRedTheme() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            if (ctx == null) {
                return true;
            }
            return ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_RED_THEME, true);
        } catch (Throwable ignore) {
            return true;
        }
    }

    private static final String KEY_GLASS = "liquidGlass";
    private static final String KEY_OUTLINE = "messageOutline";
    private static final String KEY_OUTLINE_COLOR = "outlineColorRed";

    public static boolean glassEnabled() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            return ctx == null || ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_GLASS, true);
        } catch (Throwable ignore) {
            return true;
        }
    }

    public static boolean outlineEnabled() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            return ctx == null || ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_OUTLINE, true);
        } catch (Throwable ignore) {
            return true;
        }
    }

    public static int outlineColor() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            boolean red = ctx == null || ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_OUTLINE_COLOR, true);
            return red ? 0xFFE53935 : 0xFF2196F3;
        } catch (Throwable ignore) {
            return 0xFFE53935;
        }
    }

    public static void apply(SparseIntArray colors, boolean dark) {
        if (colors == null) {
            return;
        }
        if (glassEnabled()) {
            colors.put(Theme.key_dialogBackground, dark ? 0x99000000 : 0x99FFFFFF);
            colors.put(Theme.key_actionBarDefaultSubmenuBackground, dark ? 0x99121212 : 0x99F5F5F5);
        }
        if (outlineEnabled()) {
            colors.put(Theme.key_chat_inBubbleShadow, outlineColor());
            colors.put(Theme.key_chat_outBubbleShadow, outlineColor());
        }
        if (!isRedTheme()) {
            return;
        }
        colors.put(Theme.key_actionBarDefault, RED);
        colors.put(Theme.key_actionBarDefaultIcon, 0xFFFFFFFF);
        colors.put(Theme.key_actionBarDefaultTitle, 0xFFFFFFFF);
        colors.put(Theme.key_dialogTextBlue, RED_TEXT);
        colors.put(Theme.key_dialogTextBlue2, RED_TEXT);
        colors.put(Theme.key_dialogButton, RED_TEXT);
        colors.put(Theme.key_dialogFloatingButton, RED);
        colors.put(Theme.key_dialogCheckboxSquareBackground, RED);
        colors.put(Theme.key_dialogRadioBackgroundChecked, RED);
        colors.put(Theme.key_checkboxSquareBackground, RED);
        colors.put(Theme.key_radioBackgroundChecked, RED);
        colors.put(Theme.key_switchTrackChecked, RED);
        colors.put(Theme.key_chats_unreadCounter, RED);
        colors.put(Theme.key_chat_messagePanelSend, RED);
        colors.put(Theme.key_windowBackgroundWhiteLinkText, RED_TEXT);
        colors.put(Theme.key_windowBackgroundWhiteBlueHeader, RED_TEXT);
        if (dark) {
            colors.put(Theme.key_windowBackgroundWhite, 0xFF000000);
            colors.put(Theme.key_windowBackgroundGray, 0xFF000000);
            colors.put(Theme.key_dialogBackground, 0xFF0D0D0D);
            colors.put(Theme.key_actionBarDefaultSubmenuBackground, 0xFF141414);
        }
    }
}
