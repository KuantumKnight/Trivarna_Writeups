# The Seven-Stage Breach — Forensic Write-up

## Current result

The supplied evidence supports a coherent compromise chain from a phishing link through payload execution, command-and-control activity, attacker VPN access, and PsExec-based lateral movement to the domain controller.

The final archive, `target/exfil_data.zip`, has also been identified and characterized. It is a valid WinZip AES-256 encrypted ZIP containing `flag.txt` and a sample customer database. However, its password has not been recovered. The available logs and packet capture do not contain the archive bytes, its password, an observed archive-creation command, or an exfiltration request body. Substantial targeted and dictionary cracking has also produced no password.

Accordingly, this report reconstructs the seven stages as far as the evidence permits, but it does **not** invent a flag. The defensible current conclusion is that the narrative portion is solvable from the artifacts while the archive key is either hidden by a mechanism not yet identified, outside the supplied evidence, or unintentionally omitted from the challenge.

## Evidence layout

The original challenge package is:

```text
The_Seven-Stage_Breach.zip
```

Its SHA-256 digest is:

```text
0248d4c20298335aa624a9cbf43630f054018fc859b310098e38b926f63d9bcd
```

The archive was extracted under:

```text
evidence/The Seven-Stage Breach/
```

The supplied artifacts are:

| Category | Artifact | Size (bytes) | Purpose |
|---|---|---:|---|
| Email | `email/phishing_email.eml` | 766 | Initial-access lure and malicious URL |
| Memory-derived timeline | `forensics/memory_timeline.csv` | 200,966 | Process and connection observations |
| Web server | `logs/apache.log` | 183,530 | Internal API activity |
| DNS | `logs/dns.log` | 247,085 | C2 name-resolution activity |
| Firewall | `logs/firewall.log` | 266,500 | Outbound traffic to the attacker address |
| Linux authentication | `logs/linux_auth.log` | 268,550 | SSH access from the VPN-assigned address |
| Web server | `logs/nginx.log` | 174,250 | Administrative web access |
| Proxy | `logs/proxy.log` | 220,668 | Malware download and C2 HTTP POSTs |
| Windows Security | `logs/security.log` | 350,610 | Network logons and malicious service installation |
| Sysmon | `logs/sysmon.log` | 336,478 | PowerShell and PsExec process creation |
| VPN | `logs/vpn.log` | 225,983 | Attacker VPN connection and assigned address |
| Network capture | `pcap/enterprise_traffic.pcap` | 177,514 | DNS-like, HTTP beacon, and SMB-like traffic |
| Encrypted collection | `target/exfil_data.zip` | 543 | Encrypted flag and customer-data sample |

Selected integrity hashes:

| Artifact | SHA-256 |
|---|---|
| `email/phishing_email.eml` | `1bd2f74715622ccc243c2bc3427270f7046ae9abe4ca5a987002154a58149512` |
| `pcap/enterprise_traffic.pcap` | `4e40c0f0e227535c035a7a443bf857974ee12c4528d4e9e160ba72705f4eb602` |
| `target/exfil_data.zip` | `a9d737d292225bcf808581dee1058a63f3ffd5e20bd1fa3130e3b2693fff8a4b` |

## Executive incident narrative

The intended victim was `john.doe` on workstation `WS-JDOE`, associated with internal address `192.168.1.105`. The victim received an urgent invoice-themed email that linked to an executable disguised with a double extension: `invoice_99824.pdf.exe`.

The proxy then recorded the workstation downloading that file directly from `c2-telecom-breach.com` at `198.51.100.77`. Sysmon recorded that executable launching PowerShell with execution-policy bypass and an encoded argument, and a memory-derived process record independently showed `powershell.exe` running shortly afterward.

The compromised workstation communicated with the C2 infrastructure through repeated DNS queries and HTTP POST requests. The same external IP later established a VPN session as `vpn_ext_user99` and received internal address `10.8.0.45`, giving the attacker a second route into the environment.

