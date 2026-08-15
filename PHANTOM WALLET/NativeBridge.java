package com.phantom.wallet.crypto;

public final class NativeBridge {
  static { System.loadLibrary("phantomcore"); }
  public static native byte[] nativeDeriveMaterial(byte[] a, byte[] b);
  public static native byte[] nativeBackupVeil(byte[] a);
  public static native String nativeBuildInfo();
  public static native int nativeQrChecksum(byte[] a);
  public static native long nativeReceiptSignature(long a);
}
