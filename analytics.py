import pandas as pd

def get_sales_summary(df):
    # Make sure 'Date' exists; if not, use current date for demo
    if 'Date' not in df.columns:
        df['Date'] = pd.Timestamp.today()

    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')

    # Monthly sales
    monthly_sales = df.groupby('Month')['Sales'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Month'].astype(str)

    # Product-wise sales
    product_sales = df.groupby('Product')['Sales'].sum().reset_index()

    return monthly_sales.to_dict(orient='records'), product_sales.to_dict(orient='records')