Windows Security and Sysmon then recorded installation and execution of `PSEXESVC` on `DC01`, while the packet capture shows repetitive SMB-like traffic from `192.168.1.105` to `192.168.1.10:445` containing the marker `TreeConnect PSEXESVC`. This is strong evidence of PsExec-style remote service execution and lateral movement to the domain controller.

The challenge provides an encrypted archive containing `flag.txt` and `exfiltrated_customer_db_sample.csv`, which represents the intended collection/exfiltration objective. That final stage is only partially evidenced, though: none of the supplied telemetry shows the command that created the archive, the actual customer-data query, an HTTP upload body, or the archive traversing the network.

## Detailed seven-stage reconstruction

### Stage 1 — Phishing delivery and initial access

The phishing email contains the following headers and lure:

```text
From: "Billing Dept" <billing-alert@c2-telecom-breach.com>
To: "John Doe" <john.doe@telecom-corp.local>
Subject: URGENT: Overdue Infrastructure Invoice #99824
Date: Mon, 03 Aug 2026 07:11:30 -0400
Message-ID: <20260803071130.99824@c2-telecom-breach.com>
```

The embedded URL is:

```text
http://c2-telecom-breach.com/downloads/invoice_99824.pdf.exe
```

The final `.exe` extension is the important detail. The name is designed to appear like a PDF invoice while actually delivering a Windows executable.

**Assessment:** Confirmed phishing delivery. User interaction is strongly implied by the subsequent download and execution, though the logs do not contain a literal click event.

**Likely ATT&CK mapping:** T1566.002, Spearphishing Link; T1204.002, User Execution: Malicious File.

### Stage 2 — Malicious payload retrieval

The proxy recorded the victim downloading the linked executable:

```text
2026-08-03 07:13:20
source: 192.168.1.105
user: john.doe
method: GET
URL: http://c2-telecom-breach.com/downloads/invoice_99824.pdf.exe
upstream: DIRECT/198.51.100.77
response size: 458921
content type: application/x-msdownload
```

This joins the email identity, victim address, malicious domain, payload filename, and C2 IP in a single event. The MIME type also confirms that the downloaded object was treated as a Windows executable rather than a PDF.

**Assessment:** Confirmed payload retrieval from attacker infrastructure.

### Stage 3 — Payload execution and PowerShell

Sysmon recorded process creation on `WS-JDOE`:

```text
Time: 2026-08-03 07:16:40
Event ID: 1
Host: WS-JDOE
User: TELECOM\john.doe
Image: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
Command line: powershell.exe -ExecutionPolicy Bypass -Enc Qnljb2RlRG93bmxvYWREYXRh
Parent image: C:\Users\john.doe\Downloads\invoice_99824.pdf.exe
MD5: a1b2c3d4e5f678901234567890abcdef
```

At `07:20:00`, the memory timeline independently contains a `pslist` entry for `powershell.exe`, PID `4892`, parent PID `3102`, using the standard PowerShell path. That record corroborates the process-creation log.

The encoded token was examined rather than accepted at face value. Ordinary Base64 decoding gives:

```text
BycodeDownloadData
```

PowerShell's `-EncodedCommand` convention normally expects UTF-16LE bytes. Decoding those same bytes as UTF-16LE does not yield a valid PowerShell command. It produces nonsensical Unicode text. Therefore the argument appears to be a synthetic clue or malformed placeholder, not a faithfully executable encoded command. `BycodeDownloadData` may be intended to evoke a download method, but it should not be reported as a real command without qualification.

The MD5 value is also conspicuously patterned and is probably synthetic rather than a genuine malware digest.

**Assessment:** Execution is confirmed. The exact PowerShell behavior is not recoverable from the encoded argument as supplied.

**Likely ATT&CK mapping:** T1059.001, PowerShell; T1204.002, User Execution: Malicious File.

### Stage 4 — Command and control

