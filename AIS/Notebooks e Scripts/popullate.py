import csv
from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017"
 
# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient

client = MongoClient(CONNECTION_STRING)

print(client.list_database_names())

db = client["ais"]
collection = db["dados"]

with open('merged.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        collection.insert_one({
        "country_code": row["Country Code"],
        "year": int(row["year"]),
        "gdp": float(row["gdp"]),
        "inflation": float(row["inflation"]),
        "govexp": float(row["govexp"]),
        "literacy_rate": float(row["literacy_rate"])
        })


client.close()