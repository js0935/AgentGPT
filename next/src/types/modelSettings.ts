import { type Language } from "../utils/languages";

export const LLAMA_8B = "meta/llama-3.1-8b-instruct" as const;
export const LLAMA_70B = "meta/llama-3.1-70b-instruct" as const;
export const MISTRAL_NEMOTRON = "mistralai/mistral-nemotron" as const;
export const NEMOTRON_MINI = "nvidia/nemotron-mini-4b-instruct" as const;

export const GPT_MODEL_NAMES = [
  LLAMA_8B,
  LLAMA_70B,
  MISTRAL_NEMOTRON,
  NEMOTRON_MINI,
] as const;
export type GPTModelNames =
  | "meta/llama-3.1-8b-instruct"
  | "meta/llama-3.1-70b-instruct"
  | "mistralai/mistral-nemotron"
  | "nvidia/nemotron-mini-4b-instruct";

export const MAX_TOKENS: Record<GPTModelNames, number> = {
  "meta/llama-3.1-8b-instruct": 128000,
  "meta/llama-3.1-70b-instruct": 128000,
  "mistralai/mistral-nemotron": 128000,
  "nvidia/nemotron-mini-4b-instruct": 4096,
};

export interface ModelSettings {
  language: Language;
  customApiKey: string;
  customModelName: GPTModelNames;
  customTemperature: number;
  customMaxLoops: number;
  maxTokens: number;
}