The DNS log shows repeated resolution attempts from `192.168.1.105` for both:

```text
c2-telecom-breach.com
cmd.c2-telecom-breach.com
```

The anomalous query times include:

```text
07:07:30
07:22:30
07:42:30
08:02:30
08:22:30
```

The proxy also contains three C2 POSTs from `john.doe` at `192.168.1.105`:

```text
2026-08-03 07:33:20 POST http://c2-telecom-breach.com/c2/gate.php
2026-08-03 08:06:40 POST http://c2-telecom-breach.com/c2/gate.php
2026-08-03 08:40:00 POST http://c2-telecom-breach.com/c2/gate.php
```

Each request is routed directly to `198.51.100.77`, has content type `application/octet-stream`, and records a size of 512 bytes. The firewall log is dominated by outbound traffic from the victim workstation to `198.51.100.77:80`, further supporting continuing communication.

The packet capture later shows 600 HTTP requests of this form:

```http
GET /beacon/poll?id=0 HTTP/1.1
Host: c2-telecom-breach.com
```

The `id` value increments through `599`. These are beacons or synthetic representations of beacons; the capture does not contain the earlier POST bodies.

**Assessment:** Confirmed command-and-control activity over web protocols, with DNS used to locate or identify the C2 infrastructure.

**Likely ATT&CK mapping:** T1071.001, Web Protocols; possibly T1071.004, DNS.

### Stage 5 — External VPN access with a compromised account

At `07:40:00`, the VPN log records:

```text
vpn_ext_user99/198.51.100.77:44301 Peer Connection Initiated
vpn_ext_user99/198.51.100.77:44301 MULTI: primary virtual IP for vpn_ext_user99: 10.8.0.45
```

This is especially significant because `198.51.100.77` is already the malware download and C2 address. The attacker therefore used the same infrastructure to authenticate to the corporate VPN as `vpn_ext_user99`, receiving internal address `10.8.0.45`.

The Linux authentication log repeatedly reports accepted public-key logins for `deploy_user` from `10.8.0.45:54122`. Nginx also records requests from `10.8.0.45` to `/admin/dashboard`. These provide supporting evidence that the VPN address was used to access internal Linux and web assets. However, those files contain highly repetitive entries without a unique transition event, so they cannot safely establish a precise one-event chronology.

**Assessment:** Confirmed attacker VPN session; downstream internal access is supported but represented by synthetic/repetitive telemetry.

**Likely ATT&CK mapping:** T1133, External Remote Services; T1078, Valid Accounts.

### Stage 6 — Lateral movement with PsExec

At `07:49:20`, Windows Security Event ID 7045 records installation of a service:

```text
Service name: PSEXESVC
Service file: %SystemRoot%\PSEXESVC.exe
Service type: user mode service
Start account: LocalSystem
```

At `07:50:00`, Sysmon Event ID 1 on `DC01` records:

```text
User: NT AUTHORITY\SYSTEM
Image: C:\Windows\PSEXESVC.exe
Command line: C:\Windows\PSEXESVC.exe
Parent image: C:\Windows\System32\services.exe
MD5: f9e8d7c6b5a43210f9e8d7c6b5a43210
```

The packet capture contains 600 TCP packets from:

```text
192.168.1.105:44500 -> 192.168.1.10:445
```

Their repeated payload ends with:

```text
TreeConnect PSEXESVC
```

Taken together, the service-install event, SYSTEM process on `DC01`, destination TCP/445, and `PSEXESVC` packet marker make the intended interpretation unambiguous: the attacker used PsExec-style SMB service execution to move laterally to `DC01`, which is likely `192.168.1.10`.

As with the PowerShell event, the recorded MD5 looks intentionally patterned and should not be treated as a real-world malware hash without validation.

**Assessment:** Confirmed remote service installation and execution consistent with PsExec lateral movement.

