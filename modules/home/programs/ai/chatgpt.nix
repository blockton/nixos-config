#=====================================================================#
# CHATGPT DESKTOP - CHATGPT AND CODEX
#=====================================================================#
{
  inputs,
  pkgs,
  ...
}: {
  home.packages = [
    inputs.llm-agents.packages.${pkgs.stdenv.hostPlatform.system}.chatgpt
  ];
}
