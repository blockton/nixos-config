{ pkgs, ... }:
{
  home.packages = with pkgs; [
    ngrok # Tunnels local ports to the internet
    yt-dlp # YouTube/media downloader

    # SSH and SSL/TLS
    openssh # OpenSSH client and server
    openssl # OpenSSL cryptography toolkit
    openssl.dev # OpenSSL development headers
  ];
}
