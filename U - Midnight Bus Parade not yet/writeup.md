# U - Midnight Bus Parade not yet

## Challenge information

- Category: Hardware
- Difficulty: Medium
- Points: 150
- Artifact: `parade_capture.csv`
- Supporting note: `board_note.txt`

The challenge provides an eight-channel logic-analyzer export containing several buses simultaneously, deliberately planted flag-looking strings, and a configuration stream.

## Files and channel map

The archive contains:

```text
attachments/board_note.txt
attachments/parade_capture.csv
```

The channel assignment is:

```text
D0 = SCL       D1 = SDA
D2 = SCK       D3 = MOSI
D4 = MISO      D5 = CS_N
D6 = UART_TX   D7 = spare trigger
```

The note also specifies:

```text
UART: 115200 baud, 8N1, idle high
SPI:  mode 0, chip select active low
I2C:  7-bit address 0x50
date: 15-08-1947
```

The CSV is a transition-row export rather than a row-per-sample waveform. Each row gives the complete channel state at a timestamp, so decoders must detect edges and retain the most recent state between rows.

## Initial inspection

```bash
unzip -l challenge.zip
unzip -o challenge.zip -d extracted
file extracted/attachments/*
wc -l extracted/attachments/parade_capture.csv
```

The capture has 16,523 data rows. Its timing exposes several independent clocks:

- SPI edges are concentrated in the sub-microsecond range.
- I²C activity is on D0/D1.
- UART transitions on D6 are approximately 8,701 ns apart, consistent with the supplied 115200-baud setting after timestamp quantization.

## I²C decoding

I²C was decoded by detecting start/stop conditions, sampling SDA on SCL rising edges, and grouping eight data bits followed by an ACK bit.

The first byte is `0xa0`, the write-form address byte for the 7-bit device address `0x50`. The following bytes contain this visible decoy:

```text
UNI6CTF{EEPROM_VISIBLE_FAKE_1947}
```

The stream then contains a packet marker and a binary-looking region:

```text
00 ff 56 46 48 57 00 25 a7 ...
         V  F  H  W
```

The marker `VFHW` is significant because the SPI configuration independently identifies it as the packet marker.

The EEPROM stream also ends with another readable decoy:

```text
UNI6CTF{ADDR_50_IS_NOT_ENOUGH}
```

These strings are not the final flag; they are deliberately visible ceremonial material.

## SPI decoding

SPI was decoded using mode 0 semantics: sample data on the rising edge of SCK while CS_N is low. There is one long transaction. MOSI is mostly zero padding, while MISO contains the useful configuration text:

```text
CFG{order=sha256(15-08-1947|chakra-order);xor=15-08-1947|midnight-bus;packet=VFHW;fake=UNI6CTF{SPI_CONFIG_FAKE_FLAG}}
```

The SPI-visible flag is another decoy:

```text
UNI6CTF{SPI_CONFIG_FAKE_FLAG}
```

The meaningful fields are:

```text
order  = sha256(15-08-1947|chakra-order)
xor    = 15-08-1947|midnight-bus
packet = VFHW
```

The `order` and `xor` fields must be kept separate. They are different challenge components/stages:

- The ordering stage uses the `chakra-order` seed/material to reconstruct packet order.
- The XOR stage uses the distinct literal key `15-08-1947|midnight-bus`.

Do not XOR with the SHA-256 digest merely because the configuration mentions SHA-256. The digest-related value is the ordering clue; the literal date-and-bus string is the XOR key.

## Recovering the ordering permutation

The binary I²C records have the form of an index followed by two bytes, separated by `0xa7`. Ignoring initial packet-length material and the trailing decoy, the record indices appear in this capture order:

```text
21, 3, 18, 9, 6, 8, 32, 0, 1, 16, 24, 2, 10, 28,
15, 5, 12, 30, 4, 13, 19, 35, 11, 22, 25, 36, 20, 33,
7, 29, 23, 27, 26, 14, 31, 34, 17
```

This is a permutation of indices `0..36`. It is reproduced by the deterministic shuffle convention used to create the capture:

```python
import random

order = list(range(37))
random.Random("15-08-1947|chakra-order").shuffle(order)
print(order)
```

The output is the permutation above. Therefore the ordering seed is:

```text
15-08-1947|chakra-order
```

The SPI text describes this stage as `sha256(...)`; the practical reconstruction must preserve the ordering convention and must not substitute the XOR key.

## Record sanity check

For a record with index `i`, its two value bytes satisfy:

```text
byte_a XOR byte_b == 0x5a XOR i
```

For example, record zero is:

```text
[0, 0x35, 0x6f]
0x35 XOR 0x6f == 0x5a
```

This validates alignment of the I²C decoder, but it does not produce the final message. Treating either visible I²C flag or this relation as the answer leads to a decoy.

## UART decoding

UART uses D6, idle high, 8N1. A decoder should:

1. Locate a falling edge from idle high to the start bit.
2. Sample at the center of the start bit, eight data bits, and stop bit.
3. Interpret data bits least-significant-bit first.
4. Validate start and stop bits.
5. Advance by a complete 10-bit frame so falling data edges are not mistaken for new starts.

The capture contains misleading edges and repeated material. A decoder that treats every falling edge as a new frame over-accepts bytes and produces more than 400 apparent bytes. A frame-aware decoder produces a much smaller stream and is the correct basis for the final reconstruction.

An exploratory decoder is included as [`decode_capture.py`](./decode_capture.py). It demonstrates the SPI and I²C parsing and prints the decoy/configuration material described above.

## Decoys found

The recovered flag-shaped strings are:

```text
UNI6CTF{EEPROM_VISIBLE_FAKE_1947}
UNI6CTF{SPI_CONFIG_FAKE_FLAG}
UNI6CTF{ADDR_50_IS_NOT_ENOUGH}
```

None is intended as the answer. The SPI configuration explicitly labels one as `fake=`, and the others are placed in visible I²C/trailing regions.

## Current conclusion

Reliable recovered values:

```text
packet marker: VFHW
ordering seed: 15-08-1947|chakra-order
XOR key:       15-08-1947|midnight-bus
I²C address:   0x50
```

The ordering seed and XOR key belong to different stages/challenges and must be handled independently. The visible flags are confirmed decoys. The final controller message is expected from the correctly framed UART payload after applying the ordering stage and then the separate literal XOR key.
