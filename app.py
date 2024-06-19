from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from TEST import display_image
import cv2 as cv
from Email import get_email_for_bike_number
import os
from Phone import get_phone_for_bike_number

app = Flask(__name__, static_folder='static')
app.config['MONGO_URI'] = 'mongodb+srv://newuser:newuser123@cluster0.zwjwk35.mongodb.net/'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Replace with your SMTP port
app.config['MAIL_USERNAME'] = 'safetypublic52@gmail.com'
app.config['MAIL_PASSWORD'] = 'tzefccakaeaoddbi'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'nagachaitu1270@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None  # Optional, can be adjusted based on your needs
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mongo = PyMongo(app)
mail = Mail(app)

@app.route("/")
def ps52():
    return render_template("contact.html")
  
from flask_mail import Message
import os

@app.route("/login", methods=['GET', 'POST'])
def login():
    # global captchaValue
    if request.method == 'POST':
        bike_number = request.form.get('bike-number')
        entered_captcha = request.form.get('captcha-input')

        # Fetch the email associated with the bike number
        email = get_email_for_bike_number(bike_number)

        # Check if the captcha matches
        if email:
                # Fetch the frame (image) for the given bike number
            frame = display_image(bike_number)

            if frame is not None:
                    # Send an email with the frame (image) and note
                msg = Message("E-Challan Alert - Helmet Violation", sender='your_sender_email', recipients=[email])
                msg.body = "This is to inform you that an e-challan has been issued for a recent traffic violation. The violation pertains to not wearing a helmet while riding a vehicle. For your safety and to avoid further penalties, please verify this e-challan by visiting the official e-challan website. Ensure that you settle any fines or address the violation promptly."
                msg.html = "<p>Official E-Challan Website: [Website URL]</p><p>If you have any questions or require assistance, please contact our customer support team at [Contact Information].</p><p>Thank you for your cooperation in following traffic regulations.</p>"

                    # Save the frame (image) temporarily to the server
                frame_path = "temp_frame.jpg"  # Temporary path for the image
                cv.imwrite(frame_path, frame)

                    # Attach the frame (image) to the email
                with app.open_resource(frame_path) as image:
                    msg.attach("helmet_image.jpg", "image/jpeg", image.read())

                    # Send the email
                mail.send(msg)
                    # Remove the temporary image file
                os.remove(frame_path)

                return "Email sent successfully!"
            else:
                return "Image not found for the given bike number."
        else:
            return "Bike number not found in the database."

    return render_template("login.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    
