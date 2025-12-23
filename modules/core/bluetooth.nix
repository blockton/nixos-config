{
  # Bluetooth hardware configuration
  hardware.bluetooth = {
    enable = true;
    powerOnBoot = false; # Don't auto-enable on boot to save power
    settings = {
      General = {
        # Enable various Bluetooth profiles
        Enable = "Source,Sink,Media,Socket";
        Experimental = true; # Enable experimental features
      };
    };
  };
  # Blueman Bluetooth manager GUI
  services.blueman.enable = true;
}
