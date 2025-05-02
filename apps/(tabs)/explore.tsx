import React, { useEffect, useState } from "react";
import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import { Picker } from "@react-native-picker/picker";
import { useRouter } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";

const ExploreScreen = () => {
  const [dropdownItems, setDropdownItems] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const router = useRouter();

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await fetch(
          "http://10.118.131.151:5001/dropdown-options"
        );
        const data = await response.json();

        console.log("Dropdown options raw data:", data);

        // Use Object.values to handle dynamic or case-sensitive keys like "Tables_in_PROJECT_4560"
        const tableNames = data.map((item: any) => Object.values(item)[0]);
        console.log("Extracted table names:", tableNames);

        // Skip the first table (if needed)
        setDropdownItems(tableNames.slice(1));

        if (tableNames.length > 1) {
          setSelectedTable(tableNames[1]);
        } else if (tableNames.length > 0) {
          setSelectedTable(tableNames[0]);
        }
      } catch (error) {
        console.error("Error fetching dropdown items:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTables();
  }, []);

  const handleSelect = (itemValue: string) => {
    setSelectedTable(itemValue);
    console.log("Selected Table:", itemValue);
    router.push({
      pathname: "/",
      params: { selectedTable: itemValue },
    });
  };

  if (loading) {
    return (
      <View style={styles.loaderContainer}>
        <ActivityIndicator size="large" color="#000" />
        <Text style={styles.loaderText}>Loading table list...</Text>
      </View>
    );
  }

  return (
    <LinearGradient
      colors={["#f0f8ff", "#e6f7ff", "#b3e0ff"]}
      style={styles.container}
    >
      <Text style={styles.title}>Select a Table</Text>
      <View style={styles.pickerWrapper}>
        <Picker
          selectedValue={selectedTable}
          onValueChange={handleSelect}
          style={styles.picker}
        >
          {dropdownItems.map((tableName) => (
            <Picker.Item key={tableName} label={tableName} value={tableName} />
          ))}
        </Picker>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 20,
  },
  loaderContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#b3e0ff",
  },
  loaderText: {
    color: "#333",
    fontSize: 18,
    marginTop: 10,
    fontWeight: "600",
  },
  title: {
    fontSize: 24,
    color: "#333",
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 20,
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: "#fff",
    borderRadius: 10,
    overflow: "hidden",
    backgroundColor: "rgba(255, 255, 255, 0.8)",
  },
  picker: {
    height: 50,
    width: "100%",
    color: "#192f5d",
    fontSize: 16,
  },
});

export default ExploreScreen;
