#!/usr/bin/env bash
set -u

rename_if_free() {
  local old="$1" new="$2"
  if [ -d "$old" ] && [ ! -e "$new" ]; then
    mv -- "$old" "$new"
  fi
}

# Correct obvious naming variants. These are directory renames only.
rename_if_free 'Cipher Cascade' 'U - Cipher Cascade'
rename_if_free 'gjost freq' 'Ghost Frequency'
rename_if_free 'ghost command' 'Ghost Command'
rename_if_free 'bootloader trust' 'Bootloader Trust'
rename_if_free 'silent pairing' 'Silent Pairing'
rename_if_free 'operationtricolor' 'Operation Tricolor: The Weak PKI'
rename_if_free 'operationtricolor:adminforgery' 'Operation Tricolor: The Forged Admin Token'
rename_if_free 'HIDDENWORLDULTRA' 'U - Hidden World (HIDDENWORLDULTRA)'

# Every challenge gets a directory. mkdir is additive and never removes files.
while IFS= read -r name; do
  [ -n "$name" ] && mkdir -p -- "$name"
done <<'CHALLENGES'
U - Cipher Cascade
U - Midnight NAND Reliquary
Azad Bharat
U - Saffron Glitch Badge
U - My First IOT
U - Loose Lips
U - AI Conversation Forensics
U - Parade Order
U - Signal Sabha
U - Latern Booth
U - Citadel Dispatch
U - Azadi Ledger
U- The Internet Never Forgets - FREE FLAG
Velostra Vault
Leaky Stream
Same k, Twice
Double Lock
Shared Secret
Invisible Ink
Frame Drop
Carved Secret
Ghost Frequency
Buried Plane
VaultX Wallet
U - Silk Dispatch
Operation Shadow Backup
Operation Black Vault
Registry Analysis
Timeline Reconstruction
Android Forensics
Browser Forensics
Deleted File Recovery
U - New Destiny
The Flight Window
U - Saffron Echoes in Old Delhi
U - Image Chain
U - Cipher Chain
U - Hidden World
U - One Among a Thousand
U - The Endless Archive
U - Digital Footprints 3
U - Digital Footprints 2
The Seven-Stage Breach
U - Digital Footprints 1
Echoes of Exfiltration
The Silent VoIP Call
U - Echoes of Freedom
Ghosts in the Smart Office
U - Independence Secret
Operation Tricolor: The Weak PKI
Operation Tricolor: The Forged Admin Token
U - Tricolour Victory
Operation Tricolor: The Captured Admin Token
U - Operation Digital Sentry
Operation Tricolor: The Leaked Router Token
U - Modern Indian Strength
Sensor Fusion
Intercepted Independence Activation SMS
Ghost Command
Silent Pairing
Bootloader Trust
Operation Tricolor: The Weak PKI
CHALLENGES

# Download only when the expected artifact is not already in that challenge tree.
download_if_missing() {
  local dir="$1" url="$2" file="$3"
  if ! find "$dir" -type f -name "$file" -size +0c -print -quit 2>/dev/null | grep -q .; then
    if ! curl -L --fail --silent --show-error --output "$dir/$file" "$url"; then
      printf 'DOWNLOAD_FAILED %s/%s\n' "$dir" "$file" >&2
    fi
  fi
}

