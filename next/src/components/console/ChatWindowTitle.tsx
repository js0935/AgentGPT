import React from "react";

import type { GPTModelNames } from "../../types";
import { LLAMA_70B, MISTRAL_NEMOTRON } from "../../types";

export const ChatWindowTitle = ({ model }: { model: GPTModelNames }) => {
  if (model === LLAMA_70B) {
    return (
      <>
        Agent<span className="text-amber-500">70B</span>
      </>
    );
  }

  if (model === MISTRAL_NEMOTRON) {
    return (
      <>
        Agent<span className="text-neutral-400">Nemotron</span>
      </>
    );
  }

  return (
    <>
      Agent<span className="text-neutral-400">Llama</span>
    </>
  );
};
