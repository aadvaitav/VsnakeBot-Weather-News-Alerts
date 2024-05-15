import requests
import streamlit as st
from gdacs.api import GDACSAPIReader
from email.message import EmailMessage
import smtplib

client = GDACSAPIReader()

def get_latest_event_info(event_type):
    event = client.latest_events(event_type=event_type, limit=1)

    if event:
        event_data = event.features[0]

        country = event_data['properties'].get('country', 'Not available')
        name = event_data['properties'].get('name', 'Not available')
        source = event_data.get('url', {}).get('report', 'Not available')  # Added error handling

        return country, name, source
    else:
        return 'NA', 'NA', 'NA'

# Function to display event info
def display_event_info(event_type, country, name, source):
    st.subheader(f"{event_type} Info:")
    st.write("Country:", country)
    st.write("Title:", name)
    st.write("Report:", source)
    st.write("\n")

def get_weather(api_key, location):
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=1&aqi=no&alerts=no" #change the url with the url from where you are getting the weather api
    response = requests.get(url)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Error: {response.status_code}")
        return None

def analyze_weather(weather_data):
    # Analyze current weather conditions
    current_conditions = []
    current_temperature_c = weather_data['current']['temp_c']
    current_condition = weather_data['current']['condition']['text']
    current_conditions.append(f"Current weather: {current_condition}, Temperature: {current_temperature_c}°C")

    # Analyze upcoming weather forecast for the next hours
    forecast_conditions = []
    for hour in weather_data['forecast']['forecastday'][0]['hour']:
        forecast_time = hour['time']
        forecast_condition = hour['condition']['text']
        forecast_temperature_c = hour['temp_c']
        forecast_conditions.append(f"At {forecast_time}: {forecast_condition}, Temperature: {forecast_temperature_c}°C")

    return current_conditions, forecast_conditions

def get_weather_report(api_key, location):
    weather_data = get_weather(api_key, location)

    if weather_data:
        # Analyze weather conditions
        current_conditions, forecast_conditions = analyze_weather(weather_data)


        all_conditions = current_conditions + forecast_conditions


        weather_report = []


        weather_report.append("**Current Weather Conditions**")
        if current_conditions:
            for condition in current_conditions:
                weather_report.append(condition)


        weather_report.append("**Forecasted Weather Conditions for the Next Hours**")
        if forecast_conditions:
            for forecast in forecast_conditions:
                weather_report.append(forecast)

        # Add precautions based on weather conditions to report
        weather_report.append("**Precautions:**")
        displayed_precautions = set()  # Set to store displayed precautions
        for condition in all_conditions:
            if "High wind speed" in condition and "High wind speed" not in displayed_precautions:
                weather_report.append("- Secure loose objects and stay indoors if possible.")
                displayed_precautions.add("High wind speed")
            elif "High temperature" in condition and "High temperature" not in displayed_precautions:
                weather_report.append("- Stay hydrated and avoid prolonged exposure to the sun.")
                displayed_precautions.add("High temperature")
            elif "Low temperature" in condition and "Low temperature" not in displayed_precautions:
                weather_report.append("- Dress warmly and avoid prolonged exposure to cold.")
                displayed_precautions.add("Low temperature")
            elif "Rain" in condition and "Rain" not in displayed_precautions:
                weather_report.append("- Carry an umbrella and drive carefully.")
                displayed_precautions.add("Rain")
            elif "Thunder" in condition and "Thunder" not in displayed_precautions:
                weather_report.append("- Seek shelter indoors immediately. Avoid open areas and tall objects.")
                displayed_precautions.add("Thunder")
            elif "Mist" in condition and "Mist" not in displayed_precautions:
                weather_report.append("- Drive with caution, especially in areas with reduced visibility.")
                weather_report.append("- Use fog lights if driving.")
                weather_report.append("- Keep a safe distance from other vehicles.")
                weather_report.append("- Use windshield wipers and defrosters to improve visibility.")
                weather_report.append("- Avoid sudden stops and sharp turns.")
                weather_report.append(
                    "- Be alert for pedestrians and cyclists, as they may be less visible in misty conditions.")
                weather_report.append(
                    "- If visibility is severely reduced, consider pulling over to a safe location until conditions improve.")
                displayed_precautions.add("Mist")

        return weather_report
    else:
        return ["Failed to retrieve weather data."]

def greet():
    return "Hello! I'm an intelligent bot. How can I assist you today?"

