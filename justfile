set shell := ["/usr/bin/env", "bash", "-c"]
set quiet

JUST := "just -u -f " + justfile()
_default:
    @echo "Files commands:"
    @echo "  lint   - Lint all .nix & .sh files"
    @echo "  format - Format all .nix & .sh files"
    @echo ""
    @echo "System commands:"
    @echo "  all    - All of above"
    @echo "  clean  - Clean up caches"
    @echo "  nixos  - Switch NixOS generation"
    @echo "  update - Update all flake inputs"
    @echo ""
    @echo "Secrets commands:"
    @echo "  add     - Add a secret"
    @echo "  rem     - Remove a secret"
    @echo "  key     - Show SOPS public key"
    @echo "  view    - View decrypted secrets"
    @echo "  encrypt - Encrypt file back to secrets"
    @echo "  decrypt - Decrypt secrets to file for manual editing"
    @echo "  setup-sops - Setup the SOPS age key"
    @echo "  setup-keys - Setup SSH and GPG keys from SOPS"
    @echo ""
    @echo "Usage:"
    @echo "  just <command>"

lint:
    @echo -e "\n➤ Linting Nix files…"
    @nix run nixpkgs#time -- -f "⏱ Completed in %E" nix run nixpkgs#statix -- check --ignore '.git/**'
    @echo "✔ Nix linting passed!"
    @echo -e "\n➤ Checking Bash scripts…"
    @nix run nixpkgs#time -- -f "⏱ Completed in %E" find . -name "*.sh" -not -path "./.git/*" -exec nix run nixpkgs#shellcheck -- {} +
    @echo "✔ ShellCheck passed!"


nixos:
    @echo -e "\n➤ Rebuilding NixOS…"
    nh os switch .


format:
    @echo -e "\n➤ Formatting Nix files"
    treefmt
    @echo "✔ Formatting passed!"


update:
    @echo -e "\n➤ Updateing flake inputs..."
    nix flake update
    @echo -e "✔ Updated succesfully"

clean:
    @echo -e "\n➤ Cleaning up build artifacts and caches…"
    @echo "[DEL] Cleaning Nix store (1 day older)..."
    nh clean all --keep 1
    @echo "[OPT] Optimizing Nix store..."
    nix store optimise
    @echo -e "✔ Cleanup completed!"


all:
    @echo -e "\n➤ Running full pipeline…"
    {{JUST}} lint
    {{JUST}} format
    {{JUST}} nixos
    @echo -e "✔ All done!"


view:
    @echo -e "\n➤ Viewing decrypted secrets…"
    sops --decrypt secrets/secrets.yaml


decrypt:
    @echo -e "\n➤ Decrypting secrets to secrets/secrets-decrypted.yaml…"
    sops --decrypt secrets/secrets.yaml > secrets/secrets-decrypted.yaml
    @echo "Edit secrets/secrets-decrypted.yaml then run: just encrypt"


encrypt:
    @echo -e "\n➤ Encrypting secrets/secrets-decrypted.yaml to secrets/secrets.yaml…"
    sops --encrypt secrets/secrets-decrypted.yaml > secrets/secrets.yaml
    @rm secrets/secrets-decrypted.yaml
    @echo "✔ Encrypted and cleaned up!"


setup-sops:
    @echo -e "\n➤ Setting up SOPS age key…"
    sops-setup


setup-keys:
    @echo -e "\n➤ Setting up SSH and GPG keys from SOPS…"
    setup-keys


rem key:
    @echo -e "\n➤ Removing secret: {{key}}"
    sops unset secrets/secrets.yaml '["{{key}}"]'
    @echo "✔ Secret removed!"


add key value:
    @echo -e "\n➤ Adding secret: {{key}} = {{value}}"
    sops --set '["{{key}}"] "{{value}}"' secrets/secrets.yaml
    @echo "✔ Secret added!"

key:
    @echo -e "\n➤ SOPS public key:"
    @sops --version && echo ""
    @if [ -f ~/.config/sops/age/keys.txt ]; then \
        echo "Public key:"; \
        nix shell nixpkgs#age -c age-keygen -y ~/.config/sops/age/keys.txt; \
    else \
        echo "No age key found. Run 'just setup' to create one."; \
    fi
