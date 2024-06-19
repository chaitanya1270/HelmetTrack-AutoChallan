from pymongo import MongoClient
import cv2
import numpy as np
import base64

# MongoDB connection details
connection_string = "mongodb+srv://newuser:newuser123@cluster0.zwjwk35.mongodb.net/"
db_name = "Helmet-detection"
collection_name = "without-helmet"

# Function to retrieve and display the image
def display_image(bike_num):
    client = MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]

    # Query the collection for the document with the specified bike_num
    document = collection.find_one({"bike_num": bike_num})

    if document:
        # Retrieve and decode the frame data from the document
        frame_bytes = document["frame"]

        # Convert frame data to a NumPy array
        frame_np = np.frombuffer(frame_bytes, np.uint8)

        # Decode the frame using OpenCV
        frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
        return frame
        # Display the image using OpenCV
        # cv2.imshow("Image", frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        print(f"No document found for bike_num: {bike_num}")

# Specify the bike_num you want to retrieve
# bike_num = "HR26D05554"

# Call the function to retrieve and display the image
# display_image(bike_num)
