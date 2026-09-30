# Mozilla Server Side TLS guidelines 5.7

Source: https://raw.githubusercontent.com/mozilla/ssl-config-generator/99178dc/docs/guidelines/5.7.json
Source: https://raw.githubusercontent.com/mozilla/ssl-config-generator/99178dc/docs/guidelines/CHANGELOG.md
Fetched: 2026-09-29
License: Mozilla ssl-config-generator (https://github.com/mozilla/ssl-config-generator), MPL-2.0. Verbatim copy; formatting preserved.

## CHANGELOG.md (verbatim section)

```markdown
## [5.7] - 2023-05-15

### Changed

- `intermediate` configuration in order to append `TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
  to the bottom of the cipher list for `iana` and `openssl`. [mozilla/server-side-tls#285](https://github.com/mozilla/server-side-tls/issues/285)
```

## Machine-generated diff of the guideline JSON (5.6.json -> 5.7.json, difflib)

```diff
--- 5.6.json
+++ 5.7.json
@@ -1,4 +1,4 @@
 {
-    "version": 5.6,
-    "href": "https://ssl-config.mozilla.org/guidelines/5.6.json",
+    "version": 5.7,
+    "href": "https://ssl-config.mozilla.org/guidelines/5.7.json",
     "configurations": {
@@ -60,3 +60,4 @@
                     "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
-                    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256"
+                    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
+                    "TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
                 ],
@@ -70,3 +71,4 @@
                     "DHE-RSA-AES128-GCM-SHA256",
-                    "DHE-RSA-AES256-GCM-SHA384"
+                    "DHE-RSA-AES256-GCM-SHA384",
+                    "DHE-RSA-CHACHA20-POLY1305"
                 ]
```

## 5.7.json (verbatim)

```json
{
    "version": 5.7,
    "href": "https://ssl-config.mozilla.org/guidelines/5.7.json",
    "configurations": {
        "modern": {
            "certificate_curves": ["prime256v1", "secp384r1"],
            "certificate_signatures": ["ecdsa-with-SHA256", "ecdsa-with-SHA384", "ecdsa-with-SHA512"],
            "certificate_types": ["ecdsa"],
            "ciphers": {
                "caddy": [],
                "go": [],
                "iana": [],
                "openssl": []
            },
            "ciphersuites": [
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            ],
            "dh_param_size": null,
            "ecdh_param_size": 256,
            "hsts_min_age": 63072000,
            "maximum_certificate_lifespan": 90,
            "ocsp_staple": true,
            "oldest_clients": ["Firefox 63", "Android 10.0", "Chrome 70", "Edge 75", "Java 11", "OpenSSL 1.1.1", "Opera 57", "Safari 12.1"],
            "recommended_certificate_lifespan": 90,
            "rsa_key_size": null,
            "server_preferred_order": false,
            "tls_curves": ["X25519", "prime256v1", "secp384r1"],
            "tls_versions": ["TLSv1.3"]
        },
        "intermediate": {
            "certificate_curves": ["prime256v1", "secp384r1"],
            "certificate_signatures": ["sha256WithRSAEncryption", "ecdsa-with-SHA256", "ecdsa-with-SHA384", "ecdsa-with-SHA512"],
            "certificate_types": ["ecdsa", "rsa"],
            "ciphers": {
                "caddy": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
                ],
                "go": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305"
                ],
                "iana": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
                ],
                "openssl": [
                    "ECDHE-ECDSA-AES128-GCM-SHA256",
                    "ECDHE-RSA-AES128-GCM-SHA256",
                    "ECDHE-ECDSA-AES256-GCM-SHA384",
                    "ECDHE-RSA-AES256-GCM-SHA384",
                    "ECDHE-ECDSA-CHACHA20-POLY1305",
                    "ECDHE-RSA-CHACHA20-POLY1305",
                    "DHE-RSA-AES128-GCM-SHA256",
                    "DHE-RSA-AES256-GCM-SHA384",
                    "DHE-RSA-CHACHA20-POLY1305"
                ]
            },
            "ciphersuites": [
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            ],
            "dh_param_size": 2048,
            "ecdh_param_size": 256,
            "hsts_min_age": 63072000,
            "maximum_certificate_lifespan": 366,
            "ocsp_staple": true,
            "oldest_clients": ["Firefox 27", "Android 4.4.2", "Chrome 31", "Edge", "IE 11 on Windows 7", "Java 8u31", "OpenSSL 1.0.1", "Opera 20", "Safari 9"],
            "recommended_certificate_lifespan": 90,
            "rsa_key_size": 2048,
            "server_preferred_order": false,
            "tls_curves": ["X25519", "prime256v1", "secp384r1"],
            "tls_versions": ["TLSv1.2", "TLSv1.3"]
        },
        "old": {
            "certificate_curves": ["prime256v1", "secp384r1"],
            "certificate_signatures": ["sha256WithRSAEncryption"],
            "certificate_types": ["rsa"],
            "ciphers": {
                "caddy": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
                ],
                "go": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305",
                    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_RSA_WITH_AES_128_CBC_SHA256",
                    "TLS_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
                ],
                "iana": [
                    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
                    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
                    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
                    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
                    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
                    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
                    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
                    "TLS_RSA_WITH_AES_128_GCM_SHA256",
                    "TLS_RSA_WITH_AES_256_GCM_SHA384",
                    "TLS_RSA_WITH_AES_128_CBC_SHA256",
                    "TLS_RSA_WITH_AES_256_CBC_SHA256",
                    "TLS_RSA_WITH_AES_128_CBC_SHA",
                    "TLS_RSA_WITH_AES_256_CBC_SHA",
                    "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
                ],
                "openssl": [
                    "ECDHE-ECDSA-AES128-GCM-SHA256",
                    "ECDHE-RSA-AES128-GCM-SHA256",
                    "ECDHE-ECDSA-AES256-GCM-SHA384",
                    "ECDHE-RSA-AES256-GCM-SHA384",
                    "ECDHE-ECDSA-CHACHA20-POLY1305",
                    "ECDHE-RSA-CHACHA20-POLY1305",
                    "DHE-RSA-AES128-GCM-SHA256",
                    "DHE-RSA-AES256-GCM-SHA384",
                    "DHE-RSA-CHACHA20-POLY1305",
                    "ECDHE-ECDSA-AES128-SHA256",
                    "ECDHE-RSA-AES128-SHA256",
                    "ECDHE-ECDSA-AES128-SHA",
                    "ECDHE-RSA-AES128-SHA",
                    "ECDHE-ECDSA-AES256-SHA384",
                    "ECDHE-RSA-AES256-SHA384",
                    "ECDHE-ECDSA-AES256-SHA",
                    "ECDHE-RSA-AES256-SHA",
                    "DHE-RSA-AES128-SHA256",
                    "DHE-RSA-AES256-SHA256",
                    "AES128-GCM-SHA256",
                    "AES256-GCM-SHA384",
                    "AES128-SHA256",
                    "AES256-SHA256",
                    "AES128-SHA",
                    "AES256-SHA",
                    "DES-CBC3-SHA"
                ]
            },
            "ciphersuites": [
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            ],
            "dh_param_size": 1024,
            "ecdh_param_size": 256,
            "hsts_min_age": 63072000,
            "maximum_certificate_lifespan": 366,
            "ocsp_staple": true,
            "oldest_clients": ["Firefox 1", "Android 2.3", "Chrome 1", "Edge 12", "IE8 on Windows XP", "Java 6", "OpenSSL 0.9.8", "Opera 5", "Safari 1"],
            "recommended_certificate_lifespan": 90,
            "rsa_key_size": 2048,
            "server_preferred_order": true,
            "tls_curves": ["X25519", "prime256v1", "secp384r1"],
            "tls_versions": ["TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
        }
    }
}
```
