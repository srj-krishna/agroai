import streamlit as st
import os
import embedchain
from streamlit.logger import get_logger
import azure.ai.translation.text
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError
from streamlit_js_eval import get_geolocation
import requests
from geopy.geocoders import Nominatim
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


st.set_page_config(
    page_title=("AgroNeuBot"),
    page_icon="🌱",
    )

version = embedchain.__version__
st.title("💬 AgroNeuBot")
st.caption("🚀 powered by AgroNeuLM and AgroNeuGraph from NeuBiom Labs!")
system_message = "You are an AgroNeubot, here to help with information and context-specific recommendations for farming in Kerala for the following query. If you don't know something just say that you don't have the information and only answer questions related to agriculture."
lang = "English"
final_prompt = ""
city = "NA"
state = "NA"
country = "NA"
               

@st.cache_resource
def agroneugraph():
    return embedchain.App.from_config("config.yaml")


conn = st.connection("gsheets", type=GSheetsConnection)

# initialize Nominatim API
geolocator = Nominatim(user_agent="neugeoloc")
WEATHER_KEY = st.secrets['WEATHER_KEY']
trkey = st.secrets['TRKEY']
os.environ["HUGGINGFACE_ACCESS_TOKEN"] = st.secrets['HUGGINGFACE_ACCESS_TOKEN']
os.environ["PINECONE_API_KEY"] = st.secrets['PINECONE_API_KEY']
text_translator = TextTranslationClient(credential = TranslatorCredential(trkey, "southeastasia"));


def chathistory_dataframe():
    return pd.DataFrame({
        'Date': [],
        'Query': [],
        'City': [],
        'State': [],
        'Country': []
    })

def find_current_weather(lat, lon):
    base_url  = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
    weatherdata = requests.get(base_url).json()
    return weatherdata


def translate_string(from_lang, to_lang, string):
    try:
        input_text_elements = [ InputTextItem(text = string) ]
        response = text_translator.translate(content = input_text_elements, to = [to_lang], from_parameter = from_lang)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                return translated_text.text

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
        return string  # return original string if translation fails

def get_final_answer(text):
        parts = text.rsplit("Answer:", 1)
        if len(parts) > 1:
            return parts[-1].strip()  # Stripping to remove any leading/trailing whitespace
        else:
            return "No answer found."

    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
        Hi! I'm AgroNeuBot, your personal agricultural assistant. I'm here to help you with information and context-specific recommendations for farming. How can I help you today? """,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
querylog = chathistory_dataframe()

with st.sidebar:
    lang = st.radio(
    "Select Language",
    ["English", "Malayalam(മലയാളം)", "Hindi(हिंदी)", "Tamil(தமிழ்)", "Kannada(ಕನ್ನಡ)", "Telugu(తెలుగు)"], index=0)
    
    if lang == "English":
        lang_code = 'en'
    elif lang == "Malayalam(മലയാളം)":
        lang_code = 'ml'
    elif lang == "Hindi(हिंदी)":
        lang_code = 'hi'
    elif lang == "Tamil(தமிழ்)":
        lang_code = 'ta'
    elif lang == "Kannada(ಕನ್ನಡ)":
        lang_code = 'kn'
    elif lang == "Telugu(తెలుగు)":
        lang_code = 'te'

        # List of crops
    crops = ["All crops", "Wheat", "Rice", "Maize", "Coffee","Coconut", "Arecanut", "Cashew", "Rubber", "Cardamom", "Banana", "Mango", "Soybean", "Potato", "Tomato", "Cotton", "Sugarcane", "Sunflower"]
    # List of states in India
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]

    # Create dropdown menu for selecting crop
    selected_crop = st.sidebar.selectbox("Select Crop", crops)
    
    # Display a message while waiting for geolocation
    #st.write("👇Please share your location for context-specific recommendations.")
    if st.checkbox("Share my location"):
        geoloc = get_geolocation()
        if geoloc is not None:
            try:
                latitude = geoloc['coords']['latitude']
                longitude = geoloc['coords']['longitude']
                weather_data = find_current_weather(latitude, longitude) 
                region = geolocator.reverse(str(latitude)+","+str(longitude))
                address = region.raw['address']
                city = address.get('city', '')
                state = address.get('state', '')
                country = address.get('country', '')
                st.write("📍Region:",city,",",state,",", country)
                #set_location_button = st.button("Reset Region Manually")
                # Function to set location when the button is clicked
                #if set_location_button:
                    #selected_state = st.selectbox("Select State", states)
                    #state = selected_state
                # Display weather data here
                # Extracting relevant information from the JSON response
                weather_description = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp']
                min_temperature = weather_data['main']['temp_min']
                max_temperature = weather_data['main']['temp_max']
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                # Displaying the weather details
                st.write("## Current Weather Status")
                st.write("**Description:**", weather_description)
                st.write("**Temperature:**", temperature, "°C")
                st.write("**Humidity:**", humidity, "%")
                st.write("**Wind Speed:**", wind_speed, "m/s")
            
            except KeyError:
                st.error("Error: Unable to retrieve geolocation.")

        
            
st.caption("💬 Language set to " + lang)

#conn.update(worksheet="userlog", data=querylog)
if prompt := st.chat_input("Ask me anything!"):
    app = agroneugraph()
 
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    if lang == "English":
        final_prompt = prompt
    else:    
        tr_prompt = translate_string(lang_code, 'en', prompt)   
        final_prompt = tr_prompt

    querylog['Date']=datetime.now().date()
    querylog['Query']= final_prompt
    querylog['City']= city
    querylog['State']= state
    querylog['Country']= country
    prevlog = conn.read(worksheet="userlog", usecols=list(range(5)), ttl =5)
    newlog = pd.concat([prevlog,querylog])
    st.dataframe(querylog)
    conn.update(worksheet="userlog", data=newlog)        
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""
        final_response = ""

        for response in app.query(system_message+final_prompt):
            msg_placeholder.empty()
            full_response += response
            
            # Translate to Malayalam
        result_response = str(full_response)
        result = get_final_answer(result_response)
        if lang == "English":
            final_response = result
        else:
            tr_response = translate_string('en',lang_code, result )   
            final_response = tr_response
        
        
        msg_placeholder.markdown(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
