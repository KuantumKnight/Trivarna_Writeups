# U - Hidden World

## Flag

Not yet verified.

## Solution

Export the supplied Google Doc as DOCX and inspect `word/document.xml`. The visible
string at the top is a decoy: ROT47 turns it into
`UNI6CTF{Wr0ng_F1ag_S4bm1tted}`. Near the bottom of the document is a one-point,
white-on-white hyperlink to a second Google Doc:

```text
https://docs.google.com/document/d/1nzY54zh_N1dDs3lYv5g0TxVlpxS21g9Xc1c5kpgb3dk/edit?usp=sharing
```

The second document contains another explicit decoy,
`UNI6CTF{th1s_1s_4_d3c0y}`, surrounded by a fake prompt-injection message. Its
real payload is made from four zero-width Unicode characters:

```text
U+200C -> 00
U+200D -> 01
U+202C -> 10
U+FEFF -> 11
```

Concatenating those two-bit values and decoding every 16 bits as a character
reveals the next document:

```text
https://docs.google.com/document/d/1IsIl-Z-HYRoLJVIB5ZJ_yDHLKQfGNimxfpX1ZEBaXE4/edit?usp=s
```

The third document uses visibly similar Unicode characters: full-width Latin,
Greek/Cyrillic homoglyphs, and unusual Unicode spaces. The altered region is
exactly 75 characters long. Treat an ordinary ASCII character as `0` and a
Unicode replacement as `1`, then split the resulting stream into five-bit
groups. Mapping `0..25` to `A..Z` and `26` to a space gives:

```text
LMT SCGWPOOCWZR
```

Further decoding is required. Do not treat this intermediate value as a flag.
