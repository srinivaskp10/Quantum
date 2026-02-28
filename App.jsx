import { useState } from "react";
import axios from "axios";
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";

export default function App() {
  const [data, setData] = useState(null);

  const uploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post(
      "http://127.0.0.1:8000/upload",
      formData
    );

    setData(res.data);
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>🚀 AI Sales Intelligence</h1>
        <p style={styles.subtitle}>
          Upload CSV → Get Insights
        </p>

        {/* Upload Panel */}
        <div style={styles.upload}>
          <h2>Upload Sales CSV</h2>
          <input type="file" onChange={uploadFile} />
        </div>

        {data && (
          <>
            {/* KPI Cards */}
            <div style={styles.stats}>
              <Card title="Total Sales" value={data.total_sales} />
              <Card title="Average Sales" value={data.avg_sales} />
              <Card title="Top Product" value={data.top_product} />
            </div>

            {/* Charts */}
            <div style={styles.charts}>
              <ChartCard title="Monthly Sales">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.monthly_sales}>
                    <XAxis dataKey="Month" stroke="#ccc" />
                    <YAxis stroke="#ccc" />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="Sales"
                      stroke="#22d3ee"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Product Sales">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.product_sales}>
                    <XAxis dataKey="Product" stroke="#ccc" />
                    <YAxis stroke="#ccc" />
                    <Tooltip />
                    <Bar dataKey="Sales" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Campaign */}
            <div style={styles.campaign}>
              💡 AI Campaign Strategy: {data.campaign}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* Components */

function Card({ title, value }) {
  return (
    <div style={styles.card}>
      <div>{title}</div>
      <h2>{value}</h2>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div style={styles.chartCard}>
      <h3>{title}</h3>
      {children}
    </div>
  );
}

/* Styles */

const styles = {
  page: {
    minHeight: "100vh",
    background:
      "radial-gradient(circle at top, #0f172a, #020617)",
    color: "white",
    fontFamily: "Poppins, sans-serif",
    padding: 30
  },

  container: {
    maxWidth: 1200,
    margin: "auto"
  },

  title: {
    fontSize: 42,
    textAlign: "center"
  },

  subtitle: {
    textAlign: "center",
    color: "#94a3b8",
    marginBottom: 30
  },

  upload: {
    background: "rgba(255,255,255,0.05)",
    border: "2px dashed #38bdf8",
    padding: 30,
    borderRadius: 20,
    textAlign: "center",
    marginBottom: 30,
    backdropFilter: "blur(10px)"
  },

  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 20,
    marginBottom: 30
  },

  card: {
    background: "rgba(255,255,255,0.05)",
    padding: 20,
    borderRadius: 18,
    textAlign: "center",
    backdropFilter: "blur(12px)",
    boxShadow: "0 0 25px rgba(56,189,248,0.2)"
  },

  charts: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 25,
    marginBottom: 30
  },

  chartCard: {
    background: "rgba(255,255,255,0.05)",
    padding: 20,
    borderRadius: 18
  },

  campaign: {
    background:
      "linear-gradient(135deg,#6366f1,#22d3ee)",
    padding: 25,
    borderRadius: 20,
    color: "#020617",
    fontWeight: "600",
    fontSize: 18
  }
};