download_if_missing 'U - Midnight NAND Reliquary' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments_BxuEwtD.zip' 'attachments_BxuEwtD.zip'
download_if_missing 'U - Saffron Glitch Badge' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments_VhuJ9RF.tgz' 'attachments_VhuJ9RF.tgz'
download_if_missing 'U - My First IOT' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/my-first-iot.tgz' 'my-first-iot.tgz'
download_if_missing 'U - Parade Order' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments.json' 'attachments.json'
download_if_missing 'U - Signal Sabha' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments_VLWOpSP.tgz' 'attachments_VLWOpSP.tgz'
download_if_missing 'U - Latern Booth' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments_hgXAXjf.zip' 'attachments_hgXAXjf.zip'
download_if_missing 'U - Citadel Dispatch' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments_UvpPpFC.zip' 'attachments_UvpPpFC.zip'
download_if_missing 'U - Azadi Ledger' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments.tgz' 'attachments.tgz'
download_if_missing 'Leaky Stream' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/chal_YungDiw.zip' 'chal_YungDiw.zip'
download_if_missing 'Same k, Twice' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/auth_log_bundle.json' 'auth_log_bundle.json'
download_if_missing 'Double Lock' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/chal_WHZ50JK.zip' 'chal_WHZ50JK.zip'
download_if_missing 'Shared Secret' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/chal.zip' 'chal.zip'
download_if_missing 'Invisible Ink' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/compliance_report.pdf' 'compliance_report.pdf'
download_if_missing 'Frame Drop' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/hallway_frames.zip' 'hallway_frames.zip'
download_if_missing 'Carved Secret' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/panel_export.png' 'panel_export.png'
download_if_missing 'Ghost Frequency' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/hub_audio_log.wav' 'hub_audio_log.wav'
download_if_missing 'Buried Plane' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/hub_snapshot.png' 'hub_snapshot.png'
download_if_missing 'VaultX Wallet' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/player_files.zip' 'player_files.zip'
download_if_missing 'U - Silk Dispatch' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/attachments.zip' 'attachments.zip'
download_if_missing 'Operation Shadow Backup' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/ctf_player_files.zip' 'ctf_player_files.zip'
download_if_missing 'Operation Black Vault' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/players_files.zip' 'players_files.zip'
download_if_missing 'Registry Analysis' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/hives.zip' 'hives.zip'
download_if_missing 'Timeline Reconstruction' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/mft_extract.raw.zip' 'mft_extract.raw.zip'
download_if_missing 'Android Forensics' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/backup.ab' 'backup.ab'
download_if_missing 'Browser Forensics' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/chromium_profile.zip' 'chromium_profile.zip'
download_if_missing 'Deleted File Recovery' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/evidence.img.zip' 'evidence.img.zip'
download_if_missing 'U - New Destiny' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/verifier.blob' 'verifier.blob'
download_if_missing 'The Flight Window' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/The_Flight_Window.zip' 'The_Flight_Window.zip'
download_if_missing 'U - One Among a Thousand' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/UNI6CTF_QR.zip' 'UNI6CTF_QR.zip'
download_if_missing 'U - The Endless Archive' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/2500.zip' '2500.zip'
download_if_missing 'The Seven-Stage Breach' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/The_Seven-Stage_Breach.zip' 'The_Seven-Stage_Breach.zip'
download_if_missing 'Echoes of Exfiltration' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Echoes_of_Exfiltration.zip' 'Echoes_of_Exfiltration.zip'
download_if_missing 'The Silent VoIP Call' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/The_Silent_VoIP_Call.zip' 'The_Silent_VoIP_Call.zip'
download_if_missing 'U - Echoes of Freedom' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Audio_Challenge.zip' 'Audio_Challenge.zip'
download_if_missing 'U - Independence Secret' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Challenge_QR.png' 'Challenge_QR.png'
download_if_missing 'Operation Tricolor: The Weak PKI' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Operation_Tricolor_The_Weak_PKI.zip' 'Operation_Tricolor_The_Weak_PKI.zip'
download_if_missing 'Operation Tricolor: The Forged Admin Token' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Operation_Tricolor_The_Forged_Admin_Token.zip' 'Operation_Tricolor_The_Forged_Admin_Token.zip'
download_if_missing 'U - Tricolour Victory' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/india_independence_day.jpg' 'india_independence_day.jpg'
download_if_missing 'Operation Tricolor: The Captured Admin Token' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Operation_Tricolor_The_Captured_Admin_Token.zip' 'Operation_Tricolor_The_Captured_Admin_Token.zip'
download_if_missing 'Operation Tricolor: The Leaked Router Token' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Operation_Tricolor_The_Leaked_Router_Token.zip' 'Operation_Tricolor_The_Leaked_Router_Token.zip'
download_if_missing 'Intercepted Independence Activation SMS' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/Intercepted_Independence_Activation_SMS.zip' 'Intercepted_Independence_Activation_SMS.zip'
download_if_missing 'Ghost Command' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/botclient_armhf_stripped' 'botclient_armhf_stripped'
download_if_missing 'Silent Pairing' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/hub_capture.json' 'hub_capture.json'
download_if_missing 'Bootloader Trust' 'https://csem.ip-167-235-30-42.swiftwave.xyz/media/event_challenge_files/smartlock_fw_v2.csfw' 'smartlock_fw_v2.csfw'
