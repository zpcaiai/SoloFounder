import { describe, expect, it } from "vitest";
import { translations } from "../i18n/translations";

describe("translations", () => {
  it("has identical key sets for en and zh", () => {
    const en = Object.keys(translations.en).sort();
    const zh = Object.keys(translations.zh).sort();
    expect(zh).toEqual(en);
  });

  it("has no empty values in either language", () => {
    for (const [lang, dict] of Object.entries(translations)) {
      for (const [key, value] of Object.entries(dict)) {
        expect(value, `${lang}.${key} should not be empty`).not.toBe("");
      }
    }
  });
});
