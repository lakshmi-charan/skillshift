# OWASP Password Storage Cheat Sheet revision of 2026-03-26 (commit 02bfdad)

Source: https://raw.githubusercontent.com/OWASP/CheatSheetSeries/02bfdad/cheatsheets/Password_Storage_Cheat_Sheet.md
License: OWASP Cheat Sheet Series, CC BY-SA 4.0 (https://github.com/OWASP/CheatSheetSeries). Verbatim excerpt; formatting preserved.

Unified diff against the previous revision (f387056, 2024-12-09):

```diff
--- f387056 (2024-12-09)
+++ 02bfdad (2026-03-26)
@@ -25,5 +25,5 @@
 Since **encryption is a two-way function**, attackers can retrieve the original plaintext from the encrypted data. It can be used to store data such as a user's address since this data is displayed in plaintext on the user's profile. Hashing their address would result in a garbled mess.
 
- The only time encryption should be used in passwords is in edge cases where it is necessary to obtain the original plaintext password. This might be necessary if the application needs to use the password to authenticate with another system that does not support a modern way to programmatically grant access, such as OpenID Connect (OIDC). Wherever possible, an alternative architecture should be used to avoid the need to store passwords in an encrypted form.
+The only time encryption should be used in passwords is in edge cases where it is necessary to obtain the original plaintext password. This might be necessary if the application needs to use the password to authenticate with another system that does not support a modern way to programmatically grant access, such as OpenID Connect (OIDC). Wherever possible, an alternative architecture should be used to avoid the need to store passwords in an encrypted form.
 
 For further guidance on encryption, see the [Cryptographic Storage Cheat Sheet](Cryptographic_Storage_Cheat_Sheet.md).
@@ -31,5 +31,5 @@
 ### When Password Hashes Can Be Cracked
 
-**Strong passwords stored with modern hashing algorithms and using hashing best practices should be effectively impossible for an attacker to crack.**  It is your responsibility as an application owner to select a modern hashing algorithm.
+**Strong passwords stored with modern hashing algorithms and using hashing best practices should be effectively impossible for an attacker to crack.** It is your responsibility as an application owner to select a modern hashing algorithm.
 
 However, there are some situations where an attacker can "crack" the hashes in some circumstances by doing the following:
@@ -55,16 +55,25 @@
 Salting also protects against an attacker's pre-computing hashes using rainbow tables or database-based lookups. Finally, salting means that it is impossible to determine whether two users have the same password without cracking the hashes, as the different salts will result in different hashes even if the passwords are the same.
 
-[Modern hashing algorithms](#password-hashing-algorithms) such as Argon2id, bcrypt, and PBKDF2 automatically salt the passwords, so no additional steps are required when using them.
+At the algorithm and specification level, modern password hashing functions such as [Argon2id](#argon2id), [bcrypt](#bcrypt), and [PBKDF2](#pbkdf2) require the caller to provide a salt.
+However, most widely used implementations and libraries automatically generate and manage salts internally, so application developers typically do not need to handle salt generation manually when using these libraries correctly.
 
 ### Peppering
 
-A [pepper](https://datatracker.ietf.org/doc/html/draft-ietf-kitten-password-storage-07#section-4.2) can be used in addition to salting to provide an additional layer of protection. It prevents an attacker from being able to crack any of the hashes if they only have access to the database, for example, if they have exploited a SQL injection vulnerability or obtained a backup of the database. Peppering strategies do not affect the password hashing function in any way.
-
-For example, one peppering strategy is hashing the passwords as usual (using a password hashing algorithm) and then using an HMAC (e.g., HMAC-SHA256, HMAC-SHA512, depending on the desired output length) on the original password hash before storing the password hash in the database, with the pepper acting as the HMAC  key.
-
-- The pepper is **shared between stored passwords**, rather than being *unique* like a salt.
-- Unlike a password salt, the pepper **should not be stored in the database**.
+[Peppering](https://datatracker.ietf.org/doc/html/draft-ietf-kitten-password-storage-07#section-4.2) is a class of strategies that can be used in addition to salting to provide an additional layer of protection. It prevents an attacker from being able to crack any of the hashes if they only have access to the database, for example, if they have exploited a SQL injection vulnerability or obtained a backup of the database.
+
+#### Common requirements for peppering strategies
+
+- A pepper is **shared between stored passwords**, rather than being *unique* to an individual password like a password salt.
+- Unlike a password salt, the pepper should not be public and **should not be stored along with the generated hash**. The pepper should be stored separately from the password database.
 - Peppers are secrets and should be stored in "secrets vaults" or HSMs (Hardware Security Modules). See the [Secrets Management Cheat Sheet](Secrets_Management_Cheat_Sheet.md) for more information on securely storing secrets.
-- Like any other cryptographic key, a pepper rotation strategy should be considered.
+- In the event of a pepper's compromise, the pepper will have to be changed. Peppers cannot be changed without knowledge of a user's password. Therefore changing a pepper will require forcing all users whose passwords were protected by the previous pepper to reset their passwords.
+
+#### Pre-hashing peppers
+
+In this strategy, a pepper is added to a password before being hashed by a password hashing algorithm. The computed hash is then stored in the database. In this case the pepper should be a random value generated securely. See the [Cryptographic_Storage_Cheat_Sheet](Cryptographic_Storage_Cheat_Sheet.html#secure-random-number-generation) for more information on securely generating random values.
+
+#### Post-hashing peppers
+
+In this strategy, a password is hashed as usual using a password hashing algorithm. The resulting password hash is then hashed again using an HMAC (e.g., HMAC-SHA256, HMAC-SHA512, depending on the desired output length) before storing the resulting hash in the database. In this case the pepper is acting as the HMAC key and should be generated as per requirements of the HMAC algorithm.
 
 ### Using Work Factors
@@ -72,5 +81,5 @@
  The work factor is the number of iterations of the hashing algorithm that are performed for each password (usually, it's actually `2^work` iterations). The work factor is typically stored in the hash output. It makes calculating the hash more computationally expensive, which in turn reduces the speed and/or increases the cost for which an attacker can attempt to crack the password hash.
 
-When you choose a work factor, strike a balance between security and performance. Though higher work factors make hashes more difficult for an attacker to crack, they will slow down the process of verifying a login attempt. If the work factor is too high, the performance of the application may be degraded, which could used by an attacker to carry out a denial of service attack by exhausting the server's CPU with a large number of login attempts.
+When you choose a work factor, strike a balance between security and performance. Though higher work factors make hashes more difficult for an attacker to crack, they will slow down the process of verifying a login attempt. If the work factor is too high, the performance of the application may be degraded, which could be used by an attacker to carry out a denial of service attack by exhausting the server's CPU with a large number of login attempts.
 
 There is no golden rule for the ideal work factor - it will depend on the performance of the server and the number of users on the application. Determining the optimal work factor will require experimentation on the specific server(s) used by the application. As a general rule, calculating a hash should take less than one second.
@@ -88,5 +97,8 @@
 You do not need to hide which password hashing algorithm is used by an application. If you utilize a modern password hashing algorithm with proper configuration parameters, it should be safe to state in public which password hashing algorithms are in use and be listed [here](https://pulse.michalspacek.cz/passwords/storages).
 
-Three hashing algorithms that should be considered:
+When selecting a password hashing algorithm, developers should prefer modern algorithms that are designed to resist both GPU-based and memory-based attacks.
+Where available, newer algorithms should be chosen for new applications, while older algorithms may still be acceptable for legacy systems with appropriate configuration.
+
+Three hashing algorithms that should be considered.
 
 ### Argon2id
@@ -95,4 +107,7 @@
 
 Rather than a simple work factor like other algorithms, Argon2id has three different parameters that can be configured: the base minimum of the minimum memory size (m), the minimum number of iterations (t), and the degree of parallelism (p). We recommend the following configuration settings:
+
+These parameters control how computationally expensive it is to compute a password hash.
+Increasing memory usage, iteration count, or parallelism makes password cracking attempts significantly slower and more costly for attackers, while still remaining practical for legitimate authentication requests when tuned appropriately.
 
 - m=47104 (46 MiB), t=1, p=1 (Do not use with Argon2i)
@@ -108,5 +123,5 @@
 [scrypt](http://www.tarsnap.com/scrypt/scrypt.pdf) is a password-based key derivation function created by [Colin Percival](https://twitter.com/cperciva). While [Argon2id](#argon2id) should be the best choice for password hashing, [scrypt](#scrypt) should be used when the former is not available.
 
-Like [Argon2id](#argon2id), scrypt has three different parameters that can be configured: the minimum CPU/memory cost parameter (N), the blocksize (r) and the degree of parallelism (p). Use one of the following settings:
+Like [Argon2id](#argon2id), scrypt has three parameters that can be configured: the minimum memory cost parameter (N), the blocksize (r), and the degree of parallelism (p). Use one of the following settings:
 
 - N=2^17 (128 MiB), r=8 (1024 bytes), p=1
@@ -116,5 +131,5 @@
 - N=2^13 (8 MiB), r=8 (1024 bytes), p=10
 
-These configuration settings provide an equal level of defense. The only difference is a trade off between CPU and RAM usage.
+These configuration settings provide a similar minimal level of defense, with the main trade-off between parallelism and RAM usage.
 
 ### bcrypt
@@ -153,7 +168,7 @@
 The work factor for PBKDF2 is implemented through an iteration count, which should set differently based on the internal hashing algorithm used.
 
-- PBKDF2-HMAC-SHA1: 1,300,000 iterations
+- PBKDF2-HMAC-SHA1: 1,400,000 iterations
 - PBKDF2-HMAC-SHA256: 600,000 iterations
-- PBKDF2-HMAC-SHA512: 210,000 iterations
+- PBKDF2-HMAC-SHA512: 220,000 iterations
 
 ### Parallel PBKDF2
```

Updated summary section (verbatim, 02bfdad):

# Password Storage Cheat Sheet

## Introduction

This cheat sheet advises you on the proper methods for storing passwords for authentication. When passwords are stored, they must be protected from an attacker even if the application or database is compromised. Fortunately, a majority of modern languages and frameworks provide built-in functionality to help store passwords safely.

However, once an attacker has acquired stored password hashes, they are always able to brute force hashes offline. Defenders can slow down offline attacks by selecting hash algorithms that are as resource intensive as possible.

To sum up our recommendations:

- **Use [Argon2id](#argon2id) with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism.**
- **If [Argon2id](#argon2id) is not available, use [scrypt](#scrypt) with a minimum CPU/memory cost parameter of (2^17), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1.**
- **For legacy systems using [bcrypt](#bcrypt), use a work factor of 10 or more and with a password limit of 72 bytes.**
- **If FIPS-140 compliance is required, use [PBKDF2](#pbkdf2) with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256.**
- **Consider using a [pepper](#peppering) to provide additional defense in depth (though alone, it provides no additional secure characteristics).**

## Background

### Hashing vs Encryption

Hashing and encryption can keep sensitive data safe, but in almost all circumstances, **passwords should be hashed, NOT encrypted.**

Because **hashing is a one-way function** (i.e., it is impossible to "decrypt" a hash and obtain the original plaintext value), it is the most appropriate approach for password validation. Even if an attacker obtains the hashed password, they cannot use it to log in as the victim.

