import pandas as pd

# Load all datasets
listings = pd.read_json("data/listings_final_expanded.json")
properties = pd.read_json("data/property_attributes_final_expanded.json")
agents = pd.read_json("data/agents_cleaned.json")
buyers = pd.read_json("data/buyers_cleaned.json")
sales = pd.read_csv("data/sales_cleaned.csv")

print("✅ All datasets loaded successfully!\n")

print("Listings Shape:", listings.shape)
print("Properties Shape:", properties.shape)
print("Agents Shape:", agents.shape)
print("Buyers Shape:", buyers.shape)
print("Sales Shape:", sales.shape)