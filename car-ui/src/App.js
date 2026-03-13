import { useState } from "react";
import carImage from "./assets/car-logo2.jpg";

function App() {
  const [query, setQuery] = useState("");
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(false);
 // helper to pick color based on fuel type
  const fuelColor = (fuel) => {
    switch (fuel.toLowerCase()) {
      case "petrol": return "#e67e22";
      case "diesel": return "#3498db";
      case "hybrid": return "#27ae60";
      case "electric": return "#9b59b6";
      default: return "#7f8c8d";
    }
  };

  // helper to pick color based on transmission
  const transColor = (trans) => trans.toLowerCase() === "automatic" ? "#1abc9c" : "#e74c3c";

  const searchCars = async () => {
    if (!query) return;
    setLoading(true);

    try {
    const response = await fetch("http://127.0.0.1:8000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: query,
        top_k: 5
      })
    });

    const data = await response.json();
    setCars(data.results);
  } catch (error) {
    console.error("Error fetching car recommendations:", error);
  } finally {
    setLoading(false);
  }
};

return (
    <div style={{
      maxWidth: 1000,
      margin: "40px auto",
      fontFamily: "Arial, sans-serif",
      background: "linear-gradient(to bottom, #f5f7fa, #e4ebf5)",
      padding: 20,
      borderRadius: 10
    }}>
      <h1 style={{ textAlign: "center", marginBottom: 30, color: "#2c3e50" }}> AI Car Finder</h1>
<img
  src={carImage}
  alt="Lexus IS 350"
  style={{ width: "100%", height: 390, objectFit: "cover", borderRadius: 8 }}
/>
      {/* Fixed progress bar */}
      <div style={{ height: 4, backgroundColor: "#eee", marginBottom: 20, overflow: "hidden", borderRadius: 2 }}>
        {loading && (
          <div
            style={{
              width: "50%",
              height: "100%",
              backgroundColor: "#3498db",
              animation: "loading 1s linear infinite",
            }}
          />
        )}
      </div>

      {/* Search input + button */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 30 }}>
        <input
          type="text"
          placeholder="I want a family car under 25,000 euros"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: 1,
            padding: "12px 15px",
            fontSize: 16,
            border: "1px solid #ccc",
            borderRadius: 6,
            outline: "none",
            minWidth: 300,
          }}
          disabled={loading}
        />
        <button
          onClick={searchCars}
          disabled={loading}
          style={{
            marginLeft: 10,
            padding: "12px 20px",
            fontSize: 16,
            backgroundColor: loading ? "#95a5a6" : "#3498db",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: loading ? "not-allowed" : "pointer",
            transition: "background-color 0.2s",
          }}
          onMouseOver={(e) => !loading && (e.currentTarget.style.backgroundColor = "#2980b9")}
          onMouseOut={(e) => !loading && (e.currentTarget.style.backgroundColor = "#3498db")}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Car cards grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: 20
      }}>
        {cars.length === 0 && !loading && (
          <p style={{ gridColumn: "1/-1", textAlign: "center", color: "#7f8c8d" }}>
            No cars found yet.
          </p>
        )}

        {cars.map((car, i) => (
          <div key={i} style={{
            borderRadius: 10,
            backgroundColor: "#fff",
            boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
            overflow: "hidden",
            transition: "transform 0.2s",
          }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}>

            {/* Card content */}
            <div style={{ padding: 15 }}>
              <h3 style={{ margin: "0 0 10px 0", color: "#34495e" }}>
                {car.brand} {car.model}
              </h3>

              <p style={{
                margin: "5px 0",
                fontWeight: "bold",
                fontSize: 18,
                color: "#e74c3c",
                backgroundColor: "#fdecea",
                display: "inline-block",
                padding: "2px 6px",
                borderRadius: 6
              }}>
                Price: €{car.price.toLocaleString()}
              </p>

              <div style={{ display: "flex", gap: 10, flexWrap: "wrap", margin: "10px 0" }}>
                <span style={{
                  backgroundColor: fuelColor(car.fuel_type),
                  color: "#fff",
                  padding: "2px 8px",
                  borderRadius: 6,
                  fontSize: 12
                }}>{car.fuel_type}</span>
                <span style={{
                  backgroundColor: transColor(car.transmission),
                  color: "#fff",
                  padding: "2px 8px",
                  borderRadius: 6,
                  fontSize: 12
                }}>{car.transmission}</span>
              </div>

              <p style={{ margin: "3px 0" }}>Year: {car.model_year}</p>
              <p style={{ margin: "3px 0" }}>Mileage: {car.milage} km</p>
              <p style={{ margin: "3px 0" }}>Interior: {car.int_col}</p>
              <p style={{ margin: "3px 0" }}>Exterior: {car.ext_col}</p>

              <span style={{
                display: "inline-block",
                marginTop: 10,
                padding: "2px 8px",
                backgroundColor: `rgba(52, 152, 219, ${Math.min(car.score, 1)})`,
                color: "#fff",
                borderRadius: 6,
                fontSize: 12
              }}>Score: {car.score.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}
export default App;