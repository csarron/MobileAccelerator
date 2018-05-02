package com.cscao.apps.ncsdemo;

import static com.cscao.apps.ncsdemo.Helper.OPENED_PRODUCT_ID;
import static com.cscao.apps.ncsdemo.Helper.PRODUCT_ID;
import static com.cscao.apps.ncsdemo.Helper.VENDOR_ID;
import static com.cscao.apps.ncsdemo.Helper.getNcsPath;
import static com.cscao.apps.ncsdemo.Helper.getPath;
import static com.cscao.apps.ncsdemo.Helper.getStatus;
import static com.qualcomm.qti.snpe.NeuralNetwork.Runtime.CPU;
import static com.qualcomm.qti.snpe.NeuralNetwork.Runtime.DSP;
import static com.qualcomm.qti.snpe.NeuralNetwork.Runtime.GPU;
import static com.qualcomm.qti.snpe.NeuralNetwork.Runtime.GPU_FLOAT16;

import android.Manifest;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.text.SpannableStringBuilder;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.orhanobut.logger.AndroidLogAdapter;
import com.orhanobut.logger.CsvFormatStrategy;
import com.orhanobut.logger.DiskLogAdapter;
import com.orhanobut.logger.FormatStrategy;
import com.orhanobut.logger.Logger;
import com.orhanobut.logger.PrettyFormatStrategy;
import com.qualcomm.qti.snpe.FloatTensor;
import com.qualcomm.qti.snpe.NeuralNetwork;
import com.qualcomm.qti.snpe.SNPE;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

    private String mModelFile;
    private String mImageFile;
    private String mCmdFile;

    private Button mRunNcsButton;
    private Button mRunSnpeButton;
    private Button mRunOffloadButton;

    private TextView mStatusTextView;
    private TextView mDeviceTextView;

    CompositeDisposable mDisposable = new CompositeDisposable();
    private boolean mIsNcsAttached = false;
    private boolean mIsBenchmarking = false;
    private SNPE.NeuralNetworkBuilder mSnpeNetworkBuilder;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mRunNcsButton = findViewById(R.id.run_ncs_btn);
        mRunSnpeButton = findViewById(R.id.run_snpe_btn);
        mRunOffloadButton = findViewById(R.id.run_offload_btn);

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

        mSnpeNetworkBuilder = new SNPE.NeuralNetworkBuilder(getApplication())
                // Allows selecting a runtime order for the network.
                // In the example below use DSP and fall back, in order, to GPU then CPU
                // depending on whether any of the runtime is available.
                .setRuntimeOrder(DSP, GPU, CPU);

        Switch benchSwitch = findViewById(R.id.bench_sw);
        benchSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                addStatus("turn benchmarking on");
                mIsBenchmarking = true;
            } else {
                mIsBenchmarking = false;
                addStatus("turn benchmarking off");
            }

        });
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

    private void updateButtonState() {
        mRunNcsButton.setEnabled(mIsNcsAttached && mModelFile.endsWith(".graph"));
        mRunSnpeButton.setEnabled(mModelFile.endsWith(".dlc"));
    }

    public void mayCopyAsset() {
        mRunNcsButton.setEnabled(false);
        mRunSnpeButton.setEnabled(false);
        addStatus("initializing...");

        Observable<String> copyAssetObservable = Observable.create(
                emitter -> {
                    mCmdFile = copyAssetFileToSdcardNcsDir("mvnc/MvNCAPI.mvcmd");
                    setCmdFile(mCmdFile);
                    emitter.onNext(mCmdFile);

                    mModelFile = copyAssetFileToSdcardNcsDir("mobilenet_v2_1.0_224.graph");
//                    setModelFile(mModelFile);
                    emitter.onNext(mModelFile);

                    mModelFile = copyAssetFileToSdcardNcsDir("mobilenet_v2_1.0_224.dlc");
                    setModelFile(mModelFile);
                    emitter.onNext(mModelFile);

                    mImageFile = copyAssetFileToSdcardNcsDir("chairs.jpg");
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
                        updateButtonState();
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
        if (mIsBenchmarking) {
            return;
        }
        mSpannableBuilder.clear();
        mSpannableBuilder.append(mStatusTextView.getText());
        mSpannableBuilder.append(getStatus(statuses));
        mStatusTextView.setText(mSpannableBuilder, TextView.BufferType.SPANNABLE);
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

                        mIsNcsAttached = true;
                        updateButtonState();
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
            int productID = device.getProductId();
            int vendorID = device.getVendorId();
            String productIDStr = String.format("0x%04X", productID & 0xFFFFF);
            String vendorIDStr = String.format("0x%04X", vendorID & 0xFFFFF);

            String action = intent.getAction();
            if (UsbManager.ACTION_USB_DEVICE_DETACHED.equals(action)) {
                if (vendorID == VENDOR_ID && productID == PRODUCT_ID) {
                    mIsNcsAttached = false;
                    updateButtonState();
                }
                mDeviceTextView.setText(R.string.detached);
                addStatus(device.getProductName(), " detached");
                addStatus("VendorId:", vendorIDStr, ", ProductId:", productIDStr);

            } else if (UsbManager.ACTION_USB_DEVICE_ATTACHED.equals(action)) {
                if (vendorID == VENDOR_ID && productID == PRODUCT_ID) {
                    mIsNcsAttached = true;
                    updateButtonState();
                }
                mDeviceTextView.setText(R.string.attached);
//                addStatus("Manufacturer: ", device.getManufacturerName());
                addStatus(device.getProductName(), " attached");
                addStatus("VendorId:", vendorIDStr, ", ProductId:", productIDStr);

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
        Observable<String> copyAssetObservable = Observable.create(
                emitter -> {
                    emitter.onNext(checkUsbPermission());
                    emitter.onNext(checkSELinuxPermission());
                    emitter.onComplete();
                });

        Disposable copyAssetDisposable = copyAssetObservable.subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(this::addStatus);
        mDisposable.add(copyAssetDisposable);

    }

    public String checkUsbPermission() {
        List<String> checkCmdResults;
        //check permission without requesting root
        String CHECK_USB_CMD = "cat /ueventd.rc | grep /dev/bus/usb/ | grep 777";
        checkCmdResults = Shell.SH.run(CHECK_USB_CMD);
        System.out.println(checkCmdResults);
        boolean isUsbOk = (checkCmdResults != null && !checkCmdResults.isEmpty());

        if (isUsbOk) {
            return "USB permission is good";
        } else {
            if (Shell.SU.available()) {
                return setUsbPermission();
            } else {
                return "Root access is not available or denied";
            }
        }
    }

    private String setUsbPermission() {
        // change permission commands
        String MOUNT_CMD = "mount -o rw,remount -t rootfs rootfs /";
        String CHANGE_CMD = "sed -i 's/\\(\\/dev\\/bus\\/usb\\/\\* .*\\)0660/\\10777/g' "
                + "/ueventd.rc";
        String KILL_CMD = "pkill ueventd";

        for (String cmd : new String[]{MOUNT_CMD, CHANGE_CMD, KILL_CMD}) {
            List<String> cmdResults = Shell.SU.run(cmd);
            if (cmdResults == null) {
                Logger.w("Cannot execute:" + cmd);
                return "Cannot execute: " + cmd;
            }
        }
        return "Successfully set USB permission";
    }

    public String checkSELinuxPermission() {
        List<String> checkCmdResults;
        //check permission without requesting root
        String CHECK_SE_CMD = "getenforce | grep Permissive";
        checkCmdResults = Shell.SH.run(CHECK_SE_CMD);

        boolean isPermissive = (checkCmdResults != null && !checkCmdResults.isEmpty());

        if (isPermissive) {
            return "SELinux is permissive (good)";
        } else {
            if (Shell.SU.available()) {
                return setSELinux();
            } else {
                return "Root access is not available or denied";
            }
        }
    }

    private String setSELinux() {
        String ENFORCE_CMD = "/system/bin/setenforce 0";
        List<String> seResults = Shell.SU.run(ENFORCE_CMD);
        if (seResults == null) {
            Logger.w("Cannot set SELinux to permissive!");
            return "Cannot set SELinux to permissive!";
        }
        return "Successfully set SELinux to permissive";
    }

    private static final int MODEL_REQUEST_CODE = 1;
    private static final int IMAGE_REQUEST_CODE = 2;

    public void selectModel(View view) {
        performFileSelection(MODEL_REQUEST_CODE);
    }

    public void selectImage(View view) {
        performFileSelection(IMAGE_REQUEST_CODE);
    }

    public void performFileSelection(int requstCode) {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");

        startActivityForResult(intent, requstCode);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode,
            Intent resultData) {
        if (requestCode == MODEL_REQUEST_CODE && resultCode == Activity.RESULT_OK) {

            if (resultData != null) {
                Uri uri = resultData.getData();
                if (uri != null) {
                    Logger.d(uri);
                    String modelFile = getPath(this, uri);
                    if (modelFile != null) {
                        mRunNcsButton.setEnabled(false);
                        mRunSnpeButton.setEnabled(false);

                        if (modelFile.endsWith(".graph") || modelFile.endsWith(".dlc")) {
                            mModelFile = modelFile;
                            addStatus("selected model: ", modelFile);
                            updateButtonState();
                        } else {
                            addStatus("selected invalid model: ", modelFile);
                            addStatus("model should end with either .graph or .dlc !");
                        }
                    } else {
                        addStatus("path cannot be resolved, uri is:", uri.toString());
                    }
                } else {
                    addStatus("uri is null!");
                }
            } else {
                Logger.w("request model no result data!");
            }
        } else if (requestCode == IMAGE_REQUEST_CODE && resultCode == Activity.RESULT_OK) {

            if (resultData != null) {
                Uri uri = resultData.getData();
                if (uri != null) {
                    Logger.d(uri);
                    String imageFile = getPath(this, uri);
                    mImageFile = imageFile;
                    addStatus("selected image: ", imageFile);
                } else {
                    addStatus("uri is null!");
                }
            } else {
                Logger.w("request image no result data!");
            }
        } else {
            Logger.w("unknown request code: " + requestCode);
        }
    }

    private String doSnpeInference(String modelFile, String imageFile) {
        long startTime = System.currentTimeMillis();

        try {
            NeuralNetwork network = mSnpeNetworkBuilder.setModel(new File(modelFile))
                    .build();
            runOnUiThread(() -> addStatus("running snpe on: " + network.getRuntime().name()));
            long modelInitTime = System.currentTimeMillis();

            FloatTensor inputTensor = network.createFloatTensor(
                    network.getInputTensorsShapes().get("input:0"));

            int[] dimensions = inputTensor.getShape();

//            Logger.d("input names: " + network.getInputTensorsNames()
//                    + " dims: " + Arrays.toString(dimensions));

            if (dimensions[0] != dimensions[1]) {
                Logger.w("image height and width not equal: " + Arrays.toString(dimensions));
            }

            float[] pixelFloats = getImageFloats(imageFile, dimensions[0], dimensions[1]);
            inputTensor.write(pixelFloats, 0, pixelFloats.length);

            final Map<String, FloatTensor> inputs = new HashMap<>();
            inputs.put("input:0", inputTensor);

            long beginTime = System.currentTimeMillis();
            final Map<String, FloatTensor> outputsMap = network.execute(inputs);

            FloatTensor outputTensor = outputsMap.get("output:0");

            final float[] outputValues = new float[outputTensor.getSize()];
            outputTensor.read(outputValues, 0, outputValues.length);
            long endTime = System.currentTimeMillis();

            String resultStr = decodePredictions(outputValues, 0);
            long cleanTime = System.currentTimeMillis();

            network.release();
            long finishTime = System.currentTimeMillis();

            long initTime = modelInitTime - startTime;
            long inputTime = beginTime - modelInitTime;
            long executeTime = endTime - beginTime;
            long outputTime = cleanTime - endTime;
            long cleanUpTime = finishTime - cleanTime;

            String timeStr = " init: " + initTime + " ms"
                    + " input: " + inputTime + " ms"
                    + " infer: " + executeTime + " ms"
                    + " output: " + outputTime + " ms"
                    + " clean: " + cleanUpTime + " ms"
                    + " total: " + (finishTime - startTime) + " ms";
            return resultStr + timeStr;
//            final List<String> result = new LinkedList<>();
//            for (Map.Entry<String, FloatTensor> output : outputsMap.entrySet()) {
//                final FloatTensor tensor = output.getValue();
//                final float[] values = new float[tensor.getSize()];
//                tensor.read(values, 0, values.length);
//                // Process the output ...
//            }

        } catch (IOException e) {
            e.printStackTrace();
        }


        return "snpe failed";
    }

    public String doNcsInference(String graphFile, String imageFile) {
        long startTime = System.currentTimeMillis();

        long deviceHandle = openNcsDevice(0);
        long graphHandle = loadNcsModel(graphFile, deviceHandle);

        long modelInitTime = System.currentTimeMillis();

        float[] imageData = getImageFloats(imageFile, 224, 224);

        long beginTime = System.currentTimeMillis();

        float[] predictions = inferOnNcs(graphHandle, imageData);
        long endTime = System.currentTimeMillis();

        float[] layerTimes = getNcsLayerTimes(graphHandle, 200);
        float sum = 0;
        for (float layerTime : layerTimes) {
            sum += layerTime;
        }
        System.out.println(sum);
        String resultStr = decodePredictions(predictions, 0);

        long cleanTime = System.currentTimeMillis();
        cleanUpNcs(graphHandle, deviceHandle);
        long finishTime = System.currentTimeMillis();

        long initTime = modelInitTime - startTime;
        long inputTime = beginTime - modelInitTime;
        long executeTime = endTime - beginTime;
        long outputTime = cleanTime - endTime;
        long cleanUpTime = finishTime - cleanTime;

        String timeStr = " init: " + initTime + " ms"
                + " input: " + inputTime + " ms"
                + " infer: " + sum + " ms"
                + " output: " + outputTime + " ms"
                + " clean: " + cleanUpTime + " ms"
                + " total: " + (finishTime - startTime) + " ms";
        return resultStr + timeStr;
    }


    public native float[] getImageFloats(String imageFile, int width, int height);

    public native String decodePredictions(float[] predictions, int labelOffset);

    public native void setCmdFile(String cmdFile);

    public native void setModelFile(String modelFile);

    public native void setImageFile(String imageFile);

//    public native String doNcsInference(String graphFile, String imageFile, int labelOffset);

    public native void setLogLevel(int level);

    // return device handle
    public native long openNcsDevice(int index);

    // return model graph handle
    public native long loadNcsModel(String modelFile, long deviceHandle);

    public native float[] inferOnNcs(long graphHandle, float[] imageData);

    public native float[] getNcsLayerTimes(long graphHandle, int maxLayers);


    public native void cleanUpNcs(long graphHandle, long deviceHandle);

    public void onRadioButtonClicked(View view) {

        RadioButton radioButton = (RadioButton) view;
        switch (view.getId()) {
            case R.id.dsp_rb:
                if (mSnpeNetworkBuilder.isRuntimeSupported(DSP)) {
                    addStatus("selected SNPE on DSP");
                    mSnpeNetworkBuilder.setRuntimeOrder(DSP);
                } else {
                    addStatus("SNPE on DSP is not available");
                    radioButton.setChecked(false);
                    radioButton.setEnabled(false);
                }
                break;
            case R.id.gpu_rb:
                if (mSnpeNetworkBuilder.isRuntimeSupported(GPU)) {
                    addStatus("selected SNPE on GPU");
                    mSnpeNetworkBuilder.setRuntimeOrder(GPU);
                } else {
                    addStatus("SNPE on GPU is not available");
                    radioButton.setChecked(false);
                    radioButton.setEnabled(false);
                }
                break;
            case R.id.gpu_16_rb:
                if (mSnpeNetworkBuilder.isRuntimeSupported(GPU_FLOAT16)) {
                    addStatus("selected SNPE on GPU_FLOAT16");
                    mSnpeNetworkBuilder.setRuntimeOrder(GPU_FLOAT16);
                } else {
                    addStatus("SNPE on GPU_FLOAT16 is not available");
                    radioButton.setChecked(false);
                    radioButton.setEnabled(false);
                }
                break;
            default:
                addStatus("selected SNPE on CPU");
                mSnpeNetworkBuilder.setRuntimeOrder(CPU);

        }
    }

    public void runInference(View view) {
        Observable<String> ncsObservable;
        switch (view.getId()) {
            case R.id.run_ncs_btn:
                addStatus("using ncs model: ", mModelFile, " image: ", mImageFile);
                addStatus("begin doing ncs inference...");
                ncsObservable = Observable.create(
                        emitter -> {
                            String results = doNcsInference(mModelFile, mImageFile);
                            emitter.onNext(results);
                            emitter.onComplete();
                        });

                break;
            case R.id.run_offload_btn:
                addStatus("selected offload");
                ncsObservable = Observable.create(
                        emitter -> {
//                            String results = doNcsInference(mModelFile, mImageFile);
//                            emitter.onNext(results);
//                            emitter.onComplete();
                        });
                break;
            default:
                addStatus("using snpe model: ", mModelFile, " image: ", mImageFile);
                addStatus("begin doing snpe inference...");
                ncsObservable = Observable.create(
                        emitter -> {
                            String results = doSnpeInference(mModelFile, mImageFile);
                            emitter.onNext(results);
                            emitter.onComplete();
                        });
        }


        Disposable ncsDisposable = ncsObservable.subscribeOn(Schedulers.computation())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(result -> {
                    addStatus(result);
                    updateButtonState();
                });
        mDisposable.add(ncsDisposable);
    }
}
