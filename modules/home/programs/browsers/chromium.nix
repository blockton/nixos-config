{ pkgs, ... }:
{
  # Chromium browser configuration
  programs.chromium = {
    enable = true;
    package = pkgs.chromium;

    # Essential browser extensions
    extensions = [
      "eimadpbcbfnmbkopoojfekhnkhdbieeh" # Dark Reader
      "bggfcpfjbdkhfhfmkjpbhnkhnpjjeomc" # GitHub Icons
      "hlepfoohegkhhmjieoechaddaejaokhf" # Refined GitHub
      "aapbdbdomjkkjkaonfhkkikfgjllcleb" # Google Translate
      "gighmmpiobklfepjocnamgkkbiglidom" # AdGuard AdBlocker
    ];
  };
}
