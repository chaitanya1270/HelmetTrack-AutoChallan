from pymongo import MongoClient
connection_string = "mongodb+srv://newuser:newuser123@cluster0.zwjwk35.mongodb.net/"
client = MongoClient(connection_string)
db = client["Helmet-detection"]

# Function to get the email for a given bike number
def get_phone_for_bike_number(bike_number):
    images_in_collection = db["bike_number"]
    query = {"bike_number": bike_number}
    result = images_in_collection.find_one(query)
    if result:
        return result["phone_number"]
    else:
        return None

# Bike number for which you want to retrieve the email
# bike_number_to_check = "HR26D05554"

# Get the email associated with the bike number
