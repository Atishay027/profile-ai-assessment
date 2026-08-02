import { useEffect, useState } from "react";
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
import { useGenerateInsight } from "../../src/hooks/useInsight";
import { useProfile, useUpdateProfile } from "../../src/hooks/useProfile";

const BIO_LIMIT = 400;

export default function ProfileScreen() {
  const { data: profile, isLoading, isError, error, refetch } = useProfile();
  const updateProfile = useUpdateProfile();
  const generateInsight = useGenerateInsight();

  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState("");
  const [city, setCity] = useState("");
  const [occupation, setOccupation] = useState("");
  const [bio, setBio] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (profile && !isEditing) {
      setFullName(profile.full_name);
      setCity(profile.city);
      setOccupation(profile.occupation ?? "");
      setBio(profile.bio ?? "");
    }
  }, [profile, isEditing]);

  function startEditing() {
    if (!profile) return;
    setFullName(profile.full_name);
    setCity(profile.city);
    setOccupation(profile.occupation ?? "");
    setBio(profile.bio ?? "");
    setFormErrors({});
    setSaveSuccess(false);
    setIsEditing(true);
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!fullName.trim()) errors.full_name = "Full name is required.";
    if (!city.trim()) errors.city = "City is required.";
    if (bio.length > BIO_LIMIT) errors.bio = `Bio must be ${BIO_LIMIT} characters or fewer.`;
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSave() {
    if (updateProfile.isPending || !validate()) return;
    updateProfile.mutate(
      {
        full_name: fullName.trim(),
        city: city.trim(),
        occupation: occupation.trim(),
        bio,
      },
      {
        onSuccess: () => {
          setIsEditing(false);
          setSaveSuccess(true);
          setFormErrors({});
        },
        onError: (err) => {
          if (err instanceof ApiError && Object.keys(err.fieldErrors).length > 0) {
            setFormErrors(err.fieldErrors);
          }
        },
      }
    );
  }

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.mutedText}>Loading profile…</Text>
      </View>
    );
  }

  if (isError) {
    const notFound = error instanceof ApiError && error.status === 404;
    if (notFound) {
      return (
        <View style={styles.center}>
          <Text style={styles.mutedText}>No profile found for this account yet.</Text>
        </View>
      );
    }
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>
          {error instanceof ApiError ? error.message : "Failed to load profile."}
        </Text>
        <Pressable style={styles.button} onPress={() => refetch()}>
          <Text style={styles.buttonText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.center}>
        <Text style={styles.mutedText}>No profile found yet.</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {saveSuccess && !isEditing && (
        <View style={styles.successBanner}>
          <Text style={styles.successText}>Profile saved.</Text>
        </View>
      )}

      {isEditing ? (
        <View style={styles.card}>
          <Text style={styles.subheading}>Edit Profile</Text>

          <Field label="Full name *" error={formErrors.full_name}>
            <TextInput
              style={styles.input}
              value={fullName}
              onChangeText={setFullName}
              placeholder="Full name"
            />
          </Field>

          <Field label="City *" error={formErrors.city}>
            <TextInput style={styles.input} value={city} onChangeText={setCity} placeholder="City" />
          </Field>

          <Field label="Occupation" error={formErrors.occupation}>
            <TextInput
              style={styles.input}
              value={occupation}
              onChangeText={setOccupation}
              placeholder="Occupation"
            />
          </Field>

          <Field label={`Bio (${bio.length}/${BIO_LIMIT})`} error={formErrors.bio}>
            <TextInput
              style={[styles.input, styles.multiline]}
              value={bio}
              onChangeText={setBio}
              placeholder="Short bio"
              multiline
            />
          </Field>

          {updateProfile.isError && Object.keys(formErrors).length === 0 && (
            <Text style={styles.errorText}>
              {updateProfile.error instanceof ApiError
                ? updateProfile.error.message
                : "Failed to save profile."}
            </Text>
          )}

          <View style={styles.row}>
            <Pressable
              style={[styles.button, styles.secondaryButton]}
              onPress={() => {
                setIsEditing(false);
                setFormErrors({});
              }}
              disabled={updateProfile.isPending}
            >
              <Text style={styles.secondaryButtonText}>Cancel</Text>
            </Pressable>
            <Pressable
              style={[styles.button, updateProfile.isPending && styles.buttonDisabled]}
              onPress={handleSave}
              disabled={updateProfile.isPending}
            >
              {updateProfile.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Save</Text>
              )}
            </Pressable>
          </View>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.subheading}>Your Profile</Text>
          <InfoRow label="Full name" value={profile.full_name} />
          <InfoRow label="City" value={profile.city} />
          <InfoRow label="Occupation" value={profile.occupation || "—"} />
          <InfoRow label="Bio" value={profile.bio || "—"} />
          <Pressable style={styles.button} onPress={startEditing}>
            <Text style={styles.buttonText}>Edit Profile</Text>
          </Pressable>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.subheading}>AI Profile Insight</Text>
        <Text style={styles.mutedText}>
          Generates a display-only summary from your saved profile. It never changes your profile
          data.
        </Text>

        <Pressable
          style={[styles.button, generateInsight.isPending && styles.buttonDisabled]}
          onPress={() => generateInsight.mutate()}
          disabled={generateInsight.isPending}
        >
          {generateInsight.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Generate Profile Insight</Text>
          )}
        </Pressable>

        {generateInsight.isError && (
          <Text style={styles.errorText}>
            {generateInsight.error instanceof ApiError
              ? generateInsight.error.message
              : "Failed to generate insight."}
          </Text>
        )}

        {generateInsight.data && (
          <View style={styles.insightResult}>
            <InsightCard label="Summary" value={generateInsight.data.summary} />
            <InsightCard label="Communication Style" value={generateInsight.data.communication_style} />
            <InsightCard label="Suggested Focus" value={generateInsight.data.suggested_focus} />
          </View>
        )}
      </View>
    </ScrollView>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      {children}
      {error ? <Text style={styles.fieldError}>{error}</Text> : null}
    </View>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function InsightCard({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.insightCard}>
      <Text style={styles.insightLabel}>{label}</Text>
      <Text style={styles.insightValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 16,
    backgroundColor: colors.background,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    padding: 24,
    backgroundColor: colors.background,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: 16,
    gap: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  subheading: {
    fontSize: 18,
    fontWeight: "600",
    color: colors.text,
  },
  field: {
    gap: 4,
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
    minHeight: 80,
    textAlignVertical: "top",
  },
  fieldError: {
    color: colors.danger,
    fontSize: 12,
  },
  errorText: {
    color: colors.danger,
    fontSize: 14,
    textAlign: "center",
  },
  mutedText: {
    color: colors.mutedText,
    fontSize: 13,
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
  row: {
    flexDirection: "row",
    gap: 12,
    justifyContent: "flex-end",
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
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
  infoRow: {
    gap: 2,
  },
  infoValue: {
    fontSize: 15,
    color: colors.text,
  },
  insightResult: {
    gap: 10,
    marginTop: 8,
  },
  insightCard: {
    backgroundColor: colors.background,
    borderRadius: 8,
    padding: 12,
    gap: 4,
  },
  insightLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.mutedText,
    textTransform: "uppercase",
  },
  insightValue: {
    fontSize: 14,
    color: colors.text,
  },
});
