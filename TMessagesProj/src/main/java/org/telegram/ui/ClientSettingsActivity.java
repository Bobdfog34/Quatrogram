ackage org.telegram.ui;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import org.telegram.messenger.LocaleController;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Cells.TextInfoPrivacyCell;
import org.telegram.ui.Components.LayoutHelper;

public class ClientSettingsActivity extends BaseFragment {

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
    public ViewGroup onCreateView(ViewGroup parent) {
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

        fragmentView = new LinearLayout(getParentActivity());
        ((LinearLayout) fragmentView).setOrientation(LinearLayout.VERTICAL);

        nftGiftsCell = new TextCheckCell(getParentActivity());
        nftGiftsCell.setTextAndValue(LocaleController.getString(R.string.ClientSettingsNFTGifts), LocaleController.getString(R.string.ClientSettingsNFTGiftsInfo), false);
        nftGiftsCell.setChecked(false);
        nftGiftsCell.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                nftGiftsCell.setChecked(!nftGiftsCell.isChecked());
            }
        });
        ((LinearLayout) fragmentView).addView(nftGiftsCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 48));

        TextInfoPrivacyCell infoCell = new TextInfoPrivacyCell(getParentActivity());
        infoCell.setText(LocaleController.getString(R.string.ClientSettingsNFTGiftsInfo), false);
        ((LinearLayout) fragmentView).addView(infoCell, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT, 0, 20, 0, 0));

        return fragmentView;
    }

    @Override
    public void onFragmentDestroy() {
        super.onFragmentDestroy();
    }
}
