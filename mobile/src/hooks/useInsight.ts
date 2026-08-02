import { useMutation } from "@tanstack/react-query";

import { api } from "../api/client";
import type { InsightResult } from "../types";
import { DEMO_USER_ID } from "./useProfile";

export function useGenerateInsight() {
  return useMutation({
    mutationFn: () => api.post<InsightResult>(`/profiles/${DEMO_USER_ID}/insight`),
  });
}
