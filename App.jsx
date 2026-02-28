import React, { useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, Legend
} from "recharts";

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return setError("Please select a file.");
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError("Upload failed! Make sure backend is running.");
    }
  };

  return (
    <div className="p-8 font-sans">
      <h1 className="text-3xl mb-4 font-bold">MarketMind Dashboard</h1>

      <div className="mb-4">
        <input type="file" onChange={handleFileChange} />
        <button
          className="ml-2 p-2 bg-blue-600 text-white rounded"
          onClick={handleUpload}
        >
          Upload
        </button>
      </div>

      {error && <p className="text-red-600">{error}</p>}

      {data && !data.error && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="p-4 bg-gray-100 rounded shadow">
              <h2 className="font-bold">Total Sales</h2>
              <p>${data.total_sales}</p>
            </div>
            <div className="p-4 bg-gray-100 rounded shadow">
              <h2 className="font-bold">Average Sales</h2>
              <p>${data.avg_sales}</p>
            </div>
            <div className="p-4 bg-gray-100 rounded shadow">
              <h2 className="font-bold">Top Product</h2>
              <p>{data.top_product}</p>
            </div>
          </div>

          <h2 className="text-2xl mb-2 font-bold">Monthly Sales</h2>
          <LineChart width={600} height={300} data={data.monthly_sales}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="Sales" stroke="#8884d8" />
          </LineChart>

          <h2 className="text-2xl mt-8 mb-2 font-bold">Product-wise Sales</h2>
          <BarChart width={600} height={300} data={data.product_sales}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Product" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Sales" fill="#82ca9d" />
          </BarChart>

          <h2 className="text-2xl mt-8 mb-2 font-bold">Campaign Suggestion</h2>
          <p>{data.campaign}</p>
        </>
      )}

      {data && data.error && <p className="text-red-600">{data.error}</p>}
    </div>
  );
}

export default App;