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
          Upload CSV → Get AI Insights
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

            {/* Charts — STACKED */}
            <div style={styles.charts}>
              <ChartCard title="Monthly Sales">
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={data.monthly_sales}>
                    <XAxis dataKey="Month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="Sales"
                      stroke="#38bdf8"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Product Sales">
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={data.product_sales}>
                    <XAxis dataKey="Product" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
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

/* 🎨 STYLES — PREMIUM */

const styles = {
  page: {
    minHeight: "100vh",
    background:
      "linear-gradient(135deg, #020617 0%, #0f172a 40%, #020617 100%)",
    color: "white",
    fontFamily: "Poppins, sans-serif",
    padding: 30
  },

  container: {
    maxWidth: 1000,
    margin: "auto"
  },

  title: {
    fontSize: 42,
    textAlign: "center",
    background:
      "linear-gradient(90deg,#38bdf8,#6366f1)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent"
  },

  subtitle: {
    textAlign: "center",
    color: "#94a3b8",
    marginBottom: 30
  },

  upload: {
    background: "rgba(255,255,255,0.06)",
    border: "2px dashed #38bdf8",
    padding: 30,
    borderRadius: 18,
    textAlign: "center",
    marginBottom: 30,
    backdropFilter: "blur(12px)"
  },

  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 20,
    marginBottom: 30
  },

  card: {
    background: "rgba(255,255,255,0.06)",
    padding: 20,
    borderRadius: 18,
    textAlign: "center",
    backdropFilter: "blur(10px)",
    boxShadow: "0 0 25px rgba(56,189,248,0.25)"
  },

  /* 🔥 STACKED CHARTS */
  charts: {
    display: "flex",
    flexDirection: "column",
    gap: 25,
    marginBottom: 30
  },

  chartCard: {
    background: "rgba(255,255,255,0.06)",
    padding: 20,
    borderRadius: 18,
    backdropFilter: "blur(10px)"
  },

  campaign: {
    background:
      "linear-gradient(135deg,#6366f1,#22d3ee)",
    padding: 25,
    borderRadius: 18,
    color: "#020617",
    fontWeight: "600",
    fontSize: 18
  }
};