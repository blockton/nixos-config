set shell := ["/usr/bin/env", "bash", "-c"]
set quiet

nixos:
    @echo -e "\n➤ Building . . ."
    sudo nixos-rebuild switch --flake .
    @echo -e "\n\n✔ NixOS rebuild completed!"

home:
    @echo -e "\n➤ Switching . . ."
    home-manager switch --flake .
    @echo -e "\n\n✔ Home switch completed!"

update:
    @echo -e "\n➤ Updating . . ."
    nix flake update
    @echo -e "\n\n✔ Flake updated!"
