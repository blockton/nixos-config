set quiet
set shell := ["/usr/bin/env", "bash", "-c"]

JUST := "just -u -f " + justfile()
header := "Available tasks:\n"

_default:
    @{{JUST}} --list-heading "{{header}}" --list


# lint: Validate all nix files using statix
lint:
	@echo -e "\n➤ Linting . . ."
	nix run nixpkgs#statix -- check .
	@echo -e "\n\n✔ Linting passed!"

# Apply Home Manager configuration
home:
	@echo -e "\n➤ Switching . . ."
	home-manager switch --flake .
	@echo -e "\n\n✔ Home switch completed!"

# Rebuild and switch the system NixOS configuration
nixos:
	@echo -e "\n➤ Building . . ."
	sudo nixos-rebuild switch --flake .
	@echo -e "\n\n✔ NixOS rebuild completed!"

# Update the inputs in the flake.lock file to the latest compatible versions
update:
	@echo -e "\n➤ Updating . . ."
	nix flake update
	@echo -e "\n\n✔ Flake updated!"

# Remove old Nix store paths and garbage-collect to free disk space
clean:
	@echo -e "\n➤ Cleaning . . ."
	sudo nix-collect-garbage --delete-older-than "3d"
	@echo -e "\n\n✔ Garbage collected!"

# Format all .nix files with nixfmt and report execution time
format:
	@echo -e "\n➤ Formatting . . ."
	nix run nixpkgs#time -- -f "⏱ Completed in %E" fd -e nix -X nixfmt --strict
	@echo -e "\n\n✔ Formatting passed!"