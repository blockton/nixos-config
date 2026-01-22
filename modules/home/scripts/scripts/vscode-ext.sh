#!/usr/bin/env bash
set -euo pipefail

INPUT="$1"
PUBLISHER="${INPUT%.*}"
NAME="${INPUT#*.}"

echo "Fetching info for ${PUBLISHER}.${NAME}..."

API_URL="https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
PAYLOAD='{"filters":[{"criteria":[{"filterType":7,"value":"'${PUBLISHER}'.'${NAME}'"}]}],"assetTypes":[],"flags":914}'

VERSION=$(curl -s "$API_URL" -H "Content-Type: application/json; charset=utf-8" -H "Accept: application/json;api-version=3.0-preview.1" -d "$PAYLOAD" | jq -r '.results[0].extensions[0].versions[0].version' 2>/dev/null || echo "")

if [[ -z "$VERSION" ]]; then
  echo "Error: Extension not found"
  exit 1
fi

DOWNLOAD_URL="https://${PUBLISHER}.gallery.vsassets.io/_apis/public/gallery/publisher/${PUBLISHER}/extension/${NAME}/${VERSION}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
HASH_RAW=$(nix-prefetch-url --type sha256 "$DOWNLOAD_URL" 2>/dev/null || "")
HASH=$(nix hash to-sri --type sha256 "$HASH_RAW" 2>/dev/null | grep -v warning || echo "sha256-$HASH_RAW")

cat <<EOF

  ${PUBLISHER}.${NAME} = pkgs.vscode-utils.buildVscodeMarketplaceExtension {
    mktplcRef = {
      name = "${NAME}";
      hash = "${HASH}";
      version = "${VERSION}";
      publisher = "${PUBLISHER}";
    };
  };
EOF

echo ""
echo "Add to extensions list: ${PUBLISHER}.${NAME}"
