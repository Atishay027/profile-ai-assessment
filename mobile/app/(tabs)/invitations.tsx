import type { UseQueryResult } from "@tanstack/react-query";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { ApiError } from "../../src/api/client";
import { colors } from "../../src/components/theme";
import {
  useGatheringHistory,
  useRespondToInvitation,
  useSubmitFeedback,
  useUpcomingInvitations,
} from "../../src/hooks/useInvitations";
import type { Invitation } from "../../src/types";

const HISTORY_LABELS: Record<string, string> = {
  ATTENDED: "Attended",
  NOT_ATTENDED: "Not Attended",
  DECLINED: "Declined",
  EXPIRED: "Expired",
};

function formatEventWindow(invitation: Invitation): string {
  const start = new Date(invitation.event_start);
  const end = new Date(invitation.event_end);
  const dateStr = start.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
  const startTime = start.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  const endTime = end.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  return `${dateStr} · ${startTime} – ${endTime}`;
}

export default function InvitationsScreen() {
  const upcoming = useUpcomingInvitations();
  const history = useGatheringHistory();

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Section
        title="Upcoming"
        query={upcoming}
        emptyText="No upcoming invitations right now."
        renderItem={(invitation) => <UpcomingItem key={invitation.id} invitation={invitation} />}
      />
      <Section
        title="Gathering History"
        query={history}
        emptyText="No past gatherings yet."
        renderItem={(invitation) => <HistoryItem key={invitation.id} invitation={invitation} />}
      />
    </ScrollView>
  );
}

function Section({
  title,
  query,
  emptyText,
  renderItem,
}: {
  title: string;
  query: UseQueryResult<Invitation[], unknown>;
  emptyText: string;
  renderItem: (item: Invitation) => React.ReactNode;
}) {
  return (
    <View style={styles.section}>
      <Text style={styles.heading}>{title}</Text>
      {query.isLoading ? (
        <View style={styles.sectionCenter}>
          <ActivityIndicator color={colors.primary} />
          <Text style={styles.mutedText}>Loading…</Text>
        </View>
      ) : query.isError ? (
        <View style={styles.sectionCenter}>
          <Text style={styles.errorText}>
            {query.error instanceof ApiError ? query.error.message : "Failed to load."}
          </Text>
          <Pressable style={styles.button} onPress={() => query.refetch()}>
            <Text style={styles.buttonText}>Retry</Text>
          </Pressable>
        </View>
      ) : !query.data || query.data.length === 0 ? (
        <Text style={styles.mutedText}>{emptyText}</Text>
      ) : (
        query.data.map(renderItem)
      )}
    </View>
  );
}

function UpcomingItem({ invitation }: { invitation: Invitation }) {
  const respond = useRespondToInvitation();
  const [actionError, setActionError] = useState<string | null>(null);

  function handleRespond(action: "accept" | "decline") {
    if (respond.isPending) return;
    setActionError(null);
    respond.mutate(
      { invitationId: invitation.id, action },
      {
        onError: (err) => {
          setActionError(err instanceof ApiError ? err.message : "Failed to respond.");
        },
      }
    );
  }

  return (
    <View style={styles.card}>
      <Text style={styles.itemTitle}>{invitation.title}</Text>
      <Text style={styles.mutedText}>{formatEventWindow(invitation)}</Text>
      {invitation.location ? <Text style={styles.mutedText}>{invitation.location}</Text> : null}

      {invitation.can_respond && (
        <>
          <View style={styles.row}>
            <Pressable
              style={[
                styles.button,
                styles.secondaryButton,
                respond.isPending && styles.buttonDisabled,
              ]}
              onPress={() => handleRespond("decline")}
              disabled={respond.isPending}
            >
              <Text style={styles.secondaryButtonText}>Decline</Text>
            </Pressable>
            <Pressable
              style={[styles.button, respond.isPending && styles.buttonDisabled]}
              onPress={() => handleRespond("accept")}
              disabled={respond.isPending}
            >
              {respond.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Accept</Text>
              )}
            </Pressable>
          </View>
          {actionError && <Text style={styles.errorText}>{actionError}</Text>}
        </>
      )}

      {invitation.bucket === "ACCEPTED_UPCOMING" && (
        <View style={[styles.badge, styles.badgeAccepted]}>
          <Text style={styles.badgeText}>Accepted — see you there</Text>
        </View>
      )}

      {invitation.bucket === "ATTENDANCE_PENDING" && (
        <View style={[styles.badge, styles.badgeWarning]}>
          <Text style={styles.badgeTextWarning}>Attendance pending confirmation</Text>
        </View>
      )}
    </View>
  );
}

function historyBadgeStyle(bucket: string) {
  switch (bucket) {
    case "ATTENDED":
      return styles.badgeAttended;
    case "NOT_ATTENDED":
      return styles.badgeNotAttended;
    case "DECLINED":
      return styles.badgeDeclined;
    default:
      return styles.badgeExpired;
  }
}

