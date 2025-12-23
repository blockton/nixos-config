{
  security = {
    sudo.enable = true;
    rtkit.enable = true;

    pam.services = {
      swaylock = { };
      hyprlock = { };
    };
  };
}
