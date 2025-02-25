import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageTk, Image
import speech_recognition as sr
import pyttsx3
import datetime
import requests
import threading
import webbrowser

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to speak a response
def speak(text):
    engine.say(text)
    engine.runAndWait()

predefined_contacts = {
    "akshat": "+919324568711",
    "dipen" : "+917506629379",
    "Alice": "+1987654321",
    "Bob": "+1122334455",
    # Add more contacts as needed
}

# Function to listen to the microphone
def listen():
    with sr.Microphone() as source:
        status_label.config(text="Listening...", fg="#3498db")  # Blue color
        window.update()
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    status_label.config(text="Processing...", fg="#e74c3c")  # Red color
    window.update()

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""

# Function to get the current time
def get_current_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {current_time}"

# Function to get weather information
def get_weather(city_name):
    api_key = "c6e315d09197cec231495138183954bd"  # OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}  # You can adjust units as per your preference

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data["cod"] == 200:
            weather_desc = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"The weather in {city_name} is {weather_desc} with a temperature of {temperature}°C."
        else:
            return "Sorry, unable to fetch weather information."
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, an error occurred while fetching weather information."

def get_bitcoin_price():
    api_url = "https://api.coindesk.com/v1/bpi/currentprice.json"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            bitcoin_price = data["bpi"]["USD"]["rate"]
            return f"The current price of Bitcoin is {bitcoin_price} USD."
        else:
            return "Failed to retrieve Bitcoin price. Please try again later."
    except Exception as e:
        return f"An error occurred: {e}"

# Function to open a web page
def open_webpage(url):
    webbrowser.open(url)

# Function to extract the contact name from the user command
def extract_contact_name(command):
    # Example: "call John" -> Extract "John"
    parts = command.lower().split("call ")
    if len(parts) > 1:
        return parts[1].strip()
    else:
        return ""

# Function to get the phone number of a contact
def get_phone_number(contact_name):
    return predefined_contacts.get(contact_name)

from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'AC1800cb40c18d29e041633d3c00431236'
auth_token = '4b4381bacb64fc902614737e235c5b02'

# Initialize Twilio client
client = Client(account_sid, auth_token)

def make_call(contact_name):
    phone_number = get_phone_number(contact_name)
    if phone_number:
        try:
            # Make a call using Twilio
            call = client.calls.create(
                twiml='<Response><Say>Hello, you are receiving a call from the voice assistant.</Say></Response>',
                to=phone_number,
                from_='+12513364174'
            )
            response_box.insert(tk.END, f"Assistant: Calling {contact_name}...\n")
            speak(f"Calling {contact_name}...")
        except Exception as e:
            print(f"Twilio Error: {str(e)}")  # Print the full exception details
            response_box.insert(tk.END, f"Assistant: Failed to make the call: {str(e)}\n")
            speak("Sorry, there was an error while making the call.")
    else:
        response_box.insert(tk.END, f"Assistant: Contact {contact_name} not found.\n")
        speak(f"Sorry, I couldn't find contact {contact_name}.")

def handle_input():
    command = listen()
    if command:
        user_command_label.config(text=f"User said: {command}", fg="#2ecc71")  # Green color
    if "hello" in command:
        response_box.insert(tk.END, "Assistant: Hello! How can I assist you today?\n")
        speak("Hello! How can I assist you today?")
    elif "time" in command:
        current_time = get_current_time()
        response_box.insert(tk.END, f"Assistant: {current_time}\n")
        speak(current_time)
    elif "bitcoin" in command:
        bitcoin_price_info = get_bitcoin_price()
        response_box.insert(tk.END, f"Assistant: {bitcoin_price_info}\n")
        speak(bitcoin_price_info)
    elif "weather" in command:
        city_name = command.split("weather in ")[1]
        weather_info = get_weather(city_name)
        response_box.insert(tk.END, f"Assistant: {weather_info}\n")
        speak(weather_info)
    elif "open" in command:
        search_query = command.split("open ")[1]
        response_box.insert(tk.END, f"Assistant: Opening web page for {search_query}\n")
        speak(f"Opening web page for {search_query}")
        open_webpage(f"https://www.google.com/search?q={search_query}")

    elif "call" in command:
         contact_name = extract_contact_name(command)
         make_call(contact_name)

    elif "exit" in command:
        response_box.insert(tk.END, "Assistant: Goodbye!\n")
        speak("Goodbye!")
        exit()
    else:
        response_box.insert(tk.END, "Assistant: I'm sorry, I didn't catch that.\n")
        speak("I'm sorry, I didn't catch that.")
    status_label.config(text="", fg="#f0f0f0")  # Set back to the default color

# Function to handle user input in a separate thread
def handle_input_thread():
    threading.Thread(target=handle_input).start()

# Function to handle the "Speak" button click event
def speak_button_clicked():
    handle_input_thread()

# Create the main window
window = tk.Tk()
window.title("Voice Assistant")

# Set window background color
window.configure(bg="#ecf0f1")  # Light gray background

# Load assistant image
image = Image.open("assitant_image.jpg")
image = image.resize((150, 150), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(image)

# Create a label to display assistant image
image_label = tk.Label(window, image=photo, bg="#ecf0f1")  # Light gray background
image_label.pack(pady=10)

# Create a label for user command
user_command_label = tk.Label(window, text="User said: ", bg="#ecf0f1", font=("Arial", 10), fg="#2ecc71")  # Green color
user_command_label.pack(pady=5)

# Create a text box to display responses
response_box = scrolledtext.ScrolledText(window, width=50, height=10, wrap=tk.WORD, bg="#34495e", fg="#ecf0f1")  # Dark blue background, light text
response_box.pack(padx=10, pady=5)

# Create a "Speak" button
speak_button = tk.Button(window, text="Speak", command=speak_button_clicked, bg="#3498db", fg="#ecf0f1", font=("Arial", 12))  # Blue button with light text
speak_button.pack(pady=5)

# Create a status label
status_label = tk.Label(window, text="", bg="#ecf0f1", font=("Arial", 10))
status_label.pack(pady=5)

# Run the main event loop
window.mainloop()
