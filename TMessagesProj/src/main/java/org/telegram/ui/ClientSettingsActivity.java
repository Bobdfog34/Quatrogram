package org.telegram.ui;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
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


    private TextCheckCell nftGiftsCell;
    private TextCheckCell redThemeCell;
    private TextCheckCell glassCell;
    private TextCheckCell outlineCell;
    private TextCheckCell outlineColorCell;
    private TextCheckCell starsCardCell;
    private TextCheckCell nftPriceCell;
    private TextCheckCell cardCustomCell;

    public ClientSettingsActivity() {
        super(null);
    }

    @Override
    public boolean onFragmentCreate() {
        super.onFragmentCreate();
        return true;
    }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setAllowOverlayTitle(true);
        actionBar.setTitle(LocaleController.getString(R.string.ClientSettings));
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) {
                    finishFragment();
                }
            }
        });

        fragmentView = new LinearLayout(context);
        ((LinearLayout) fragmentView).setOrientation(LinearLayout.VERTICAL);

        nftGiftsCell = new TextCheckCell(context);
        nftGiftsCell.setTextAndValue(LocaleController.getString(R.string.ClientSettingsNFTGifts), LocaleController.getString(R.string.ClientSettingsNFTGiftsInfo), false, false);
        nftGiftsCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_NFT_BUBBLES, true));
        nftGiftsCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                nftGiftsCell.setChecked(!nftGiftsCell.isChecked());
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_NFT_BUBBLES, nftGiftsCell.isChecked()).apply();
            }
        });
        ((LinearLayout) fragmentView).addView(nftGiftsCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        redThemeCell = new TextCheckCell(context);
        redThemeCell.setTextAndValue("Красная тема Litgram", "Красный и чёрный дизайн", false, false);
        redThemeCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_RED_THEME, true));
        redThemeCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !redThemeCell.isChecked();
                redThemeCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_RED_THEME, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(redThemeCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        glassCell = new TextCheckCell(context);
        glassCell.setTextAndValue("Жидкое стекло", "Прозрачные панели", false, false);
        glassCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_LIQUID_GLASS, true));
        glassCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !glassCell.isChecked();
                glassCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_LIQUID_GLASS, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(glassCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        outlineCell = new TextCheckCell(context);
        outlineCell.setTextAndValue("Обводка сообщений", "Цветная рамка сообщений", false, false);
        outlineCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_MESSAGE_OUTLINE, true));
        outlineCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !outlineCell.isChecked();
                outlineCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_MESSAGE_OUTLINE, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(outlineCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        outlineColorCell = new TextCheckCell(context);
        outlineColorCell.setTextAndValue("Цвет обводки", "Красный / синий / зелёный", false, false);
        outlineColorCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_OUTLINE_COLOR, false));
        outlineColorCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !outlineColorCell.isChecked();
                outlineColorCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_OUTLINE_COLOR, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(outlineColorCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        starsCardCell = new TextCheckCell(context);
        starsCardCell.setTextAndValue("Звёзды картой", "Показывать звёзды как карту", false, false);
        starsCardCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_STARS_CARD, true));
        starsCardCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !starsCardCell.isChecked();
                starsCardCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_STARS_CARD, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(starsCardCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        nftPriceCell = new TextCheckCell(context);
        nftPriceCell.setTextAndValue("Цена NFT в рублях", "Показывать стоимость подарка в ₽", false, false);
        nftPriceCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_NFT_RUB, true));
        nftPriceCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !nftPriceCell.isChecked();
                nftPriceCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_NFT_RUB, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(nftPriceCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        cardCustomCell = new TextCheckCell(context);
        cardCustomCell.setTextAndValue("Кастомизация карт", "Фон и NFT-стикеры", false, false);
        cardCustomCell.setChecked(ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_CARD_CUSTOM, true));
        cardCustomCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean checked = !cardCustomCell.isChecked();
                cardCustomCell.setChecked(checked);
                ApplicationLoader.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(KEY_CARD_CUSTOM, checked).apply();
                Toast.makeText(context, "Перезапустите Litgram, чтобы применить", Toast.LENGTH_SHORT).show();
            }
        });
        ((LinearLayout) fragmentView).addView(cardCustomCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 64));

        TextInfoPrivacyCell infoCell = new TextInfoPrivacyCell(context);
        infoCell.setText(LocaleController.getString(R.string.ClientSettingsNFTGiftsInfo));
        ((LinearLayout) fragmentView).addView(infoCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT, 0, 20, 0, 0));

        return fragmentView;
    }

    @Override
    public void onFragmentDestroy() {
        super.onFragmentDestroy();
    }
}
