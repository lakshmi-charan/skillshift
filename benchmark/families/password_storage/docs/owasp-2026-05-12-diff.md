# OWASP Password Storage Cheat Sheet revision of 2026-05-12 (commit c3c1952)

Source: https://raw.githubusercontent.com/OWASP/CheatSheetSeries/c3c1952/cheatsheets/Password_Storage_Cheat_Sheet.md
License: OWASP Cheat Sheet Series, CC BY-SA 4.0 (https://github.com/OWASP/CheatSheetSeries). Verbatim excerpt; formatting preserved.

Unified diff against the previous revision (02bfdad, 2026-03-26):

```diff
--- 02bfdad (2026-03-26)
+++ c3c1952 (2026-05-12)
@@ -5,5 +5,5 @@
 This cheat sheet advises you on the proper methods for storing passwords for authentication. When passwords are stored, they must be protected from an attacker even if the application or database is compromised. Fortunately, a majority of modern languages and frameworks provide built-in functionality to help store passwords safely.
 
-However, once an attacker has acquired stored password hashes, they are always able to brute force hashes offline. Defenders can slow down offline attacks by selecting hash algorithms that are as resource intensive as possible.
+Passwords should never be stored in plain text. Instead, they must be protected using strong, slow hashing algorithms such as Argon2id, bcrypt, or PBKDF2. A unique salt must be added to each password to prevent attackers from using precomputed lookup tables like rainbow tables. Fast hashing algorithms such as SHA‑256 are not suitable for password storage because they allow attackers to perform large numbers of guesses quickly. Using slow, memory‑hard algorithms makes brute‑force attacks significantly more difficult, expensive, and time‑consuming.
 
 To sum up our recommendations:
@@ -19,5 +19,5 @@
 ### Hashing vs Encryption
 
-Hashing and encryption can keep sensitive data safe, but in almost all circumstances, **passwords should be hashed, NOT encrypted.**
+Hashing and encryption can keep sensitive data safe, but in almost all circumstances, **Passwords should be securely hashed using modern, adaptive hashing algorithms (e.g., Argon2id, bcrypt, or PBKDF2), rather than encrypted or stored in plaintext.**
 
 Because **hashing is a one-way function** (i.e., it is impossible to "decrypt" a hash and obtain the original plaintext value), it is the most appropriate approach for password validation. Even if an attacker obtains the hashed password, they cannot use it to log in as the victim.
@@ -168,7 +168,7 @@
 The work factor for PBKDF2 is implemented through an iteration count, which should set differently based on the internal hashing algorithm used.
 
-- PBKDF2-HMAC-SHA1: 1,400,000 iterations
-- PBKDF2-HMAC-SHA256: 600,000 iterations
+- PBKDF2-HMAC-SHA256: 600,000 iterations (recommended)
 - PBKDF2-HMAC-SHA512: 220,000 iterations
+- PBKDF2-HMAC-SHA1: 1,400,000 iterations — **legacy only**, do not select for new systems. NIST SP 800-131A Rev. 2 disallows SHA-1 for new use after 2030.
 
 ### Parallel PBKDF2
```

Updated summary section (verbatim, c3c1952):

# Password Storage Cheat Sheet

## Introduction

This cheat sheet advises you on the proper methods for storing passwords for authentication. When passwords are stored, they must be protected from an attacker even if the application or database is compromised. Fortunately, a majority of modern languages and frameworks provide built-in functionality to help store passwords safely.

Passwords should never be stored in plain text. Instead, they must be protected using strong, slow hashing algorithms such as Argon2id, bcrypt, or PBKDF2. A unique salt must be added to each password to prevent attackers from using precomputed lookup tables like rainbow tables. Fast hashing algorithms such as SHA‑256 are not suitable for password storage because they allow attackers to perform large numbers of guesses quickly. Using slow, memory‑hard algorithms makes brute‑force attacks significantly more difficult, expensive, and time‑consuming.

To sum up our recommendations:

- **Use [Argon2id](#argon2id) with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism.**
- **If [Argon2id](#argon2id) is not available, use [scrypt](#scrypt) with a minimum CPU/memory cost parameter of (2^17), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1.**
- **For legacy systems using [bcrypt](#bcrypt), use a work factor of 10 or more and with a password limit of 72 bytes.**
- **If FIPS-140 compliance is required, use [PBKDF2](#pbkdf2) with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256.**
- **Consider using a [pepper](#peppering) to provide additional defense in depth (though alone, it provides no additional secure characteristics).**

## Background

### Hashing vs Encryption

Hashing and encryption can keep sensitive data safe, but in almost all circumstances, **Passwords should be securely hashed using modern, adaptive hashing algorithms (e.g., Argon2id, bcrypt, or PBKDF2), rather than encrypted or stored in plaintext.**

Because **hashing is a one-way function** (i.e., it is impossible to "decrypt" a hash and obtain the original plaintext value), it is the most appropriate approach for password validation. Even if an attacker obtains the hashed password, they cannot use it to log in as the victim.

