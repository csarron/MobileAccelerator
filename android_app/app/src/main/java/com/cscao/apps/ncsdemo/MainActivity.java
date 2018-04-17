package com.cscao.apps.ncsdemo;

import static com.cscao.apps.ncsdemo.Helper.OPENED_PRODUCT_ID;
import static com.cscao.apps.ncsdemo.Helper.PRODUCT_ID;
import static com.cscao.apps.ncsdemo.Helper.VENDOR_ID;
import static com.cscao.apps.ncsdemo.Helper.getNcsPath;
import static com.cscao.apps.ncsdemo.Helper.getSdcardPath;
import static com.cscao.apps.ncsdemo.Helper.getStatus;

import android.Manifest;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.text.SpannableStringBuilder;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.orhanobut.logger.AndroidLogAdapter;
import com.orhanobut.logger.CsvFormatStrategy;
import com.orhanobut.logger.DiskLogAdapter;
import com.orhanobut.logger.FormatStrategy;
import com.orhanobut.logger.Logger;
import com.orhanobut.logger.PrettyFormatStrategy;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;

import eu.chainfire.libsuperuser.Shell;
import io.reactivex.Observable;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.CompositeDisposable;
import io.reactivex.disposables.Disposable;
import io.reactivex.schedulers.Schedulers;

public class MainActivity extends Activity {
    public static final int PERMISSIONS_REQUEST_CODE = 7;
    SpannableStringBuilder mSpannableBuilder = new SpannableStringBuilder();

    static {
        System.loadLibrary("ncs_jni");
    }

    private String mGraphFile;
    private String mImageFile;
    private String mCmdFile;

    private Button mRunButton;
    private TextView mStatusTextView;
    private TextView mDeviceTextView;

    CompositeDisposable mDisposable = new CompositeDisposable();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mRunButton = findViewById(R.id.run_ncs_btn);

        mStatusTextView = findViewById(R.id.status_tv);
        mStatusTextView.setMovementMethod(new ScrollingMovementMethod());

        mDeviceTextView = findViewById(R.id.device_status_tv);

        checkPermissions();

        FormatStrategy formatStrategy = PrettyFormatStrategy.newBuilder()
                .showThreadInfo(false).tag(getString(R.string.app_name)).build();
        Logger.addLogAdapter(new AndroidLogAdapter(formatStrategy) {
            @Override
            public boolean isLoggable(int priority, String tag) {
                return BuildConfig.DEBUG;
            }
        });

        if (BuildConfig.DEBUG) {
            setLogLevel(2);
        } else {
            setLogLevel(1);
        }
        
        FormatStrategy csvFormatStrategy = CsvFormatStrategy.newBuilder()
                .tag(getString(R.string.app_name)).build();
        Logger.addLogAdapter(new DiskLogAdapter(csvFormatStrategy));

        // Detach events are sent as a system-wide broadcast
        IntentFilter detachFilter = new IntentFilter(UsbManager.ACTION_USB_DEVICE_DETACHED);
        registerReceiver(mUsbReceiver, detachFilter);
        IntentFilter attachFilter = new IntentFilter(UsbManager.ACTION_USB_DEVICE_ATTACHED);
        registerReceiver(mUsbReceiver, attachFilter);