**Likely ATT&CK mapping:** T1021.002, SMB/Windows Admin Shares; T1569.002, Service Execution.

### Stage 7 — Collection, staging, and exfiltration

The challenge supplies `target/exfil_data.zip`, a 543-byte encrypted archive. Its directory contains:

| Entry | Uncompressed size | Packed size | Recorded modification time |
|---|---:|---:|---|
| `flag.txt` | 122 | 145 | 2026-08-03 18:25:16 |
| `exfiltrated_customer_db_sample.csv` | 95 | 96 | 2026-08-03 18:25:16 |

The archive uses WinZip AES encryption with AES-256/AE-2 and Deflate compression. Both files are encrypted, and there is no ZIP comment. AE-2 archives commonly store a zero CRC because authentication is supplied by the AES format, so the zero CRC is not itself evidence of corruption.

The filenames clearly represent the intended final objective: collection of a customer-data sample and the challenge flag. The earlier C2 channel provides a plausible exfiltration path.

Nevertheless, the telemetry does **not** directly observe:

- a database query or export command;
- the process that created `exfil_data.zip`;
- a compression command or its password;
- a POST body containing customer data;
- the ZIP signature or encrypted archive bytes in the PCAP;
- a network transfer whose bytes hash to the supplied archive.

For that reason, the defensible statement is that collection/staging is represented by the supplied target archive and exfiltration is intended or inferred from the scenario and C2 activity. It is not fully demonstrated at the byte-transfer level by the provided logs.

**Assessment:** Intended collection is strongly supported by the archive; actual archive creation and transfer are not directly observed.

**Likely ATT&CK mapping:** T1560.001, Archive via Utility, and T1041, Exfiltration Over C2 Channel, both inferential in this dataset.

## Consolidated timeline

| Time on 2026-08-03 | Source | Event | Confidence |
|---|---|---|---|
| 07:07:30 | DNS | First listed C2-domain query from `192.168.1.105` | High as an artifact; chronology is inconsistent |
| 07:11:30 -0400 | Email | Invoice phishing message sent to John Doe | High |
| 07:13:20 | Proxy | `invoice_99824.pdf.exe` downloaded from C2 IP | High |
| 07:16:40 | Sysmon | Payload launches PowerShell with bypass and encoded token | High |
| 07:20:00 | Memory timeline | `powershell.exe` observed in process list | High |
| 07:22:30 | DNS | Repeated C2-domain resolution | High |
| 07:33:20 | Proxy | First recorded POST to `/c2/gate.php` | High |
| 07:40:00 | VPN | `vpn_ext_user99` connects from C2 IP and receives `10.8.0.45` | High |
| 07:42:30 | DNS | Repeated C2-domain resolution | High |
| 07:49:20 | Security | `PSEXESVC` service installed | High |
| 07:50:00 | Sysmon | `PSEXESVC.exe` runs as SYSTEM on `DC01` | High |
| 08:02:30 | DNS | Repeated C2-domain resolution | High |
| 08:06:40 | Proxy | Second recorded POST to `/c2/gate.php` | High |
| 08:22:30 | DNS | Repeated C2-domain resolution | High |
| 08:40:00 | Proxy | Third recorded POST to `/c2/gate.php` | High |
| 08:55:16.246–08:55:16.495 EDT | PCAP | 1,800 synthetic/repetitive DNS, HTTP, and SMB-like packets | High |
| 18:25:16 | ZIP metadata | Both encrypted members' recorded modification time | High as metadata only |

### Timeline caveats

The first C2 DNS lookup predates the phishing email by about four minutes. That cannot fit a literal sequence in which this email is the sole cause of the first C2 contact. Plausible explanations include unsynchronized clocks, synthetic log generation, prior compromise/beaconing, or an intentionally planted anomaly. There is not enough evidence to select one conclusively.

The archive's internal modification time is also many hours after the primary logs and packet capture. ZIP timestamps are easily controlled and are not reliable enough to repair the chronology by themselves.

