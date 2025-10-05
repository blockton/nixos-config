{ pkgs-stable, ... }:

with pkgs-stable;
[
  openssh
  openssl
  openssl.dev
]
