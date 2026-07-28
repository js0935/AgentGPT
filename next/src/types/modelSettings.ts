import { type Language } from "../utils/languages";

export const GPT_35_TURBO = "gpt-3.5-turbo" as const;
export const GPT_35_TURBO_16K = "gpt-3.5-turbo-16k" as const;
export const GPT_4 = "gpt-4" as const;
export const GPT_4_TURBO = "gpt-4-turbo" as const;
export const GPT_4O = "gpt-4o" as const;
export const GPT_4O_MINI = "gpt-4o-mini" as const;

export const GPT_MODEL_NAMES = [
  GPT_35_TURBO,
  GPT_35_TURBO_16K,
  GPT_4,
  GPT_4_TURBO,
  GPT_4O,
  GPT_4O_MINI,
] as const;
export type GPTModelNames =
  | "gpt-3.5-turbo"
  | "gpt-3.5-turbo-16k"
  | "gpt-4"
  | "gpt-4-turbo"
  | "gpt-4o"
  | "gpt-4o-mini";

export const MAX_TOKENS: Record<GPTModelNames, number> = {
  "gpt-3.5-turbo": 16385,
  "gpt-3.5-turbo-16k": 16385,
  "gpt-4": 8192,
  "gpt-4-turbo": 128000,
  "gpt-4o": 128000,
  "gpt-4o-mini": 128000,
};

export interface ModelSettings {
  language: Language;
  customApiKey: string;
  customModelName: GPTModelNames;
  customTemperature: number;
  customMaxLoops: number;
  maxTokens: number;
}
