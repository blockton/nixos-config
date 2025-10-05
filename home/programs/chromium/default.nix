{ pkgs, lib, ... }:

{
  programs.chromium = {
    enable = true;
    package = pkgs.chromium;
    extensions = [
      "gighmmpiobklfepjocnamgkkbiglidom" # ad blocker
      "eimadpbcbfnmbkopoojfekhnkhdbieeh" # dark reader
      "bggfcpfjbdkhfhfmkjpbhnkhnpjjeomc" # github icons
      "aapbdbdomjkkjkaonfhkkikfgjllcleb" # google translate
    ];
  };
}
