# Echoes of Exfiltration

Challenge Name: Echoes of Exfiltration
Platform: CSEMA / Trivarna
Category: Network Forensics
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover data covertly exfiltrated through ICMP traffic. Success means extracting and decoding the hidden report containing the flag.

## 2) Key Clues

- `icmp_capture.pcap` contains suspicious echo traffic.
- `firewall.log` identifies the communicating hosts.
- Relevant packets use IPv4 identification `4919` (`0x1337`).
- Payloads begin with `DAT:` and use sequence numbers.

## 3) Plan

- Filter the PCAP to the suspicious source, destination, and IP ID.
- Sort payload fragments by ICMP sequence number.
- Hex-decode, XOR with the low byte of `0x1337`, and test compression formats.

## 4) Steps

1. **Action:** Correlate `firewall.log` with the packet capture.

   **Result:** The suspicious flow was `192.168.1.105 → 203.0.113.88`.

2. **Action:** Isolate echo requests with IP ID `0x1337` and extract the bytes following `DAT:`.

   **Result:** Thirteen marked packets produced a single ordered high-entropy blob.

3. **Action:** Sort by sequence number, concatenate, and hex-decode.

   **Result:** The decoded bytes were still XOR-obfuscated.

4. **Action:** XOR every byte with `0x37`.

   **Result:** The data began with `78 9c`, the signature of a zlib stream.

5. **Action:** Decompress the zlib payload.

   **Result:** The recovered report explicitly contained the flag and stated that exfiltration used ICMP echo data.

## 5) Solution Summary

The covert channel used normal-looking ICMP echo requests as transport. A packet marker selected the fragments, sequence numbers restored their order, the IP ID supplied the XOR byte, and zlib compression produced the final report.

## 6) Flag

```text
flag{1cmp_c0v3r7_c64nn3l_3xf1l7r4710n}
```

## 7) Lessons Learned

- Correlate network logs before decoding every packet in a capture.
- IP header fields can carry both selectors and key material.
- Check magic bytes after each transform; `78 9c` immediately suggested zlib.
