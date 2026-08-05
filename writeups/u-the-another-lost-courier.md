# U - The Another Lost Courier

Challenge Name: U - The Another Lost Courier
Platform: UNI6CTF / Trivarna
Category: Web / OSINT
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Trace a courier-themed web application through its legacy infrastructure and recover the reconstructed message from response metadata.

## 2) Key Clues

- The service used a signed session cookie and random eight-hex-character routes.
- A JavaScript comment named the document, stylesheet, favicon, and status requests.
- Response headers carried fragments in ETags, timing values, favicon checksums, and `/api/status`.
- Rate limiting trusted `X-Forwarded-For`.

## 3) Plan

- Preserve the session cookie while following redirects.
- Inspect the explicitly named assets and compare their response headers.
- Use a spoofed forwarding identity only to avoid the rate-limit noise, then concatenate the authoritative fragments.

## 4) Steps

1. **Action:** Request the landing page with a cookie jar.

   **Result:** The random route was session-bound; requests without the cookie returned a misleading 404.

2. **Action:** Inspect the document, stylesheet, favicon, and status responses named by the page.

   **Result:** Their metadata fragments formed the beginning and middle of a bracketed message.

3. **Action:** Send bounded requests with a changed `X-Forwarded-For` value.

   **Result:** The flawed rate limiter accepted the requests, allowing `/api/status` to be checked reliably.

4. **Action:** Concatenate the ETag, timing, favicon, and status fragments in the documented order.

   **Result:** The complete reconstructed flag was obtained.

## 5) Solution Summary

The challenge’s main idea was reading metadata across an HTTP chain. The session cookie preserved the route state, while the trusted forwarding header made the rate limiter bypassable. The actual flag was assembled from response metadata rather than a hidden file.

## 6) Flag

```text
UNI6CTF{[ARCHIVE]->[LEGACY_INFRASTRUCTURE]->[COURIER_TRAIL]->[RECONSTRUCTED]}
```

## 7) Lessons Learned

- Retain cookies when a site uses session-bound redirects.
- Read response headers and status APIs, not only page bodies.
- Treat rate-limit bypasses as a way to improve observation reliability, not as the final objective.
