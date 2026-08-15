import com.phantom.wallet.crypto.NativeBridge;
import java.util.*;
public class Harness {
  static byte[] hx(String s) { int n=s.length(); byte[] b=new byte[n/2]; for(int i=0;i<n;i+=2)b[i/2]=(byte)Integer.parseInt(s.substring(i,i+2),16); return b; }
  static String hex(byte[] b) { StringBuilder s=new StringBuilder(); for(byte x:b)s.append(String.format("%02x",x&255)); return s.toString(); }
  public static void main(String[] args) {
    System.out.println(NativeBridge.nativeBuildInfo());
    byte[] out=NativeBridge.nativeDeriveMaterial(hx(args[0]), args.length>2 ? args[1].getBytes(java.nio.charset.StandardCharsets.UTF_8) : hx(args[1]));
    System.out.println(out == null ? "null" : (out.length + " " + hex(out)));
  }
}
