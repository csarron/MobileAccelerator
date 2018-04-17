package com.cscao.apps.ncsdemo;

import android.graphics.Color;
import android.os.Environment;
import android.text.Spannable;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;

import com.orhanobut.logger.Logger;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/***
 * Created by qqcao on Apr 16, 2018.
 *
 */
public class Helper {
    public static final int VENDOR_ID = 0x03e7;
    public static final int PRODUCT_ID = 0x2150;
    public static final int OPENED_PRODUCT_ID = 0xf63b;

    private static SimpleDateFormat mDateFormat = new SimpleDateFormat("mm:ss.SSS", Locale.US);

    public static Spannable getStatus(String... status) {
        String timeStampStr = mDateFormat.format(new Date()) + ": ";
        String statusStr =  timeStampStr + String.join("", status) + "\n";
        Logger.d(statusStr);

        Spannable spannable = new SpannableString(statusStr);
        spannable.setSpan(new ForegroundColorSpan(Color.BLUE), 0, timeStampStr.length(), Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        return spannable;
    }

    public static String getSdcardPath() {
        File sdcard = Environment.getExternalStorageDirectory();
        return sdcard.getPath();
    }

    public static String getNcsPath() {
        return new File(getSdcardPath(), "ncs").getPath();
    }
}
