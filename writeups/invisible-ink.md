# Invisible Ink

Challenge Name: Invisible Ink
Platform: CSEMA / Trivarna
Category: Forensics / PDF
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Find the flag hidden in `compliance_report.pdf`. The visible PDF contains misleading text, so success requires inspecting the document structure.

## 2) Key Clues

- The visible page contains a flag-shaped decoy.
- The PDF has custom page resources named `CSEMFragments`.
- Fragment values are referenced by offsets rather than ordinary display order.

## 3) Plan

- Inspect the PDF object tree and page resources.
- Extract the custom fragment array.
- Reassemble fragments using their explicit offsets, not PDF object order.

## 4) Steps

1. **Action:** Inspect objects and streams with a PDF parser such as `mutool` or `qpdf`.

   **Result:** The rendered text produced `CSEMA{wh1t3_t3xt_1s_n07_1t}`, marked as a decoy by the surrounding evidence.

2. **Action:** Read `/Page/Resources/CSEMFragments`.

   **Result:** Several small strings were stored in a custom array with offset metadata.

3. **Action:** Sort fragments by their recorded offsets and concatenate them.

   **Result:** The fragments formed the actual flag.

4. **Action:** Confirm the result from the raw PDF bytes rather than a viewer export.

   **Result:** The same string was reproduced deterministically.

## 5) Solution Summary

The challenge hid data in a custom PDF resource and deliberately separated physical object order from logical message order. Reading the rendered page alone only exposed the decoy; offset-based reconstruction revealed the flag.

## 6) Flag

```text
CSEMA{0ffs3t_0rd3r_n0t_0bj3ct_0rd3r}
```

## 7) Lessons Learned

- PDF viewers show presentation, not necessarily every object.
- Inspect custom resources and indirect references when text extraction looks suspicious.
- Treat obvious flag strings as candidates until their source layer is verified.
