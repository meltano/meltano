---
title: "Encrypting Secrets"
description: Details the Alpha process for encrypting Meltano Cloud secrets
layout: doc
weight: 8
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

This document covers information on encrypting secrets in your Meltano `secrets.yml` file.

## Components for Encryption

### Encryption Method

Use the `meltano cloud config env set <SECRET_NAME>` cli command to set an environment variable secret.

This will set secrets via the `.env` file at runtime for a job or schedule.

You can list and delete secrets configured as well.

```
meltano cloud config env list
meltano cloud config env delete <SECRET_NAME>
```

Secrets are not able to be decrypted after they are set. If you need to change a secret, you can set the secret again.

#### Public Key

During the on-boarding process, Meltano will provide you with the Public Key of your public/private encryption key pair.
For details on the encryption algorithms and other security related information, refer to the [Security page](/security).

Save your public key somewhere for use during encryption.

#### Utility kms-ext

We have a utility extension for encrypting your secrets:
https://github.com/meltano/kms-ext

Recommended installation process:
```
pip install pipx
pipx install git+https://github.com/meltano/kms-ext.git@main
```

Once installed, you should be able to run `kms --help` to see usage, options, and commands available.

> **Note**
> Since the private key of your encryption key never leaves our AWS servers, you are not able to decrypt your secrets once you have encrypted them.
> If you need to change or confirm your values, you will need to re-encrypt your .env file.
> Each time encryption is performed, all contents in the .env file will update.

#### Example

For this example, the following statements are true:

- I am in my meltano project root directory
- Public key file is named `meltano.pub`
- Environment variable secrets are set in a file called `.env`
- I want my `secrets.yml` encrypted file in the root of my project directory

The following command will encrypt your `.env` file with the `meltano.pub` key and save the encrypted secrets to a file called `secrets.yml`.

```
kms encrypt meltano.pub --dotenv-path .env --output-path secrets.yml
```

By default, our cloud runners will look for `secrets.yml` in the root of your project.
If you would like to change the location or name of the secrets file, please inform us during your on-boarding process.

Example `.env` file:
```
THESE_ARE_MY_SECRET_VARS=secret_contents
DATABASE_CREDENTIALS=secret_database_credentials_here
```

The default output file, `secrets.yml`, will look similar to this:

```
env:
- name: THESE_ARE_MY_SECRET_VARS
  value:
    ciphertext: J+msMhK53SFZhAU6EGYyGwwFytyi4QzEG7cYSGMluBK1Kgs31YpldzwrNvygcyRzUtZ2XD2UKGVjzCl72aF63W/EizRCpZmwBviMLPn+ifp2MPWTVuJb0uD5qdy6ByUYjwyZdah9CwZcCCn2T0fZv9F6CX+srB4a0pluRovK14InoNm9Tr1ssqnrPPIWYH0sTNHjR0dGzdjrvOjSUqwXuPnROGmKRlHUQjW2LOYzn/3FbFC+M9uHiAGK6/lQRVTMOufvIJ/DwEnFJ22BcDhZYMBNkiB/pSnuhtdyAZf0IEgB/bzljqeZeRdoSnkm3vylyY148u78hLl9TWonDzxsbYO6oPYn8sxrzjbf9cwrwhRdMPjqyZLbMrXvwMReFa0/5r5soULrSy3aEECRD9vxZ2Xij4jHICDmfmPHPoZVovLw7se9Pnxyir9HASnSKa657fZQTcNFIWgIisIkJV6fE/+3EWyYeAwmTZ+Mjp2p13BwWRSmwMS2pY/lNm4TGAR73FvFdpjkHMLYqluTK53EHqZhUxlkfTNlMX8vYlmoUzQFCFeeGKKGtYLlQUAt+oYpFO3aUG1diM0QdR2Fss9W1VfZiHDA0bz0yCcV/GRZki8T3ehDMxaVqYreJyitM9r9TQIz8HWny1JSupNGGCFwPto4e7veOTSVo0AozBiG5Do=
    scheme: RSAES_OAEP_SHA_256
- name: DATABASE_CREDENTIALS
  value:
    ciphertext: 3A6IWdP4fZoiI+xjENaxGI3MSue6svKk5l3ecXCJt4+sbD5X9M2IcvN6sBooi9jjKyQf55ojhzSlC2Wzaaw/d4Y1Ulh2kH4lae1UHrpT+K5yvah3PqZ51xU+TZqV4+7pd2YGpoEpdNsw3C/ZfLg+tt2JjpK0nOXnbgVTLrcqqVQj7PpjNSXFXr2IJmULgybRgCBKmBoTJWcLasLVvhuTOqdU5ZCm0fp/RXRltlK3/pFE1YMOXrVOGbozNluoHS5b5JrdOGZuHZ+He56PmH3bh4d1pWmi970gI+BQ3GBkyLOxdYigK0d/z8mZCdsc0G93GRS35J3HSg2cHoACsXPvCxAFSwt73skBsNMKuRdplrBc0YSpld5lG9ccTISGKf1t0YtXlDYI5bT/jZH56DcU0Lyz54zBo+PjNEQN4nGOil3d/pjBSXi0UuDH3GWEIw7Tvb08N3GfYPMQd5rPVagVyQjrHwGBugMDQy1SEtlsTBXl76porBnurAcb0LCiGQv+Q1dJCMG+JM1PE+qLrj6cOANhDWj8lCsHD7Nyz5Q4wJehnznvHKobDwZ50bEde53grXCp5s4gLOmaG9JCa8pDUjlM7ppqEkZcERFjKfp2VVicJI9Skcd1NRB9yemJrtdUKlsD5OOawZER0piJCBfQewJmBBDvtU7K5lPSUWqshH8=
    scheme: RSAES_OAEP_SHA_256
```

### Reserved Variables

See the [reserved variables](/platform/#reserved-variables) docs for more details on variables that are reserved for use by Meltano Cloud.
