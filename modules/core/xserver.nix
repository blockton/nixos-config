{ lib, user, ... }:
{
  services = {
    xserver = {
      enable = true;
      xkb = {
        layout = "us";
        variant = "";
      };
    };

    displayManager.autoLogin = {
      enable = true;
      user = "${user}";
    };
    libinput.enable = true;
    # libinput = {
    #   enable = true;
    #   touchpad = {
    #     tapping = true;
    #     naturalScrolling = true;
    #     tappingButtonMap = "lrm";
    #   };
    # };
  };
  # To prevent getting stuck at shutdown
  systemd.settings.Manager.DefaultTimeoutStopSec = "10s";
}
