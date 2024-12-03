#Step 1: Setup the widgets for dynamic parameters

dbutils.widgets.text("query", "restaurant", "Query")  # Default to "restaurant"
dbutils.widgets.text("near", "Kuala Lumpur", "Near")  # Default to "Kuala Lumpur"
dbutils.widgets.text("limit", "50", "Limit")  # Default limit to 50

# Step 2: Fetching widget values
query = dbutils.widgets.get("query")
near = dbutils.widgets.get("near")
limit = int(dbutils.widgets.get("limit"))

# IStep 3: Install necessary libraries
%pip install plotly requests pandas

import plotly.express as px
import pandas as pd
import requests
import plotly.graph_objects as go

# Step 4: Fetch data from the Foursquare API
api_url = "https://api.foursquare.com/v3/places/search"
headers = {
    "Accept": "application/json",
    "Authorization": ""  # Replace with your Foursquare API key
}
params = {
    "query": query,
    "near": near,
    "limit": limit
}
response = requests.get(api_url, headers=headers, params=params)

# Step 5: Check API response and extract details
if response.status_code == 200:
    data = response.json()
    restaurants = data.get("results", [])
else:
    raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

# Step 6: Convert data to a DataFrame
restaurants_list = []
for restaurant in restaurants:
    name = restaurant.get("name")
    latitude = restaurant["geocodes"]["main"]["latitude"]
    longitude = restaurant["geocodes"]["main"]["longitude"]
    address = ", ".join(restaurant.get("location", {}).get("formatted_address", "").split(","))
    category = restaurant["categories"][0]["name"] if restaurant.get("categories") else "Unknown"
    
    # Extract rating (if available)
    rating = restaurant.get("rating", "N/A")
    
    # Extract opening and closing hours (if available)
    hours = restaurant.get("hours", {}).get("status", "N/A") if "hours" in restaurant else "N/A"
    
    # Extract review count (if available)
    review_count = restaurant.get("stats", {}).get("totalCount", 0)
    
    restaurants_list.append({
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
        "category": category,
        "rating": rating,
        "hours": hours,
        "review_count": review_count
    })

restaurants_df = pd.DataFrame(restaurants_list)

# Step 7: Create color mapping for categories
category_colors = {
    "Restaurant": "blue",
    "Cafe": "green",
    "Fast Food": "red",
    "Bar": "purple",
    "Pizza": "orange",
    "Unknown": "gray"  # For any undefined categories
}

# Step 8: Plot the restaurant map
fig_map = px.scatter_mapbox(
    restaurants_df,
    lat="latitude",
    lon="longitude",
    color="category",
    color_discrete_map=category_colors,
    hover_name="name",
    hover_data=["address", "category", "rating", "hours", "review_count"],
    title="Restaurant Map in " + near,
    zoom=12,
)

fig_map.update_layout(mapbox_style="carto-positron")

# Step 9: Plot the bar chart for category distribution
fig_bar = px.bar(
    restaurants_df['category'].value_counts().reset_index(),
    x='index',
    y='category',
    labels={'index': 'Category', 'category': 'Count'},
    title="Restaurant Categories in " + near,
    color='index',  # This is key to matching the category color with map and Sunburst chart
    color_discrete_map=category_colors
)

# Step 10: Create a Sunburst chart
category_counts = restaurants_df['category'].value_counts().reset_index()

# Define labels, parents, and values for Sunburst chart
labels = category_counts['index'].tolist()
parents = [""] * len(labels)  # All categories are root categories, so no parents
values = category_counts['category'].tolist()

# Create Sunburst chart using plotly.graph_objects
fig_sunburst = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total"
))

# Customize chart layout
fig_sunburst.update_layout(
    title="Restaurant Category Distribution (Sunburst Chart)",
    margin=dict(t=40, l=0, r=0, b=0)
)

# Display the figures in Databricks
fig_map.show()
fig_bar.show()
fig_sunburst.show()

# Display the DataFrame as a table at the bottom of the plots
restaurants_df.head(10)  # Display first 10 rows of the DataFrame as a table
