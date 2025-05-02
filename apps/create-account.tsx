import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

const CreateAccountPage = () => {
  const router = useRouter();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const isValidPassword = (pwd) => {
    // Alphanumeric and must contain at least one special character
    const pattern = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$/;
    return pattern.test(pwd);
  };

  const handleCreateAccount = async () => {
    if (!firstName || !lastName || !username || !password) {
      setErrorMessage("All fields are required.");
      return;
    }

    if (!isValidPassword(password)) {
      setErrorMessage(
        "Password must include letters, numbers, and a special character."
      );
      return;
    }

    // Prepare the data to send to the backend
    const userData = {
      fname: firstName.trim(),
      lname: lastName.trim(),
      username: username.trim(),
      password: password.trim(),
      admsts: "yes", // Defaulting to "no" for standard users
    };

    try {
      const response = await fetch(
        "http://10.118.131.151:5001/create-account",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert("Account created!");
        router.back(); // Navigate back to the login screen
      } else {
        setErrorMessage(data.error || "Something went wrong.");
      }
    } catch (error) {
      console.error("Create account error:", error);
      setErrorMessage("Unable to connect to the server.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>

      {/* Username and Password requirements */}
      <Text style={styles.note}>
        • Username must be unique.{"\n"}• Password must include letters,
        numbers, and a special character.
      </Text>

      <TextInput
        style={styles.input}
        placeholder="First Name"
        value={firstName}
        onChangeText={setFirstName}
      />
      <TextInput
        style={styles.input}
        placeholder="Last Name"
        value={lastName}
        onChangeText={setLastName}
      />
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}

      <Button title="Create Account" onPress={handleCreateAccount} />
      <View style={{ marginTop: 10 }}>
        <Button title="Go Back" onPress={() => router.back()} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    marginBottom: 15,
    textAlign: "center",
  },
  note: {
    fontSize: 14,
    color: "gray",
    marginBottom: 15,
    textAlign: "center",
  },
  input: {
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    paddingHorizontal: 10,
    marginBottom: 10,
  },
  error: {
    color: "red",
    marginBottom: 10,
    textAlign: "center",
  },
});

export default CreateAccountPage;
