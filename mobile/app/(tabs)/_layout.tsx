import { Tabs } from "expo-router";

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: true }}>
      <Tabs.Screen name="index" options={{ title: "Profile" }} />
      <Tabs.Screen name="invitations" options={{ title: "Invitations" }} />
    </Tabs>
  );
}
