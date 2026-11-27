package org.telegram.ui;

import android.content.Context;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Toast;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Cells.TextInfoPrivacyCell;
import org.telegram.ui.Components.LayoutHelper;

public class ClientSettingsActivity extends BaseFragment {

    private static final String PREFS = "litgram";
    private static final String KEY_NFT_BUBBLES = "nftBubbles";
    private static final String KEY_RED_THEME = "redTheme";
    private static final String KEY_LIQUID_GLASS = "liquidGlass";
    private static final String KEY_MESSAGE_OUTLINE = "messageOutline";
    private static final String KEY_OUTLINE_COLOR = "outlineColorRed";
    private static final String KEY_STARS_CARD = "starsCard";
    private static final String KEY_NFT_RUB = "nftRub";
    private static final String KEY_CARD_CUSTOM = "cardCustom";

    public ClientSettingsActivity() {
        super(null);
    }

    @Override
    public boolean onFragmentCreate() {
        super.onFragmentCreate();
        return true;
    }

    private boolean pref(String key, boolean def) {
        try {
            return ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(key, def);
        } catch (Throwable ignore) {
            return def;
        }
    }

    private void save(String key, boolean value) {
        try {
            ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(key, value).apply();
        } catch (Throwable ignore) {}
    }

    private TextCheckCell addToggle(LinearLayout root, Context context, String title, String subtitle, String key, boolean def) {
        TextCheckCell cell = new TextCheckCell(context);
        cell.setTextAndValue(title, subtitle, false, false);
        cell.setChecked(pref(key, def));
        cell.setOnClickListener(v -> {
            boolean checked = !cell.isChecked();
            cell.setChecked(checked);
            save(key, checked);
            Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
        });
        root.addView(cell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 56));
        return cell;
    }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setAllowOverlayTitle(true);
        actionBar.setTitle("Кастом-настройки Litgram");
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) {
                    finishFragment();
                }
            }
        });

        ScrollView scroll = new ScrollView(context);
        scroll.setFillViewport(true);
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(root, LayoutHelper.createScroll(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT, 51));

        TextInfoPrivacyCell header = new TextInfoPrivacyCell(context);
        header.setText("Настройки оформления и функций Litgram. После изменения перезапустите приложение.");
        root.addView(header, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT, 0, 12, 0, 8));

        addToggle(root, context, "Красная тема Litgram", "Красный и чёрный дизайн", KEY_RED_THEME, true);
        addToggle(root, context, "Жидкое стекло", "Прозрачные панели", KEY_LIQUID_GLASS, true);
        addToggle(root, context, "Обводка сообщений", "Цветная рамка сообщений", KEY_MESSAGE_OUTLINE, true);
        addToggle(root, context, "Цвет обводки", "Вкл — красный, выкл — синий", KEY_OUTLINE_COLOR, true);
        addToggle(root, context, "Звёзды картой", "Показывать звёзды как карту", KEY_STARS_CARD, true);
        addToggle(root, context, "Цена NFT в рублях", "Стоимость подарка в ₽", KEY_NFT_RUB, true);
        addToggle(root, context, "Кастомизация карт", "Фон и NFT-стикеры", KEY_CARD_CUSTOM, true);
        addToggle(root, context, "NFT-пузыри", "Показывать NFT в чатах", KEY_NFT_BUBBLES, true);

        TextInfoPrivacyCell footer = new TextInfoPrivacyCell(context);
        footer.setText("Litgram — кастомизируйте приложение под себя.");
        root.addView(footer, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT, 0, 12, 0, 16));

        fragmentView = scroll;
        return fragmentView;
    }

    @Override
    public void onFragmentDestroy() {
        super.onFragmentDestroy();
    }
}