Several log sources consist almost entirely of repeated template records. This reinforces that the dataset is challenge-generated and that exact counts should not be interpreted as realistic production activity.

## Packet-capture analysis

### Capture summary

The capture contains 1,800 raw IPv4 packets over only about 0.248 seconds:

```text
First packet: 2026-08-03 08:55:16.246627 EDT
Last packet:  2026-08-03 08:55:16.494828 EDT
Duration:     0.248201 seconds
Link type:    Raw IPv4
```

It divides evenly into three groups:

| Traffic class | Packets | Source | Destination | Interpretation |
|---|---:|---|---|---|
| UDP/DNS-like | 600 | `192.168.1.105` | `192.168.1.1:53` | Repeated C2-domain lookup representation |
| TCP/HTTP | 600 | `192.168.1.105:54321` | `198.51.100.77:80` | `/beacon/poll?id=N` requests |
| TCP/SMB-like | 600 | `192.168.1.105:44500` | `192.168.1.10:445` | Repeated `TreeConnect PSEXESVC` marker |

The HTTP conversation totals about 62 KB and the SMB-like conversation about 47 KB. No TCP handshake or normal protocol exchange is represented; the capture is essentially a stream of crafted evidence packets.

### DNS payload issue

The DNS-like packets repeat this payload:

```text
0100000100000000000063322d74656c65636f6d2d6272656163682e636f6d0000010001
```

It embeds the ASCII string `c2-telecom-breach.com`, but the name is not encoded with valid DNS label-length bytes. Packet decoders therefore report all 600 packets as malformed. This supports the view that the PCAP is illustrative rather than a faithful network capture.

### Search for an embedded key or archive

The following possible covert channels were examined:

- source-port low and high bytes;
- differences between consecutive source ports;
- IP and transport checksum bytes;
- packet timestamp deltas;
- individual bit planes and parity in candidate numeric fields;
- forward and reverse bit ordering;
- the incrementing HTTP `id` values;
- categorical mappings of repeated DNS/VPN log values;
- TCP sequence numbers and IP identification fields;
- raw payload searches for ZIP signatures, filenames, passwords, or flag-like strings.

No meaningful printable stream, ZIP header, key phrase, credential, or archive payload emerged. TCP sequence numbers and IP IDs follow simple deterministic progressions, while the application payloads are constant except for the numeric HTTP beacon identifier.

This does not mathematically rule out every possible steganographic construction, but it rules out the conventional encodings suggested by the fields and repetition in this capture.

## Archive analysis and password-recovery status

### Confirmed archive properties

```text
Path: target/exfil_data.zip
Size: 543 bytes
SHA-256: a9d737d292225bcf808581dee1058a63f3ffd5e20bd1fa3130e3b2693fff8a4b
Encryption: WinZip AES-256, AE-2
Compression: Deflate
Members: flag.txt, exfiltrated_customer_db_sample.csv
```

Each member has its own salt, as expected for WinZip AES. There is no archive comment or visible extra metadata containing a password.

### Candidate material tested

Candidate generation incorporated essentially every obvious clue from the evidence, including:

- the malicious domain and subdomain;
- `198.51.100.77`, `192.168.1.105`, `192.168.1.10`, and `10.8.0.45`;
- usernames `john.doe`, `vpn_ext_user99`, and `deploy_user`;
- `invoice_99824`, the full payload filename, and invoice-number variants;
- `PSEXESVC`, `DC01`, `WS-JDOE`, and service/path variants;
- `/c2/gate.php`, `/beacon/poll`, and administrative routes;
- ports `80`, `445`, `44301`, `44500`, `54321`, and `54122`;
- the encoded PowerShell token and its decoded ASCII text;
- email subject, message ID, dates, and timestamps;
- supplied MD5/SHA-256 values and fragments;
- challenge-title variants, seven-stage terminology, kill-chain terminology, and ATT&CK-related words;
- capitalization, separators, years, common suffixes, leetspeak, two-token and three-token combinations, and numeric hybrids.