def get_news(api_key):
    url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}' #replace the url with the url from where you are getting the news api

    try:
        response = requests.get(url)
        data = response.json()
        if 'articles' in data:
            articles = data['articles']
            news = []
            for article in articles:
                title = article.get('title', 'No title available')
                source = article['source'].get('name', 'Unknown source')
                description = article.get('description', 'No description available')
                url = article.get('url', '#')
                news.append(f"- **Title:** {title}\n  **Source:** {source}\n  **Description:** {description}\n  **URL:** {url}\n")
            return news
        else:
            return ["No news found."]
    except Exception as e:
        return ["An error occurred:", e]

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "user@gmail.com" #replace user@gmail.com with your gmail id
    msg['from'] = user
    password = "password" #replace password with your password

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

def get_response(input_text, api_keys):
    weather_api_key, news_api_key = api_keys
    if "hi" in input_text.lower():
        return "Hi there!"
    elif "get weather" in input_text.lower():
        location = "enter location" #location can be changed here
        return get_weather_report(weather_api_key, location)
    elif "get news" in input_text.lower():
        return get_news(news_api_key)
    elif "get natural disaster events" in input_text.lower():
        # Fetch latest event info for TC, FL, and EQ
        tc_country, tc_name, tc_source = get_latest_event_info('TC')
        fl_country, fl_name, fl_source = get_latest_event_info('FL')
        eq_country, eq_name, eq_source = get_latest_event_info('EQ')


        event_info = [
            ('Tropical Cyclone', tc_country, tc_name, tc_source),
            ('Flood', fl_country, fl_name, fl_source),
            ('Earthquake', eq_country, eq_name, eq_source)
        ]


        for item in event_info:
            if item[0] == "Flood":
                precautions = """Precautions for Flood:
- Evacuate to higher ground if instructed to do so.
- Avoid walking or driving through floodwaters.
- Stay away from bridges over fast-moving water.
- Keep children and pets away from floodwaters.
- Listen to emergency alerts and instructions from authorities."""
                email_alert("Flood Alert", precautions, "a@gmail.com")#enter the gmail id to be notified for precautions
                st.write("Bot: Flood alert sent!")
            if item[0] == "Earthquake":
                precautions = """Precautions for Earthquake:
            - Drop, Cover, and Hold On: Drop down to your hands and knees, cover your head and neck with your arms, and hold on to any sturdy furniture or object nearby.
            - Stay Indoors: If you're indoors, stay there. Avoid doorways and windows, as they can pose a risk of injury from falling debris.
            - Stay Away from Hazardous Areas: Avoid areas near windows, glass, exterior walls, and heavy objects that could fall.
            - Evacuate If Necessary: If you're in a multi-story building and you can safely evacuate, do so. Use stairs, not elevators.
            - After the Earthquake: Check for injuries, fire hazards, gas leaks, and structural damage. Be prepared for aftershocks."""
                email_alert("Earthquake Alert", precautions, "a@gmail.com")#enter the gmail id to be notified for precautions
                st.write("Bot: Earthquake alert sent!")

            elif item[0] == "Tropical Cyclone":
                precautions = """Precautions for Tropical Cyclone:
            - Stay Informed: Monitor weather forecasts and updates from local authorities. Follow evacuation orders if issued.
            - Secure Your Property: Secure loose objects around your property, such as outdoor furniture and garden tools, to prevent them from becoming projectiles in strong winds.
            - Stay Indoors: Seek shelter in a sturdy building, away from windows and doors.
            - Prepare an Emergency Kit: Have an emergency kit ready with essentials such as water, non-perishable food, flashlight, batteries, first aid supplies, and important documents.
            - Evacuate Early if Advised: If you're in a vulnerable area, evacuate early to a safe location."""
                email_alert("Cyclone Alert", precautions, "a@gmail.com")#enter the gmail id to be notified for precautions
                st.write("Bot: Cyclone alert sent!")

        return event_info
    else:
        return "I'm sorry, I didn't understand that. You can ask for weather information by saying 'Get Weather', news by saying 'Get News', or natural disaster events by saying 'Get Natural Disaster Events'."

def main(weather_api_key, news_api_key):
    st.title("Vsnake Chatbot")

    st.write(greet())

    while True:
        user_input = st.text_input("You:", key=hash("You:")).strip()

        if not user_input:
            continue

        if user_input.lower() == "bye":
            st.write("Bot: Goodbye! Have a great day.")
            break
        else:
            response = get_response(user_input, (weather_api_key, news_api_key))
            if isinstance(response, str):
                st.write("Bot:", response)
            else:
                for item in response:
                    if isinstance(item, tuple):
                        display_event_info(*item)
                    else:
                        st.markdown(item, unsafe_allow_html=True)

if __name__ == "__main__":
    weather_api_key = "enter your api key for weather" #replace with your api key for obtaining weather
    news_api_key = "enter your api key for news" #replace with your api key for obtaining news
    main(weather_api_key, news_api_key)
