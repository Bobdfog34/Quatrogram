package org.telegram.ui;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Cells.TextInfoPrivacyCell;
import org.telegram.ui.Components.LayoutHelper;

public class ClientSettingsActivity extends BaseFragment {

    private static final String PREFS = "quatrogram";
    private static final String KEY_NFT_BUBBLES = "nftBubbles";

    private TextCheckCell nftGiftsCell;

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
