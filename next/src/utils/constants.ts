import { ENGLISH } from "./languages";
import type { ModelSettings } from "../types";

export const GPT_35_TURBO = "gpt-3.5-turbo" as const;
export const GPT_4 = "gpt-4" as const;
export const GPT_4_TURBO = "gpt-4-turbo" as const;
export const GPT_4O = "gpt-4o" as const;
export const GPT_4O_MINI = "gpt-4o-mini" as const;
export const GPT_MODEL_NAMES = [GPT_35_TURBO, GPT_4, GPT_4_TURBO, GPT_4O, GPT_4O_MINI];

export const DEFAULT_MAX_LOOPS_FREE = 25 as const;
export const DEFAULT_MAX_LOOPS_CUSTOM_API_KEY = 10 as const;

export const getDefaultModelSettings = (): ModelSettings => {
  return {
    customApiKey: "",
    language: ENGLISH,
    customModelName: GPT_35_TURBO,
    customTemperature: 0.8,
    customMaxLoops: DEFAULT_MAX_LOOPS_FREE,
    maxTokens: 1250,
  };
};
