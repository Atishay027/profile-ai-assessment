import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../api/client";
import type { Profile, ProfileUpdateInput } from "../types";

export const DEMO_USER_ID = "user-001";

export function useProfile() {
  return useQuery({
    queryKey: ["profile", DEMO_USER_ID],
    queryFn: () => api.get<Profile>(`/profiles/${DEMO_USER_ID}`),
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ProfileUpdateInput) =>
      api.patch<Profile>(`/profiles/${DEMO_USER_ID}`, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", DEMO_USER_ID] });
    },
  });
}
