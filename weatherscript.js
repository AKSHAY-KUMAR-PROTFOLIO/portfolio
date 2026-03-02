const apiKey = "347a48fc38b6ed9b71878f03df1cac35";
const apiUrl = "https://api.openweathermap.org/data/2.5/weather?units=metric&q=";

const searchBox = document.querySelector("#search-box");
const searchBtn = document.querySelector("#search-btn");
const weatherIcon = document.querySelector(".weather-icon");
const card = document.querySelector(".card");
const sky = document.querySelector(".sky");
const cityEl = document.querySelector(".city");
const tempEl = document.querySelector(".temp");
const descEl = document.querySelector(".description");
const humidityEl = document.querySelector(".humidity");
const windEl = document.querySelector(".wind");
const feelsEl = document.querySelector(".feels-like");

async function checkWeather(city) {
    if (!city.trim()) return alert("Enter a city!");

    try {
        const res = await fetch(`${apiUrl}${city}&appid=${apiKey}`);
        const data = await res.json();

        if (res.status !== 200) return alert(data.message);

        const weather = data.weather[0].main;
        const description = data.weather[0].description;
        const temp = Math.round(data.main.temp);
        const humidity = data.main.humidity;
        const wind = data.wind.speed;
        const feels = Math.round(data.main.feels_like);

        const currentTime = data.dt;
        const sunrise = data.sys.sunrise;
        const sunset = data.sys.sunset;
        const isDay = currentTime >= sunrise && currentTime < sunset;

        // Update UI
        cityEl.textContent = data.name;
        tempEl.textContent = `${temp}°C`;
        descEl.textContent = description;
        humidityEl.textContent = `${humidity}%`;
        windEl.textContent = `${wind} km/h`;
        feelsEl.textContent = `${feels}°C`;

        setWeatherIcon(weather);
        setWeatherBackground(weather, isDay);

    } catch(err) {
        console.error(err);
        alert("Error fetching weather!");
    }
}

function setWeatherIcon(weather) {
    switch(weather){
        case "Clear": weatherIcon.src="images/clear.png"; break;
        case "Clouds": weatherIcon.src="images/clouds.png"; break;
        case "Rain": weatherIcon.src="images/rain.png"; break;
        case "Drizzle": weatherIcon.src="images/drizzle.png"; break;
        case "Thunderstorm": weatherIcon.src="images/thunder.png"; break;
        case "Snow": weatherIcon.src="images/snow.png"; break;
        case "Mist": case "Fog": case "Haze": case "Smoke": weatherIcon.src="images/mist.png"; break;
        default: weatherIcon.src="images/clear.png";
    }
}

function setWeatherBackground(weather, isDay){
    // Reset classes
    sky.className = "sky";

    if (weather==="Rain"||weather==="Drizzle") sky.classList.add("rainy");
    else if(weather==="Snow") sky.classList.add("snowy");
    else if(weather==="Thunderstorm") sky.classList.add("thunder");
    else if(weather==="Clouds") sky.classList.add(isDay ? "cloudy-day":"cloudy-night");
    else if(weather==="Clear") sky.classList.add(isDay ? "sunny":"night");
    else sky.classList.add(isDay ? "sunny":"night");
}

searchBtn.addEventListener("click", ()=>checkWeather(searchBox.value));
searchBox.addEventListener("keypress", (e)=>{ if(e.key==="Enter") checkWeather(searchBox.value); });