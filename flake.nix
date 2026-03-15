{
  description = "optimisation-final";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    { self, nixpkgs, ... }@inputs:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      treefmtEval = forAllSystems (
        system: inputs.treefmt-nix.lib.evalModule nixpkgs.legacyPackages.${system} ./treefmt.nix
      );
    in
    {
      formatter = forAllSystems (system: treefmtEval.${system}.config.build.wrapper);
      checks = forAllSystems (system: {
        formatting = treefmtEval.${system}.config.build.check self;
      });
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default =
            let
              inherit (pkgs)
                codespell
                mkShell
                prek
                stdenv
                uv
                tinymist
                typst
                typstyle
                zlib
                ;
            in
            mkShell {
              buildInputs = [
                codespell
                prek
                self.formatter.${system}
                tinymist
                typst
                typstyle
                uv
              ];

              LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
                stdenv.cc.cc.lib
                zlib
              ];
            };
        }
      );
    };
}
