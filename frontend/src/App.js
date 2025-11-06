import React, { useEffect, useState } from "react";
import { getWeatherData } from "./apis/api";
import "./App.css";

function App() {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetchData() {
    try {
      const result = await getWeatherData();
      if (result) setWeatherData(result);
    } catch (error) {
      console.error("❌ Failed to fetch weather data:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 600000);
    return () => clearInterval(interval);
  }, []);

  const refreshNow = async () => {
    setRefreshing(true);
    await fetchData();
  };

  if (loading)
    return (
      <div className="status-screen">
        <p className="loading">⏳ Loading latest weather data...</p>
      </div>
    );

  if (!weatherData?.data?.result)
    return (
      <div className="status-screen">
        <p className="error">❌ Failed to fetch weather data.</p>
      </div>
    );

  const data = weatherData.data;

  return (
    <div className="App">
      <h1 className="title">🌦️ AI Weather Insights Dashboard</h1>

      <div className="meta">
        <p>
          <b>Processed at:</b> {new Date(data.processed_at).toLocaleString()}
        </p>
        <button
          className="refresh-btn"
          onClick={refreshNow}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "🔄 Refresh Now"}
        </button>
      </div>

      <table className="weather-table">
        <thead>
          <tr>
            <th>City</th>
            <th>Mood</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.result).map(([city, details]) => (
            <tr key={city}>
              <td>{city}</td>
              <td className={`mood ${details.mood.toLowerCase()}`}>
                {details.mood}
              </td>
              <td>{details.summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
