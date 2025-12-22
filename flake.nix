# flake.nix - Nix flake for building and running LinVAM
# Includes Vosk via prebuilt wheel (x86_64-linux only)

{
  description = "LinVAM - Linux Voice Activated Macros";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [ "x86_64-linux" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python3;

        voskWheel = pkgs.fetchurl {
          url = "https://files.pythonhosted.org/packages/py3/v/vosk/vosk-0.3.45-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.whl";
          hash = "sha256-JeAlCTxDmdcnj1Q1aO2MxUYKw6S/SMI2c6zh4l0mYZ8=";
        };

        vosk = python.pkgs.buildPythonPackage rec {
          pname = "vosk";
          version = "0.3.45";
          format = "wheel";

          src = voskWheel;

          propagatedBuildInputs = [ ];
          doCheck = false;

          meta = with pkgs.lib; {
            description = "Vosk offline speech recognition toolkit";
            homepage = "https://alphacephei.com/vosk/";
            license = licenses.asl20;
            platforms = [ "x86_64-linux" ];
          };
        };

        pythonEnv = python.withPackages (ps: with ps; [
          pyqt6
          sounddevice
          srt
          requests
          tqdm
          setuptools
          vosk
        ]);
      in
      rec {
        formatter = pkgs.nixpkgs-fmt;

        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "linvam";
          version = "0.8.4"; # Bump on new releases; matches latest tag v0.8.4

          src = self;

          pyproject = true;
          build-system = [ pkgs.python3Packages.setuptools ];

          propagatedBuildInputs = with pkgs.python3Packages; [
            pyqt6
            sounddevice
            srt
            requests
            tqdm
            setuptools
            vosk
          ];

          nativeBuildInputs = [
            pkgs.makeWrapper
            pkgs.ffmpeg
            pkgs.ydotool
          ];

          installPhase = ''
            runHook preInstall
            ${python.interpreter} setup.py install --prefix=$out --no-compile
            runHook postInstall
          '';

          postFixup = ''
            wrapProgram $out/bin/linvam \
              --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.ffmpeg pkgs.ydotool ]}
          '';

          meta = with pkgs.lib; {
            description = "Linux Voice Activated Macros";
            homepage = "https://github.com/stele95/LinVAM";
            license = licenses.gpl3Only;
            platforms = [ "x86_64-linux" ];
            mainProgram = "linvam";
          };
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.ffmpeg
            pkgs.ydotool
          ];

          shellHook = ''
            echo "LinVAM dev environment ready with Vosk included."
            echo "Run 'linvam' to test."
          '';
        };

        apps.default = {
          type = "app";
          program = "${packages.default}/bin/linvam";
        };
      }
    );
}

