export async function getWeatherData() {
  try {
    const response = await fetch(
      "https://weather-backend-api-737404936819.asia-south1.run.app/weather"
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json = await response.json();

    return json;
  } catch (error) {
    console.error("❌ Error fetching weather data:", error);
    return null;
  }
}
