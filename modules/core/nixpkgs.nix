{
  pkgs,
  pkgsStable,
  inputs,
  ...
}:
{
  nixpkgs = {
    overlays = [
      (
        final: prev:
        (import ../pkgs {
          inherit pkgs;
          inherit inputs;
          inherit pkgsStable;
          inherit (prev) system;
        })
      )
      inputs.nur.overlays.default
    ];
  };
}
