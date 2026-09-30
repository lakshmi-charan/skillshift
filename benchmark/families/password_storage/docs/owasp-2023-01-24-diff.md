# OWASP Password Storage Cheat Sheet revision of 2023-01-24 (commit f14bc4c)

Source: https://raw.githubusercontent.com/OWASP/CheatSheetSeries/f14bc4c/cheatsheets/Password_Storage_Cheat_Sheet.md
License: OWASP Cheat Sheet Series, CC BY-SA 4.0 (https://github.com/OWASP/CheatSheetSeries). Verbatim excerpt; formatting preserved.

Unified diff against the previous revision (422ec84, 2022-06-10):

```diff
--- 422ec84 (2022-06-10)
+++ f14bc4c (2023-01-24)
@@ -9,8 +9,8 @@
 This cheat sheet provides guidance on the various areas that need to be considered related to storing passwords. In short:
 
-- **Use [Argon2id](#argon2id) with a minimum configuration of 15 MiB of memory, an iteration count of 2, and 1 degree of parallelism.**
-- **If [Argon2id](#argon2id) is not available, use [scrypt](#scrypt) with a minimum CPU/memory cost parameter of (2^16), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1.**
+- **Use [Argon2id](#argon2id) with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism.**
+- **If [Argon2id](#argon2id) is not available, use [scrypt](#scrypt) with a minimum CPU/memory cost parameter of (2^17), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1.**
 - **For legacy systems using [bcrypt](#bcrypt), use a work factor of 10 or more and with a password limit of 72 bytes.**
-- **If FIPS-140 compliance is required, use [PBKDF2](#pbkdf2) with a work factor of 310,000 or more and set with an internal hash function of HMAC-SHA-256.**
+- **If FIPS-140 compliance is required, use [PBKDF2](#pbkdf2) with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256.**
 - **Consider using a [pepper](#peppering) to provide additional defense in depth (though alone, it provides no additional secure characteristics).**
 
@@ -45,5 +45,5 @@
 - Dictionaries or wordlists of common passwords
 
-While the number of permutations can be enormous with high speed hardware (such as GPUs) and cloud services with many servers for rent, the cost to an attacker is relatively small to do successful password cracking especially when best practices for hashing are not followed.
+While the number of permutations can be enormous, with high speed hardware (such as GPUs) and cloud services with many servers for rent, the cost to an attacker is relatively small to do successful password cracking especially when best practices for hashing are not followed.
 
 **Strong passwords stored with modern hashing algorithms and using hashing best practices should be effectively impossible for an attacker to crack.**  It is your responsibility as an application owner to select a modern hashing algorithm.
@@ -94,12 +94,15 @@
 ### Argon2id
 
-[Argon2](https://en.wikipedia.org/wiki/Argon2) is the winner of the 2015 [Password Hashing Competition](https://password-hashing.net). There are three different versions of the algorithm, and the Argon2id variant should be used, as it provides a balanced approach to resisting both side-channel and GPU-based attacks.
+[Argon2](https://en.wikipedia.org/wiki/Argon2) is the winner of the 2015 [Password Hashing Competition](https://en.wikipedia.org/wiki/Password_Hashing_Competition). There are three different versions of the algorithm, and the Argon2id variant should be used, as it provides a balanced approach to resisting both side-channel and GPU-based attacks.
 
 Rather than a simple work factor like other algorithms, Argon2id has three different parameters that can be configured. Argon2id should use one of the following configuration settings as a base minimum which includes the minimum memory size (m), the minimum number of iterations (t) and the degree of parallelism (p).
 
-- m=37 MiB, t=1, p=1
-- m=15 MiB, t=2, p=1
+- m=47104 (46 MiB), t=1, p=1 (Do not use with Argon2i)
+- m=19456 (19 MiB), t=2, p=1 (Do not use with Argon2i)
+- m=12288 (12 MiB), t=3, p=1
+- m=9216 (9 MiB), t=4, p=1
+- m=7168 (7 MiB), t=5, p=1
 
-Both of these configuration settings are equivalent in the defense they provide. The only difference is a trade off between CPU and RAM usage.
+These configuration settings are equivalent in the defense they provide. The only difference is a trade off between CPU and RAM usage.
 
 ### scrypt
@@ -109,9 +112,9 @@
 Like [Argon2id](#argon2id), scrypt has three different parameters that can be configured. scrypt should use one of the following configuration settings as a base minimum which includes the minimum CPU/memory cost parameter (N), the blocksize (r) and the degree of parallelism (p).
 
-- N=2^16 (64 MiB), r=8 (1024 bytes), p=1
-- N=2^15 (32 MiB), r=8 (1024 bytes), p=2
-- N=2^14 (16 MiB), r=8 (1024 bytes), p=4
-- N=2^13 (8 MiB), r=8 (1024 bytes), p=8
-- N=2^12 (4 MiB), r=8 (1024 bytes), p=15
+- N=2^17 (128 MiB), r=8 (1024 bytes), p=1
+- N=2^16 (64 MiB), r=8 (1024 bytes), p=2
+- N=2^15 (32 MiB), r=8 (1024 bytes), p=3
+- N=2^14 (16 MiB), r=8 (1024 bytes), p=5
+- N=2^13 (8 MiB), r=8 (1024 bytes), p=10
 
 These configuration settings are equivalent in the defense they provide. The only difference is a trade off between CPU and RAM usage.
@@ -121,5 +124,5 @@
 The [bcrypt](https://en.wikipedia.org/wiki/bcrypt) password hashing function should be the second choice for password storage if Argon2id is not available or PBKDF2 is required to achieve FIPS-140 compliance.
 
-The minimum work factor for bcrypt should be 10.
+The work factor should be as large as verification server performance will allow, with a minimum of 10.
 
 #### Input Limits
@@ -139,11 +142,15 @@
 The work factor for PBKDF2 is implemented through an iteration count, which should set differently based on the internal hashing algorithm used.
 
-- PBKDF2-HMAC-SHA1: 720,000 iterations
-- PBKDF2-HMAC-SHA256: 310,000 iterations
-- PBKDF2-HMAC-SHA512: 120,000 iterations
+- PBKDF2-HMAC-SHA1: 1,300,000 iterations
+- PBKDF2-HMAC-SHA256: 600,000 iterations
+- PBKDF2-HMAC-SHA512: 210,000 iterations
 
-These configuration settings are equivalent in the defense they provide.
+These configuration settings are equivalent in the defense they provide. ([Number as of december 2022, based on testing of RTX 4000 GPUs](https://tobtu.com/minimum-password-settings/))
 
-When PBKDF2 is used with an HMAC, and the password is longer than the hash function's block size (64 bytes for SHA-256), the password will be automatically pre-hashed. For example, the password "This is a password longer than 512 bits which is the block size of SHA-256" is converted to the hash value (in hex) fa91498c139805af73f7ba275cca071e78d78675027000c99a9925e2ec92eedd. A good implementation of PBKDF2 will perform this step before the expensive iterated hashing phase, but some implementations perform the conversion on each iteration. This can make hashing long passwords significantly more expensive than hashing short passwords. If a user can supply very long passwords, there is a potential denial of service vulnerability, such as the one published in [Django](https://www.djangoproject.com/weblog/2013/sep/15/security/) in 2013. Manual [pre-hashing](#pre-hashing-passwords) can reduce this risk but requires adding a [salt](#salting) to the pre-hash step.
+#### PBKDF2 Pre-hashing
+
+When PBKDF2 is used with an HMAC, and the password is longer than the hash function's block size (64 bytes for SHA-256), the password will be automatically pre-hashed. For example, the password "This is a password longer than 512 bits which is the block size of SHA-256" is converted to the hash value (in hex): `fa91498c139805af73f7ba275cca071e78d78675027000c99a9925e2ec92eedd`.
+
+A good implementation of PBKDF2 will perform pre-hashing before the expensive iterated hashing phase, but some implementations perform the conversion on each iteration. This can make hashing long passwords significantly more expensive than hashing short passwords. If a user can supply very long passwords, there is a potential denial of service vulnerability, such as the one published in [Django](https://www.djangoproject.com/weblog/2013/sep/15/security/) in 2013. Manual [pre-hashing](#pre-hashing-passwords) can reduce this risk but requires adding a [salt](#salting) to the pre-hash step.
 
 ## Upgrading Legacy Hashes
```

Updated summary section (verbatim, f14bc4c):

# Password Storage Cheat Sheet

## Introduction

It is essential to store passwords in a way that prevents them from being obtained by an attacker even if the application or database is compromised. The majority of modern languages and frameworks provide built-in functionality to help store passwords safely.

After an attacker has acquired stored password hashes, they are always able to brute force hashes offline. As a defender, it is only possible to slow down offline attacks by selecting hash algorithms that are as resource intensive as possible.

This cheat sheet provides guidance on the various areas that need to be considered related to storing passwords. In short:

- **Use [Argon2id](#argon2id) with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism.**
- **If [Argon2id](#argon2id) is not available, use [scrypt](#scrypt) with a minimum CPU/memory cost parameter of (2^17), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1.**
- **For legacy systems using [bcrypt](#bcrypt), use a work factor of 10 or more and with a password limit of 72 bytes.**
- **If FIPS-140 compliance is required, use [PBKDF2](#pbkdf2) with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256.**
- **Consider using a [pepper](#peppering) to provide additional defense in depth (though alone, it provides no additional secure characteristics).**

## Background

### Hashing vs Encryption

Hashing and encryption both provide ways to keep sensitive data safe. However, in almost all circumstances, **passwords should be hashed, NOT encrypted.**

**Hashing is a one-way function** (i.e., it is impossible to "decrypt" a hash and obtain the original plaintext value). Hashing is appropriate for password validation. Even if an attacker obtains the hashed password, they cannot enter it into an application's password field and log in as the victim.

