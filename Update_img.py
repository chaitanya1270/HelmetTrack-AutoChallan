from pymongo import MongoClient
import cv2 as cv

# MongoDB connection details
connection_string = "mongodb+srv://newuser:newuser123@cluster0.zwjwk35.mongodb.net/"
db_name = "Helmet-detection"
collection_name = "without-helmet"

# Function to insert data into the MongoDB collection
def insert_data_into_mongodb(Bike_num, Frame):
    client = MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]
    
    # Convert the image to binary format (e.g., using OpenCV and BytesIO)
    image_binary = cv.imencode('.jpg', Frame)[1].tobytes()
    
    # Create a document to insert into the collection
    data_to_insert = {
        "bike_num": Bike_num,
        "frame": image_binary  # You can store the frame data here (e.g., as a binary image)
    }

    # Insert the document into the collection
    collection.insert_one(data_to_insert)
# Example usage
# Bike_num = "ABC123"
# Frame1 = cv.imread("frame1.jpg")

# insert_data_into_mongodb(Bike_num, Frame1)
