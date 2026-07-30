import { ENGLISH } from "./languages";
import type { ModelSettings } from "../types";

export const LLAMA_8B = "meta/llama-3.1-8b-instruct" as const;
export const LLAMA_70B = "meta/llama-3.1-70b-instruct" as const;
export const MISTRAL_NEMOTRON = "mistralai/mistral-nemotron" as const;
export const NEMOTRON_MINI = "nvidia/nemotron-mini-4b-instruct" as const;
export const GPT_MODEL_NAMES = [LLAMA_8B, LLAMA_70B, MISTRAL_NEMOTRON, NEMOTRON_MINI];

export const DEFAULT_MAX_LOOPS_FREE = 25 as const;
export const DEFAULT_MAX_LOOPS_CUSTOM_API_KEY = 10 as const;

export const getDefaultModelSettings = (): ModelSettings => {
  return {
    customApiKey: "",
    language: ENGLISH,
    customModelName: LLAMA_8B,
    customTemperature: 0.8,
    customMaxLoops: DEFAULT_MAX_LOOPS_FREE,
    maxTokens: 1250,
  };
};
