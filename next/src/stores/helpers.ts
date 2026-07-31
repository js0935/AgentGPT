import type { StoreApi, UseBoundStore } from "zustand";

/*
  Automatically creates selectors for each states in store.
  Zustand recommends using selectors for calling state/actions for optimal performance
  Reference: https://docs.pmnd.rs/zustand/guides/auto-generating-selectors
*/
type WithSelectors<S> = S extends { getState: () => infer T }
  ? S & { use: { [K in keyof T]: () => T[K] } }
  : never;

export const createSelectors = <S extends UseBoundStore<StoreApi<object>>>(
  store: S
) => {
  const withSelectors = store as WithSelectors<typeof store>;
  withSelectors.use = {} as WithSelectors<typeof store>["use"];
  for (const k of Object.keys(store.getState())) {
    (withSelectors.use as Record<string, unknown>)[k] = () =>
      store((s) => s[k as keyof typeof s]);
  }

  return withSelectors;
};
