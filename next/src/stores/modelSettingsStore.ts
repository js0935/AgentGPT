import type { StateCreator } from "zustand";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { createSelectors } from "./helpers";
import type { ModelSettings } from "../types";
import { getDefaultModelSettings } from "../utils/constants";

const resetters: (() => void)[] = [];

interface ModelSettingsSlice {
  modelSettings: ModelSettings;
  updateSettings: <Key extends keyof ModelSettings>(key: Key, value: ModelSettings[Key]) => void;
}

const initialModelSettingsState = {
  modelSettings: getDefaultModelSettings(),
};

const createModelSettingsSlice: StateCreator<ModelSettingsSlice> = (set) => {
  resetters.push(() => set(initialModelSettingsState));

  return {
    ...initialModelSettingsState,
    updateSettings: <Key extends keyof ModelSettings>(key: Key, value: ModelSettings[Key]) => {
      set((state) => ({
        modelSettings: { ...state.modelSettings, [key]: value },
      }));
    },
  };
};

export const useModelSettingsStore = createSelectors(
  create<ModelSettingsSlice>()(
    persist(
      (...a) => ({
        ...createModelSettingsSlice(...a),
      }),
      {
        name: "agentgpt-settings-storage-v2",
        version: 2,
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          modelSettings: {
            ...state.modelSettings,
            customModelName: "meta/llama-3.1-8b-instruct",
            maxTokens: Math.min(state.modelSettings.maxTokens, 4000),
          },
        }),
        migrate: (persistedState, version) => {
          // 若版本不符（舊的 localStorage 有 gpt-3.5-turbo 等舊模型名稱），
          // 直接回傳預設值，拋棄舊的存儲
          if (version < 2) {
            return initialModelSettingsState as ModelSettingsSlice;
          }
          return persistedState as ModelSettingsSlice;
        },
      }
    )
  )
);

export const resetSettings = () => resetters.forEach((resetter) => resetter());
