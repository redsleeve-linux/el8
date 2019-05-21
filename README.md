# Redsleeve / EL8

**RedSleeve Linux** is a 3rd party [ARM](http://en.wikipedia.org/wiki/ARM_architecture) port of a Linux distribution of a Prominent North American Enterprise Linux Vendor (PNAELV). They object to being referred to by name in the context of clones and ports of their distribution, but if you are aware of [CentOS](http://en.wikipedia.org/wiki/CentOS), you can probably guess what [RedSleeve](http://www.redsleeve.org) is based on. 


## Extra build instructions

Some packages needed some manual love and care to build, but not really a patch:

| Package | SRPM | instruction
|---|---|---
| gpgme | gpgme-1.10.0-6.el8.src.rpm | needs to be build with '-D "check exit 0" -D "debug_package %{nil}"'
| libglvnd | libglvnd-1.0.1-0.9.git5baa1e5.el8.src.rpm | needs to be build with '-D "check exit 0" -D "debug_package %{nil}"'
| sqlite | sqlite-3.26.0-3.el8.src.rpm | needs to be build with '-D "check exit 0" -D "debug_package %{nil}"'
| stunnel | stunnel-5.48-5.el8.src.rpm | needs to be build with '-D "check exit 0" -D "debug_package %{nil}"'
