#=====================================================================#
# AGENT SKILLS - SHARED REPO-LOCAL SKILLS
#=====================================================================#
#- Links every skill into ~/.agents/skills for Codex, ChatGPT, MiMo, OMP,
#- OpenCode and Zed. ZCode reads ~/.zcode/skills; Claude Code uses claude.nix.
{
  lib,
  user,
  ...
}: let
  skills = lib.filterAttrs (_: type: type == "directory") (builtins.readDir ./skills);
  linkSkills = directory:
    lib.mapAttrs' (name: _:
      lib.nameValuePair "${directory}/${name}" {source = ./skills + "/${name}";})
    skills;
in {
  home.file =
    linkSkills ".agents/skills"
    // lib.optionalAttrs user.zcode.enable (linkSkills ".zcode/skills");
}
