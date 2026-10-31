#=====================================================================#
# MIMO CODE - CODING AGENT
#=====================================================================#
{
  inputs,
  pkgs,
  ...
}: {
  home.packages = [
    inputs.llm-agents.packages.${pkgs.stdenv.hostPlatform.system}.mimo-code
  ];
}
