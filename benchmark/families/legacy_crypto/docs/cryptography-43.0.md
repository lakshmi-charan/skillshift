# cryptography 43.0.0 release notes

Source: https://raw.githubusercontent.com/pyca/cryptography/main/CHANGELOG.rst (verbatim section)

```rst
43.0.0 - 2024-07-20
~~~~~~~~~~~~~~~~~~~

* **BACKWARDS INCOMPATIBLE:** Support for OpenSSL less than 1.1.1e has been
  removed.  Users on older version of OpenSSL will need to upgrade.
* **BACKWARDS INCOMPATIBLE:** Dropped support for LibreSSL < 3.8.
* Updated Windows, macOS, and Linux wheels to be compiled with OpenSSL 3.3.1.
* Updated the minimum supported Rust version (MSRV) to 1.65.0, from 1.63.0.
* :func:`~cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key`
  now enforces a minimum RSA key size of 1024-bit. Note that 1024-bit is still
  considered insecure, users should generally use a key size of 2048-bits.
* :func:`~cryptography.hazmat.primitives.serialization.pkcs7.serialize_certificates`
  now emits ASN.1 that more closely follows the recommendations in :rfc:`2315`.
* Added new :doc:`/hazmat/decrepit/index` module which contains outdated and
  insecure cryptographic primitives.
  ``CAST5``, ``SEED``, ``IDEA``, and ``Blowfish``, which were
  deprecated in 37.0.0, have been added to this module. They will be removed
  from the ``cipher`` module in 45.0.0.
* Moved :class:`~cryptography.hazmat.primitives.ciphers.algorithms.TripleDES`
  and :class:`~cryptography.hazmat.primitives.ciphers.algorithms.ARC4` into
  :doc:`/hazmat/decrepit/index` and deprecated them in the ``cipher`` module.
  They will be removed from the ``cipher`` module in 48.0.0.
* Added support for deterministic
  :class:`~cryptography.hazmat.primitives.asymmetric.ec.ECDSA` (:rfc:`6979`)
* Added support for client certificate verification to the
  :mod:`X.509 path validation <cryptography.x509.verification>` APIs in the
  form of :class:`~cryptography.x509.verification.ClientVerifier`,
  :class:`~cryptography.x509.verification.VerifiedClient`, and
  ``PolicyBuilder``
  :meth:`~cryptography.x509.verification.PolicyBuilder.build_client_verifier`.
* Added Certificate
  :attr:`~cryptography.x509.Certificate.public_key_algorithm_oid`
  and Certificate Signing Request
  :attr:`~cryptography.x509.CertificateSigningRequest.public_key_algorithm_oid`
  to determine the :class:`~cryptography.hazmat._oid.PublicKeyAlgorithmOID`
  Object Identifier of the public key found inside the certificate.
* Added :attr:`~cryptography.x509.InvalidityDate.invalidity_date_utc`, a
  timezone-aware alternative to the naïve ``datetime`` attribute
  :attr:`~cryptography.x509.InvalidityDate.invalidity_date`.
* Added support for parsing empty DN string in
  :meth:`~cryptography.x509.Name.from_rfc4514_string`.
* Added the following properties that return timezone-aware ``datetime`` objects:
  :meth:`~cryptography.x509.ocsp.OCSPResponse.produced_at_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPResponse.revocation_time_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPResponse.this_update_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPResponse.next_update_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPSingleResponse.revocation_time_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPSingleResponse.this_update_utc`,
  :meth:`~cryptography.x509.ocsp.OCSPSingleResponse.next_update_utc`,
  These are timezone-aware variants of existing properties that return naïve
  ``datetime`` objects.
* Added
  :func:`~cryptography.hazmat.primitives.asymmetric.rsa.rsa_recover_private_exponent`
* Added :meth:`~cryptography.hazmat.primitives.ciphers.CipherContext.reset_nonce`
  for altering the ``nonce`` of a cipher context without initializing a new
  instance. See the docs for additional restrictions.
* :class:`~cryptography.x509.NameAttribute` now raises an exception when
  attempting to create a common name whose length is shorter or longer than
  :rfc:`5280` permits.
* Added basic support for PKCS7 encryption (including SMIME) via
  :class:`~cryptography.hazmat.primitives.serialization.pkcs7.PKCS7EnvelopeBuilder`.

.. _v42-0-8:
```
