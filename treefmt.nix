{
  programs = {
    nixfmt.enable = true;
    ruff-format.enable = true;
    prettier = {
      enable = true;
      includes = [
        "*.md"
        "*.yaml"
      ];
      settings.proseWrap = "always";
    };
    taplo.enable = true;
    typstyle = {
      enable = true;
      wrapText = true;
    };
  };
}
