# Velostra Vault

Challenge Name: Velostra Vault
Platform: CSEMA / Trivarna
Category: Web / Forensics
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Investigate an offboarding incident, recover the correct vault export from the egress evidence, and unlock the protected archive.

## 2) Key Clues

- The IR portal exposes ticket lookup and an egress capture.
- Employee data identifies Rowan Kestrel, department `LOG`, badge `LX-8842-K`.
- Hidden ticket `#4471` points to the real export.
- `vault_agent` contains the production salt and an argument-order bug.

## 3) Plan

- Authenticate to the portal and enumerate investigation records.
- Follow ticket `#4471` into the packet capture.
- Extract the real export, reverse the restore-agent arguments, and use its TOTP seed.

## 4) Steps

1. **Action:** Inspect the portal’s ticket index and employee directory.

   **Result:** Ticket `#4471` linked Rowan’s pre-offboarding export to the egress mirror.

2. **Action:** Extract transferred objects from `capture.pcap`.

   **Result:** `archive01` contained `vault_export.zip`; the similarly named `archive02` was a decoy.

3. **Action:** Inspect `vault_agent` and its help text.

   **Result:** The documented argument order was reversed. The working call was:

   ```text
   decrypt vault.blob LOG LX-8842-K
   ```

4. **Action:** Use the production salt `VLX-SALT-7f3c9a`, department, badge, and returned TOTP seed.

   **Result:** The generated live code unlocked the vault and returned the flag.

## 5) Solution Summary

The solve required correlating the web portal, ticket database, packet capture, and local restore utility. The main trap was trusting the utility’s help text; its real parser consumed the department and badge in the opposite order.

## 6) Flag

```text
CSEMA{06c8a436b6e87cae1ec5a4e9475e1e75}
```

## 7) Lessons Learned

- Follow cross-artifact identifiers such as ticket numbers.
- Compare program behavior with its help text when arguments fail unexpectedly.
- Distinguish production secrets from deliberately retained legacy/decoy paths.
