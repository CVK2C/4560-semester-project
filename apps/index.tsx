import React, { useState } from "react";
import { View, Text, Button, TextInput, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

const LoginPage = () => {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogin = async () => {
    // Log the current values of email and password
    console.log("Email (raw):", JSON.stringify(email));
    console.log("Password (raw):", JSON.stringify(password));

    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    try {
      const response = await fetch("http://10.118.131.151:5001/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: email, // Sending email as username
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Successful login, you can redirect the user
        router.push("/(tabs)");
        // Assuming "(tabs)" is the route after login
      } else {
        // Display error message from the API
        setErrorMessage(
          data.error || "Something went wrong. Please try again."
        );
      }
    } catch (error) {
      setErrorMessage("Error connecting to the server.");
    }
  };

  return (
    <View style={styles.container}>
      {/* Logo at the top */}
      <View style={styles.logoContainer}>
        <Text style={styles.logo}>Price Forecast</Text>
      </View>

      {/* Login Form */}
      <View style={styles.contentContainer}>
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          secureTextEntry
          onChangeText={setPassword}
        />

        <Button title="Login" onPress={handleLogin} />

        {/* Create Account Button */}
        <View style={styles.createAccountButton}>
          <Button
            title="Create Account"
            onPress={() => router.push("/create-account")}
          />
        </View>

        {/* Display error message */}
        {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    padding: 20,
  },
  logoContainer: {
    flex: 1,
    justifyContent: "flex-end",
    alignItems: "center",
    marginTop: 50,
  },
  logo: {
    fontSize: 28,
    fontWeight: "bold",
    color: "blue",
  },
  contentContainer: {
    flex: 2,
    justifyContent: "center",
    width: "100%",
  },
  input: {
    width: "100%",
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    marginBottom: 10,
    paddingLeft: 10,
  },
  createAccountButton: {
    marginTop: 10,
  },
  error: {
    color: "red",
    marginTop: 10,
    textAlign: "center",
  },
});

export default LoginPage;
