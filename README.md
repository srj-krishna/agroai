# Welcome to streamlit

This is the app you get when you run `streamlit hello`, extracted as its own app.

Edit [Hello.py](./Hello.py) to customize this app to your heart's desire. ❤️

Check it out on [Streamlit Community Cloud](https://st-hello-app.streamlit.app/)



"""
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
                #st.write("📍Region:",city,",",state,",", country)
                st.write("📍Region:",state)
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

        """
