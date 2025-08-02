{
  description = "Simple Python Env";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        system = "${system}";

        # Uncomment for nixpkgs configuration
        # config = {
        # allowBroken = false;
        # };
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          sqlite
          (python312.withPackages (
            python-pkgs: with python-pkgs; [
              django
            ]
          ))
        ];

        LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        shellHook = ''
          # Uncomment if you use zsh
          zsh
        '';
      };
    };
}
