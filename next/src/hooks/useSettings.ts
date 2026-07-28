import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";

import { useModelSettingsStore } from "../stores";
import type { ModelSettings } from "../types";
import { getDefaultModelSettings } from "../utils/constants";
import type { Language } from "../utils/languages";
import { findLanguage } from "../utils/languages";
import i18n from "../utils/i18n";


export type SettingsModel = {
  settings: ModelSettings;
  updateSettings: <Key extends keyof ModelSettings>(key: Key, value: ModelSettings[Key]) => void;
  updateLangauge: (language: Language) => Promise<void>;
};

export function useSettings(): SettingsModel {
  const [_modelSettings, set_ModelSettings] = useState<ModelSettings>(getDefaultModelSettings());
  const modelSettings = useModelSettingsStore.use.modelSettings();
  const updateSettings = useModelSettingsStore.use.updateSettings();

  // The server doesn't have access to local storage so rendering Zustand directly will lead to a hydration error
  useEffect(() => {
    set_ModelSettings(modelSettings);
  }, [modelSettings]);

  const updateLangauge = async (language: Language): Promise<void> => {
    await i18n.changeLanguage(language.code);
    updateSettings("language", language);
  };

  return {
    settings: _modelSettings,
    updateSettings: updateSettings,
    updateLangauge: updateLangauge,
  };
}