### Cracking coverage completed

The archive hash was extracted in a format accepted by John the Ripper. Completed attempts include:

- the approximately 14-million-entry `rockyou` list;
- a roughly 10-million-entry top-password collection;
- several additional public password lists available locally;
- rule-based mutations of high-probability entries;
- corporate-themed jumbo candidate generation;
- extensive artifact-derived dictionaries and hybrids;
- exhaustive numeric candidates of lengths 1 through 7;
- exhaustive lowercase candidates of lengths 1 through 5;
- exhaustive alphanumeric candidates of lengths 1 through 4;
- targeted date, invoice, IP, port, hostname, username, and service combinations.

No candidate produced a valid password.

### Why the flag cannot yet be reported

AES-256 itself cannot be bypassed from the small amount of ciphertext. Recovery requires the password, a weakness in its generation, or an actual plaintext/key leak elsewhere. The two encrypted files are too small to enable a practical generic cryptographic attack, and the AE-2 authentication data allows candidate verification but not password derivation.

The important negative finding is that the evidence collection does not expose the password through the obvious forensic paths. Continuing with larger blind dictionaries or a GPU mask attack may eventually succeed if the password is merely weak, but that would be guessing rather than reconstructing a key from the supplied incident evidence.

Current flag status:

```text
NOT RECOVERED — encrypted archive password remains unknown
```

## Indicators of compromise

| Type | Indicator | Context |
|---|---|---|
| Domain | `c2-telecom-breach.com` | Phishing sender domain, malware hosting, HTTP C2 |
| Domain | `cmd.c2-telecom-breach.com` | DNS C2-related lookup |
| IPv4 | `198.51.100.77` | Payload host, C2 server, and VPN source |
| IPv4 | `192.168.1.105` | Victim workstation address |
| IPv4 | `192.168.1.10` | Likely `DC01`, SMB lateral-movement destination |
| IPv4 | `10.8.0.45` | VPN address assigned to attacker session |
| User | `john.doe` / `TELECOM\john.doe` | Initial compromised user |
| User | `vpn_ext_user99` | Attacker-used VPN identity |
| User | `deploy_user` | Linux public-key access identity |
| Host | `WS-JDOE` | Initial victim workstation |
| Host | `DC01` | Lateral-movement target/domain controller |
| File | `invoice_99824.pdf.exe` | Initial malicious payload |
| File/service | `PSEXESVC.exe` / `PSEXESVC` | Remote service execution artifact |
| URL | `/downloads/invoice_99824.pdf.exe` | Payload retrieval path |
| URL | `/c2/gate.php` | C2 POST endpoint |
| URL | `/beacon/poll?id=N` | Captured beacon endpoint |
| Port | TCP/80 | Malware download and C2 |
| Port | TCP/445 | SMB/PsExec lateral movement |
| Port | UDP/53 | DNS-like C2 name resolution |

The IP ranges used by the challenge include documentation/test ranges, another indication that these are simulated indicators rather than globally attributable infrastructure.

## Evidence quality and limitations

This dataset contains multiple signs of synthetic generation:

- the first C2 lookup occurs before the phishing email;
- the PowerShell Base64 token is not a valid UTF-16LE encoded command;
- both displayed MD5 values are conspicuously patterned;
- many logs contain thousands of nearly identical records;
- every DNS packet in the PCAP is malformed in the same way;
- the PCAP compresses 1,800 packets into a quarter-second and omits realistic handshakes;
- the SMB payload is a text marker rather than a normal SMB exchange;
- the archive timestamp is not aligned with the primary incident window;
- the final transfer payload and archive-creation telemetry are absent.

These do not invalidate the intended seven-stage story, but they limit how literally individual timestamps and protocol details can be interpreted. The strongest conclusions are those supported by two or more independent artifacts, especially download-to-process and service-install-to-PsExec correlations.

