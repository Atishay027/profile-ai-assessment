import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../api/client";
import type { Feedback, FeedbackInput, Invitation } from "../types";
import { DEMO_USER_ID } from "./useProfile";

export function useUpcomingInvitations() {
  return useQuery({
    queryKey: ["invitations", "upcoming", DEMO_USER_ID],
    queryFn: () => api.get<Invitation[]>(`/users/${DEMO_USER_ID}/invitations`),
  });
}

export function useGatheringHistory() {
  return useQuery({
    queryKey: ["invitations", "history", DEMO_USER_ID],
    queryFn: () => api.get<Invitation[]>(`/users/${DEMO_USER_ID}/gathering-history`),
  });
}

function useInvalidateInvitations() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["invitations"] });
}

export function useRespondToInvitation() {
  const invalidate = useInvalidateInvitations();
  return useMutation({
    mutationFn: ({
      invitationId,
      action,
    }: {
      invitationId: string;
      action: "accept" | "decline";
    }) => api.post<Invitation>(`/invitations/${invitationId}/respond`, { action }),
    onSuccess: invalidate,
  });
}

export function useSubmitFeedback() {
  const invalidate = useInvalidateInvitations();
  return useMutation({
    mutationFn: ({
      invitationId,
      input,
    }: {
      invitationId: string;
      input: FeedbackInput;
    }) => api.post<Feedback>(`/invitations/${invitationId}/feedback`, input),
    onSuccess: invalidate,
  });
}
