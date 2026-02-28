from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from analytics import get_sales_summary  # Make sure analytics.py is present

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1️⃣ Read CSV
        df = pd.read_csv(file.file)

        # 2️⃣ Compute basic stats
        total_sales = int(df['Sales'].sum())          # Convert to int
        avg_sales = float(df['Sales'].mean())        # Convert to float
        top_product = str(df.groupby('Product')['Sales'].sum().idxmax())

        # 3️⃣ Get chart data
        monthly_sales, product_sales = get_sales_summary(df)

        # 4️⃣ Convert chart numbers to float for JSON
        for row in monthly_sales:
            row['Sales'] = float(row['Sales'])
        for row in product_sales:
            row['Sales'] = float(row['Sales'])

        # 5️⃣ Generate a static campaign (replace with AI if API key available)
        campaign = f"Promote {top_product} heavily. Offer discounts and target high-value customers."

        # 6️⃣ Return all data
        return {
            "total_sales": total_sales,
            "avg_sales": round(avg_sales, 2),
            "top_product": top_product,
            "monthly_sales": monthly_sales,
            "product_sales": product_sales,
            "campaign": campaign
        }

    except Exception as e:
        return {"error": str(e)}