## Reproduction commands

The following commands illustrate the principal analysis steps. Paths assume execution from the workspace root.

List and hash the evidence:

```bash
unzip -l The_Seven-Stage_Breach.zip
sha256sum The_Seven-Stage_Breach.zip
find 'evidence/The Seven-Stage Breach' -type f -print0 | xargs -0 sha256sum
```

Inspect the phishing message and identify anomalous records:

```bash
sed -n '1,200p' 'evidence/The Seven-Stage Breach/email/phishing_email.eml'
rg -n 'c2-telecom-breach|invoice_99824|PSEXESVC|vpn_ext_user99|10\.8\.0\.45|powershell' \
  'evidence/The Seven-Stage Breach'
```

Decode the PowerShell token as ordinary Base64:

```bash
printf '%s' 'Qnljb2RlRG93bmxvYWREYXRh' | base64 -d
```

Summarize the packet capture:

```bash
tshark -r 'evidence/The Seven-Stage Breach/pcap/enterprise_traffic.pcap' -q -z io,phs
tshark -r 'evidence/The Seven-Stage Breach/pcap/enterprise_traffic.pcap' -q -z conv,tcp
tshark -r 'evidence/The Seven-Stage Breach/pcap/enterprise_traffic.pcap' \
  -Y http.request -T fields -e ip.src -e ip.dst -e http.request.method -e http.host -e http.request.uri
```

Inspect the encrypted archive:

```bash
7z l -slt 'evidence/The Seven-Stage Breach/target/exfil_data.zip'
zipinfo -v 'evidence/The Seven-Stage Breach/target/exfil_data.zip'
zip2john 'evidence/The Seven-Stage Breach/target/exfil_data.zip'
```

## Defensive response recommendations

For a real incident with this evidence, immediate actions would be:

1. Isolate `WS-JDOE` and `DC01` while preserving volatile memory and disk images.
2. Terminate the `vpn_ext_user99` session and disable or reset that account.
3. Disable or reset `john.doe`, `deploy_user`, and any credentials/tokens exposed on the affected hosts.
4. Block and hunt for `c2-telecom-breach.com`, `cmd.c2-telecom-breach.com`, and `198.51.100.77` across DNS, proxy, firewall, EDR, and email telemetry.
5. Hunt for `invoice_99824.pdf.exe`, PowerShell children of user-download executables, and execution-policy bypass commands.
6. Find and remove unauthorized `PSEXESVC` services and determine every system reached through SMB/admin shares.
7. Review domain-controller logons, privilege changes, replication activity, directory-service access, and credential-dumping indicators.
8. Investigate all activity sourced from VPN address `10.8.0.45`, including the public-key access by `deploy_user` and visits to `/admin/dashboard`.
9. Search endpoint, database, DLP, web, and proxy telemetry for `exfil_data.zip`, `flag.txt`, `exfiltrated_customer_db_sample.csv`, ZIP signatures, and transfers near or after the recorded archive timestamp.
10. Reissue affected SSH keys, VPN credentials, privileged service credentials, and potentially domain credentials based on the DC impact assessment.

## Final conclusion

The best-supported seven-stage chain is:

```text
Phishing link
  -> executable download
  -> payload launches PowerShell
  -> DNS/HTTP command and control
  -> attacker VPN access using vpn_ext_user99
  -> PsExec/SMB lateral movement to DC01
  -> customer-data collection and intended exfiltration
```

Stages 1 through 6 are supported by direct artifacts, with execution and lateral movement each corroborated across multiple sources. Stage 7 is represented by the encrypted target archive and the surrounding C2 context, but the collection and transfer mechanics are absent.

The archive is genuine and cryptographically protected, not merely renamed or trivially encoded. No password has been recovered from the supplied clues or completed cracking coverage. Until a key-bearing artifact, intended derivation rule, or successful password candidate is found, no trustworthy flag value can be supplied.
