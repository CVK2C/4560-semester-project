import React from "react";
import {
  Button,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  View,
} from "react-native";
import { useRouter } from "expo-router"; // For navigation

export default function HomeScreen() {
  const router = useRouter(); // Router hook for navigation

  const handleDelete = () => {
    router.push("/index");
  };

  const handleEmptyButton1 = () => {};

  const handleEmptyButton2 = () => {};

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.buttonContainer}>
          {/* Delete Button */}
          <Button title="Log Out" onPress={handleDelete} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    padding: 16,
    flexGrow: 1,
    justifyContent: "center",
  },
  buttonContainer: {
    flexDirection: "column",
    gap: 12,
    alignItems: "center",
  },
});
