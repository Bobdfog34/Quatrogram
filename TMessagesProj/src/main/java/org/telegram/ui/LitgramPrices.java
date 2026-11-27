package org.telegram.ui;

import android.content.Context;
import android.util.SparseIntArray;

import org.telegram.messenger.ApplicationLoader;

public class LitgramPrices {

    private static final String PREFS = "litgram";
    private static final String KEY_NFT_RUB = "nftRub";
    private static final String KEY_STARS_CARD = "starsCard";

    public static boolean nftRubEnabled() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            return ctx != null && ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_NFT_RUB, true);
        } catch (Throwable ignore) {
            return true;
        }
    }

    public static boolean starsCardEnabled() {
        try {
            Context ctx = ApplicationLoader.applicationContext;
            return ctx != null && ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_STARS_CARD, true);
        } catch (Throwable ignore) {
            return true;
        }
    }

    /** 1 star = 1 ruble, as requested. */
    public static String starsToRub(long stars) {
        return String.format(java.util.Locale.US, "%,d", stars) + " ₽";
    }

    public static String starsToRubApprox(long stars) {
        return "≈" + starsToRub(stars);
    }
}
