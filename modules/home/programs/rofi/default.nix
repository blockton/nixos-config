{ pkgs, ... }:
{
  home.packages = with pkgs; [ rofi ];

  xdg.configFile = {
    "rofi/theme.rasi".source = ./theme.rasi;
    "rofi/config.rasi".source = ./config.rasi;
    "rofi/powermenu-theme.rasi".source = ./powermenu-theme.rasi;
  };
}
