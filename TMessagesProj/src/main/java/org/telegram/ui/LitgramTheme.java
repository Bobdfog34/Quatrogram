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

    private static final String KEY_NFT_BUBBLES = "nftBubbles";

    public static boolean nftBubblesEnabled() {
        return true;
    }

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
        // Custom appearance settings removed: keep the original UI untouched.
    }
}
