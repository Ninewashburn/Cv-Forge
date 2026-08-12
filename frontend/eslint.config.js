// @ts-check
const eslint = require("@eslint/js");
const { defineConfig } = require("eslint/config");
const tseslint = require("typescript-eslint");
const angular = require("angular-eslint");

module.exports = defineConfig([
  {
    files: ["**/*.ts"],
    extends: [
      eslint.configs.recommended,
      tseslint.configs.recommended,
      tseslint.configs.stylistic,
      angular.configs.tsRecommended,
    ],
    processor: angular.processInlineTemplates,
    rules: {
      // Garde anti-tells IA au lint (convention CLAUDE.md) : aucun caractere
      // "signature IA" dans les chaines / templates. Ne vise QUE ces codepoints,
      // jamais les accents FR. Le hook pre-commit (check-tells.mjs) reste la
      // garde complete (HTML, JSON, MD, backend) ; ici c'est l'attrape au lint.
      "no-restricted-syntax": [
        "error",
        {
          selector:
            "Literal[value=/[\\u2013\\u2014\\u2018\\u2019\\u201C\\u201D\\u2026\\u2190\\u2192\\u21D2]/]",
          message:
            "Tell IA interdit (tiret cadratin, demi-cadratin, ellipse, quote courbe ou fleche). Voir CLAUDE.md. Les accents FR ne sont jamais vises.",
        },
        {
          selector:
            "TemplateElement[value.raw=/[\\u2013\\u2014\\u2018\\u2019\\u201C\\u201D\\u2026\\u2190\\u2192\\u21D2]/]",
          message:
            "Tell IA interdit dans un template literal. Voir CLAUDE.md. Les accents FR ne sont jamais vises.",
        },
      ],
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "cvforge",
          style: "camelCase",
        },
      ],
      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "cvforge",
          style: "kebab-case",
        },
      ],
    },
  },
  {
    files: ["**/*.html"],
    extends: [
      angular.configs.templateRecommended,
      angular.configs.templateAccessibility,
    ],
    rules: {},
  }
]);
