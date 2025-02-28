import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Platform,
  TouchableOpacity,
} from "react-native";

export default function TabLayout() {
  // Function to handle button press
  const handleButtonPress = (buttonName: string) => {
    console.log(`${buttonName} button pressed`);
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>Project 4050</Text>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        <Text style={styles.contentText}></Text>

        {/* Buttons */}
        <TouchableOpacity
          style={styles.button}
          onPress={() => handleButtonPress("Button 1")}
        >
          <Text style={styles.buttonText}>SIGN UP</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.button}
          onPress={() => handleButtonPress("Button 2")}
        >
          <Text style={styles.buttonText}>LOG IN</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>By: Corea, Daniel, Aron</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9f9f9", // Light gray
  },
  header: {
    paddingTop: Platform.OS === "ios" ? 40 : 20, // Space for status bar (iOS vs Android)
    paddingBottom: 20,
    backgroundColor: "#2f4f4f", // Dark blue /green header for a professional look
    alignItems: "center",
    justifyContent: "center",
  },
  headerText: {
    fontSize: 24,
    color: "#ffffff", // White text
    fontWeight: "bold",
  },
  content: {
    flex: 1,
    justifyContent: "center", // Keeps the content centered
    alignItems: "center",
    padding: 20, // Add padding around the content area
  },
  contentText: {
    fontSize: 18,
    color: "#333333", // Dark text
    fontWeight: "600",
    marginBottom: 20, // Space between text and buttons
  },
  button: {
    backgroundColor: "#2f4f4f", // Button color
    paddingVertical: 12,
    paddingHorizontal: 30,
    marginBottom: 10, // Space between buttons
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: {
    fontSize: 16,
    color: "#ffffff", // White text
    fontWeight: "bold",
  },
  footer: {
    position: "absolute", // This will keep the footer at the bottom
    bottom: 30,
    left: 0,
    right: 0,
    alignItems: "center",
  },
  footerText: {
    fontSize: 18,
    color: "#7a7a7a", // Lighter gray text for subtitle
    fontStyle: "italic",
  },
});
