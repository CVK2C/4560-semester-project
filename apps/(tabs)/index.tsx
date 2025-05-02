import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  useColorScheme,
  ActivityIndicator,
} from "react-native";
import { VictoryChart, VictoryCandlestick, VictoryAxis } from "victory-native";
import { useLocalSearchParams } from "expo-router";
import { LinearGradient } from "expo-linear-gradient"; // Import LinearGradient

// Define the type for the data
interface CandlestickData {
  trade_id: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  start_time: number;
}

function formatTime(nanoTimestamp: number | string): Date {
  const millis = Number(nanoTimestamp) / 1_000_000;
  return new Date(millis);
}

const HomeScreen = () => {
  const { selectedTable } = useLocalSearchParams<{ selectedTable: string }>();
  const [candlestickData, setCandlestickData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const colorScheme = useColorScheme();
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://10.118.131.151:5001//HomeScreen", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            selectedTable: selectedTable,
            limit: 50,
            offset: offset,
          }),
        });

        const result = await response.json();
        if (result.data) {
          const formatted = result.data
            .sort(
              (a: CandlestickData, b: CandlestickData) =>
                a.start_time - b.start_time
            )
            .map((item: CandlestickData) => ({
              x: formatTime(item.start_time),
              open: item.open,
              close: item.close,
              high: item.high,
              low: item.low,
            }));

          setCandlestickData(formatted);
        } else {
          console.warn("No data found.");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedTable, offset]);

  const loadMoreData = () => {
    setOffset((prevOffset) => prevOffset + 7);
  };

  const loadLessData = () => {
    setOffset((prevOffset) => Math.max(prevOffset - 7, 0));
  };

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <LinearGradient
        colors={["#f0f8ff", "#e6f7ff", "#b3e0ff"]}
        style={styles.container}
      >
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          <Text
            style={[
              styles.customTitle,
              { color: colorScheme === "dark" ? "black" : "#333" },
            ]}
          >
            {selectedTable}
          </Text>

          {loading ? (
            <ActivityIndicator size="large" color="#000" />
          ) : candlestickData.length > 0 ? (
            <VictoryChart domainPadding={{ x: 30 }} height={400}>
              <VictoryAxis
                label="Time"
                style={{
                  tickLabels: {
                    fontSize: 10,
                    angle: -45,
                    padding: 15,
                    fill: colorScheme === "dark" ? "#333" : "#000",
                  },
                }}
                scale="time"
                fixLabelOverlap
                tickFormat={(t) => {
                  const date = new Date(t);
                  const hours = date.getHours().toString().padStart(2, "0");
                  const minutes = date.getMinutes().toString().padStart(2, "0");
                  return `${hours}:${minutes}`;
                }}
              />
              <VictoryAxis
                dependentAxis
                style={{
                  axisLabel: {
                    fontSize: 12,
                    fill: colorScheme === "dark" ? "#333" : "#000",
                  },
                  tickLabels: {
                    fontSize: 10,
                    fill: colorScheme === "dark" ? "#333" : "#000",
                  },
                }}
              />
              <VictoryCandlestick
                candleColors={{ positive: "#81c784", negative: "#e57373" }}
                data={candlestickData}
                style={{
                  data: {
                    strokeWidth: 1,
                    stroke: "#333",
                  },
                }}
              />
            </VictoryChart>
          ) : (
            <Text style={styles.noDataText}>No candlestick data found.</Text>
          )}

          {!loading && (
            <View style={styles.loadMoreContainer}>
              <Text style={styles.loadMoreTitle}>Adjust Data</Text>
              <View style={styles.volumeButtons}>
                <Text style={styles.volumeButton} onPress={loadLessData}>
                  ➖
                </Text>
                <Text style={styles.volumeButton} onPress={loadMoreData}>
                  ➕
                </Text>
              </View>
            </View>
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 16,
  },
  customTitle: {
    fontSize: 24,
    fontWeight: "700",
    textTransform: "uppercase",
    marginBottom: 16,
    textAlign: "center",
    letterSpacing: 2,
  },
  scrollContainer: {
    alignItems: "center",
  },
  noDataText: {
    fontSize: 18,
    color: "#333",
    textAlign: "center",
    marginTop: 20,
  },
  loadMoreContainer: {
    marginTop: 20,
    alignItems: "center",
  },
  loadMoreTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
    color: "#333",
  },
  volumeButtons: {
    flexDirection: "row",
    gap: 20,
  },
  volumeButton: {
    fontSize: 30,
    backgroundColor: "#81c784",
    color: "white",
    paddingVertical: 5,
    paddingHorizontal: 15,
    borderRadius: 10,
    overflow: "hidden",
  },
});

export default HomeScreen;