function HistoryItem({ invitation }: { invitation: Invitation }) {
  return (
    <View style={styles.card}>
      <Text style={styles.itemTitle}>{invitation.title}</Text>
      <Text style={styles.mutedText}>{formatEventWindow(invitation)}</Text>
      <View style={[styles.badge, historyBadgeStyle(invitation.bucket)]}>
        <Text style={styles.badgeText}>{HISTORY_LABELS[invitation.bucket] ?? invitation.bucket}</Text>
      </View>

      {invitation.can_submit_feedback && <FeedbackForm invitationId={invitation.id} />}
    </View>
  );
}

function FeedbackForm({ invitationId }: { invitationId: string }) {
  const submitFeedback = useSubmitFeedback();
  const [isOpen, setIsOpen] = useState(false);
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState<number | undefined>(undefined);
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return (
      <View style={styles.successBanner}>
        <Text style={styles.successText}>Thanks for your feedback!</Text>
      </View>
    );
  }

  if (!isOpen) {
    return (
      <Pressable style={[styles.button, styles.secondaryButton]} onPress={() => setIsOpen(true)}>
        <Text style={styles.secondaryButtonText}>Leave Feedback</Text>
      </Pressable>
    );
  }

  function handleSubmit() {
    if (submitFeedback.isPending || !comment.trim()) return;
    submitFeedback.mutate(
      { invitationId, input: { comment: comment.trim(), rating } },
      { onSuccess: () => setSubmitted(true) }
    );
  }

  return (
    <View style={styles.feedbackForm}>
      <Text style={styles.label}>Rating (optional, 1–5)</Text>
      <View style={styles.row}>
        {[1, 2, 3, 4, 5].map((value) => (
          <Pressable
            key={value}
            style={[styles.ratingButton, rating === value && styles.ratingButtonSelected]}
            onPress={() => setRating(rating === value ? undefined : value)}
          >
            <Text style={rating === value ? styles.ratingTextSelected : styles.ratingText}>
              {value}
            </Text>
          </Pressable>
        ))}
      </View>

      <Text style={styles.label}>Comment *</Text>
      <TextInput
        style={[styles.input, styles.multiline]}
        value={comment}
        onChangeText={setComment}
        placeholder="How was it?"
        multiline
      />

      {submitFeedback.isError && (
        <Text style={styles.errorText}>
          {submitFeedback.error instanceof ApiError
            ? submitFeedback.error.message
            : "Failed to submit feedback."}
        </Text>
      )}

      <View style={styles.row}>
        <Pressable
          style={[styles.button, styles.secondaryButton]}
          onPress={() => setIsOpen(false)}
          disabled={submitFeedback.isPending}
        >
          <Text style={styles.secondaryButtonText}>Cancel</Text>
        </Pressable>
        <Pressable
          style={[
            styles.button,
            (submitFeedback.isPending || !comment.trim()) && styles.buttonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={submitFeedback.isPending || !comment.trim()}
        >
          {submitFeedback.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Submit</Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 24,
    backgroundColor: colors.background,
  },
  section: {
    gap: 12,
  },
  sectionCenter: {
    alignItems: "center",
    gap: 8,
    padding: 12,
  },
  heading: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: 16,
    gap: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.text,
  },
  mutedText: {
    color: colors.mutedText,
    fontSize: 13,
  },
  errorText: {
    color: colors.danger,
    fontSize: 13,
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
  button: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonDisabled: {
    backgroundColor: colors.primaryDisabled,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
  },
  secondaryButton: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
    color: colors.text,
    fontWeight: "600",
  },
  badge: {
    alignSelf: "flex-start",
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#fff",
  },
  badgeTextWarning: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.warning,
  },
  badgeAccepted: {
    backgroundColor: colors.primary,
  },
  badgeWarning: {
    backgroundColor: colors.warningBackground,
  },
  badgeAttended: {
    backgroundColor: colors.success,
  },
  badgeNotAttended: {
    backgroundColor: colors.danger,
  },
  badgeDeclined: {
    backgroundColor: colors.mutedText,
  },
  badgeExpired: {
    backgroundColor: colors.mutedText,
  },
  successBanner: {
    backgroundColor: colors.successBackground,
    borderRadius: 8,
    padding: 10,
  },
  successText: {
    color: colors.success,
    fontWeight: "500",
  },
  feedbackForm: {
    gap: 8,
  },
  label: {
    fontSize: 13,
    fontWeight: "500",
    color: colors.mutedText,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: colors.text,
  },
  multiline: {
    minHeight: 70,
    textAlignVertical: "top",
  },
  ratingButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  ratingButtonSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  ratingText: {
    color: colors.text,
  },
  ratingTextSelected: {
    color: "#fff",
    fontWeight: "600",
  },
});
