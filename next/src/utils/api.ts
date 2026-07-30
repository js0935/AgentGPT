/**
 * tRPC client for App Router
 */
import { createTRPCReact, httpBatchLink } from "@trpc/react-query";
import superjson from "superjson";
import { QueryClient } from "@tanstack/react-query";

import { type AppRouter } from "../server/api/root";

export const api = createTRPCReact<AppRouter>();

const getBaseUrl = () => {
  if (typeof window !== "undefined") return ""; // browser should use relative url
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return `http://localhost:3001`;  // frontend 跑在 port 3001
};

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 1000,
      retry: 1,
    },
  },
});

export const trpcClient = api.createClient({
  transformer: superjson,
  links: [
    httpBatchLink({
      url: `${getBaseUrl()}/api/trpc`,
    }),
  ],
});