        handleIntent(getIntent());
    }

    private void checkPermissions() {
        boolean writeExternalStoragePermissionGranted =
                ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                        == PackageManager.PERMISSION_GRANTED;

        if (!writeExternalStoragePermissionGranted) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    PERMISSIONS_REQUEST_CODE);
        } else {
            mayCopyAsset();
            mayChangePermission();
        }

    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
            @NonNull String permissions[], @NonNull int[] grantResults) {
        if (requestCode == PERMISSIONS_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(MainActivity.this,
                        "sdcard permission granted",
                        Toast.LENGTH_SHORT).show();
                mayCopyAsset();
                mayChangePermission();
            } else {
                Toast.makeText(this, "Please grant write permission", Toast.LENGTH_LONG).show();
            }
        }
    }

    public void mayCopyAsset() {
        mRunButton.setEnabled(false);
        addStatus("initializing...");

        Observable<String> copyAssetObservable = Observable.create(
                emitter -> {
                    mCmdFile = copyAssetFileToSdcardNcsDir("mvnc/MvNCAPI.mvcmd");
                    setCmdFile(mCmdFile);
                    emitter.onNext(mCmdFile);

                    mGraphFile = copyAssetFileToSdcardNcsDir("mobilenet_v1.graph");
                    setGraphFile(mGraphFile);
                    emitter.onNext(mGraphFile);

                    mImageFile = copyAssetFileToSdcardNcsDir("keyboard.jpg");
                    setImageFile(mImageFile);
                    emitter.onNext(mImageFile);

                    emitter.onComplete();
                });

        Disposable copyDisposable = copyAssetObservable
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(filePath -> {
                    if (filePath != null) {
                        String fileRel = Paths.get(getNcsPath())
                                .relativize(Paths.get(filePath))
                                .toString();
                        addStatus("created /sdcard/ncs/", fileRel);
                    }
                });
        mDisposable.add(copyDisposable);

    }

    private String copyAssetFileToSdcardNcsDir(final String filename) {
        try {
            File destFile = Paths.get(getNcsPath(), filename).toFile();
            String destFilePath = destFile.getPath();
            if (destFile.exists()) {
                System.out.println(String.join(destFilePath, "already copied"));
                return destFilePath;
            }

            File parentDir = new File(destFile.getParent());
            if (!parentDir.exists()) {
                boolean status = parentDir.mkdirs();
                System.out.println("created " + parentDir + (status ? " successfully" : " failed"));
            }

            InputStream in = getAssets().open(filename);
            Files.copy(in, Paths.get(destFilePath));
            System.out.println(String.join("copied ", filename, " to ", destFilePath));
            return destFilePath;
        } catch (IOException e) {
            e.printStackTrace();
        }

        return null;
    }


    public void addStatus(String... statuses) {
        mSpannableBuilder.clear();
        mSpannableBuilder.append(mStatusTextView.getText());
        mSpannableBuilder.append(getStatus(statuses));
        mStatusTextView.setText(mSpannableBuilder, TextView.BufferType.SPANNABLE);
    }

    public void runInference(View view) {
        addStatus("preparing device...");

        addStatus("using graph:", mGraphFile, " image:", mImageFile);

        addStatus("begin doing inference...");

        Observable<String> copyAssetObservable = Observable.create(
                emitter -> {
                    String results = doInference(mGraphFile, mImageFile, 0);
                    emitter.onNext(results);
                    emitter.onComplete();
                });

        Disposable copyAssetDisposable = copyAssetObservable.subscribeOn(Schedulers.computation())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(result -> {
                    addStatus(result);
                    mRunButton.setEnabled(true);
                });
        mDisposable.add(copyAssetDisposable);

    }

    private void showUsbDeviceStatus() {
        mDeviceTextView.setText(R.string.not_found);

        UsbManager manager = (UsbManager) getSystemService(Context.USB_SERVICE);
        if (manager != null) {
            HashMap<String, UsbDevice> connectedDevices = manager.getDeviceList();
            if (connectedDevices.isEmpty()) {
                addStatus("No Devices Currently Connected");
            } else {
                addStatus("Connected Device Count: " + connectedDevices.size());
                for (UsbDevice device : connectedDevices.values()) {
                    int productID = device.getProductId();
                    int vendorID = device.getVendorId();
                    String productIDStr = String.format("0x%04X", productID & 0xFFFFF);
                    String vendorIDStr = String.format("0x%04X", vendorID & 0xFFFFF);
                    if (vendorID == VENDOR_ID && (productID == PRODUCT_ID
                            || productID == OPENED_PRODUCT_ID)) {
                        mRunButton.setEnabled(true);
                        mDeviceTextView.setText(R.string.attached);

                        addStatus("Manufacturer: ", device.getManufacturerName());
                        addStatus("Product: ", device.getProductName());
                        addStatus("VendorId:", vendorIDStr, ", ProductId:", productIDStr);
                    }
                }
            }
        } else {
            Logger.w("cannot get usb manager!");
        }

    }

    private void handleIntent(Intent intent) {

        UsbDevice device = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);
        if (device != null) {
            String productID = String.format("0x%04X", device.getProductId() & 0xFFFFF);
            String vendorID = String.format("0x%04X", device.getVendorId() & 0xFFFFF);

            String action = intent.getAction();
            if (UsbManager.ACTION_USB_DEVICE_DETACHED.equals(action)) {
                mRunButton.setEnabled(false);
                mDeviceTextView.setText(R.string.detached);
                addStatus(device.getProductName(), " detached");
                addStatus("VendorId:", vendorID, ", ProductId:", productID);

            } else if (UsbManager.ACTION_USB_DEVICE_ATTACHED.equals(action)) {
                mRunButton.setEnabled(true);
                mDeviceTextView.setText(R.string.attached);
//                addStatus("Manufacturer: ", device.getManufacturerName());
                addStatus(device.getProductName(), " attached");
                addStatus("VendorId:", vendorID, ", ProductId:", productID);

            } else {
                Logger.w("unknown device action: " + action);
            }
        } else {
            showUsbDeviceStatus();
        }

    }

    /**
     * Broadcast receiver to handle USB connection events.
     */
    BroadcastReceiver mUsbReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            handleIntent(intent);
        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(mUsbReceiver);
        if (!mDisposable.isDisposed()) {
            mDisposable.dispose();
        }
    }

    private void mayChangePermission() {
        Observable<Boolean> copyAssetObservable = Observable.create(
                emitter -> {
                    emitter.onNext(initPermission());
                    emitter.onComplete();
                });

        Disposable copyAssetDisposable = copyAssetObservable.subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(result -> {
                    addStatus("init usb permission: " + (result ? "success!" : "failed!"));
                });
        mDisposable.add(copyAssetDisposable);

    }

    /**
     * 1. mount rootfs to read/write
     * 2. change /dev/bus/usb/* permission to 777 in file /ueventd.rc
     * 3. pkill ueventd (will automatically restart)
     */
    public boolean initPermission() {
        List<String> out;
        //check permission without requesting root

        String CHECK_USB_CMD = "cat /ueventd.rc | grep /dev/bus/usb/";
        boolean isUSB777 = false;
        out = Shell.SH.run(CHECK_USB_CMD);
        for (String str : out) {
            if (str.contains("0777")) {
                isUSB777 = true;
                break;
            }
        }
        Logger.d(out);

        String CHECK_SE_CMD = "getenforce";
        out = Shell.SH.run(CHECK_SE_CMD);
        boolean isPermissive = false;
        for (String str : out) {
            if ("Permissive".equals(str)) {
                isPermissive = true;
                break;
            }
        }
        Logger.d(out);

        if (isUSB777 && isPermissive) {
            return true;
        }else {
            Logger.w("permission not ok, begin setting...");
        }

        // set permission
        if (Shell.SU.available()) {
            String MOUNT_CMD = "mount -o rw,remount -t rootfs rootfs /";
            out = Shell.SU.run(MOUNT_CMD);
            if (out == null) {
                Logger.w("cannot execute:" + MOUNT_CMD);
                return false;
            }

            String COPY_CMD = "cp /ueventd.rc /sdcard/";
            out = Shell.SU.run(COPY_CMD);
            if (out == null) {
                Logger.w("cannot execute:" + COPY_CMD);
                return false;
            }

            try {
                Path eventPath = Paths.get(getSdcardPath(), "ueventd.rc");
                List<String> lines = Files.readAllLines(eventPath);
                for (int i = 0; i < lines.size(); i++) {
                    String line = lines.get(i);
                    if (line.startsWith("/dev/bus/usb/*")) {
                        Logger.d("found usb permission line:" + line);
                        line = line.replace("660", "777");
                        lines.set(i, line);
                        Logger.d("new usb permission line:" + line);
                        break;
                    }
                }
                Files.write(eventPath, lines);
            } catch (IOException e) {
                e.printStackTrace();
            }

            String COPY_BACK_CMD = "cp /sdcard/ueventd.rc /";
            out = Shell.SU.run(COPY_BACK_CMD);
            if (out == null) {
                Logger.w("cannot execute:" + COPY_BACK_CMD);
                return false;
            }

            String KILL_CMD = "pkill ueventd";
            out = Shell.SU.run(KILL_CMD);
            if (out == null) {
                Logger.w("cannot execute:" + KILL_CMD);
                return false;
            }

            String ENFORCE_CMD = "/system/bin/setenforce 0";
            out = Shell.SU.run(ENFORCE_CMD);
            if (out == null) {
                Logger.w("cannot execute:" + ENFORCE_CMD);
                return false;
            }

            return true;
        } else {
            return false;
        }
    }

    public native void setCmdFile(String cmdFile);

    public native void setGraphFile(String graphFile);

    public native void setImageFile(String imageFile);

    public native String doInference(String graphFile, String imageFile, int labelOffset);

    public native void setLogLevel(int level);
}
