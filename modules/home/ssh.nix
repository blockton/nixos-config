{
  programs.ssh = {
    enable = true;

    enableDefaultConfig = false;

    matchBlocks = {
      "*" = {
        controlPath = "~/.ssh/control-%r@%h:%p";
        controlMaster = "auto";
        addKeysToAgent = "1h";
        controlPersist = "10m";
        compression = false;
        forwardAgent = false;
        hashKnownHosts = false;
        serverAliveInterval = 0;
        serverAliveCountMax = 3;
        userKnownHostsFile = "~/.ssh/known_hosts";
      };

      github = {
        port = 443;
        user = "git";
        host = "github.com";
        hostname = "ssh.github.com";
        identityFile = "~/.ssh/id_github";
        identitiesOnly = true;
      };
    };
  };
  services.ssh-agent.enable = true;
}
