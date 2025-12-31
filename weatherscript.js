const apiKey = "347a48fc38b6ed9b71878f03df1cac35";
const apiUrl = "https://api.openweathermap.org/data/2.5/weather?units=metric&q=";

const searchBox = document.querySelector(".search input");
const searchBtn = document.querySelector(".search img");
const weatherIcon = document.querySelector(".weather img");
const card = document.querySelector(".card");

async function checkWeather(city) {
    if (city.trim() === "") {
        alert("Please enter a city name!");
        return;
    }

    try {
        const response = await fetch(apiUrl + city + `&appid=${apiKey}`);

        if (!response.ok) {
            document.querySelector(".card h5").style.display = "block";
            document.querySelector(".weather").style.display = "none";
            document.querySelector(".bottom").style.display = "none";
            return;
        }

        const data = await response.json();

        document.querySelector(".card h5").style.display = "none";
        document.querySelector(".weather").style.display = "block";
        document.querySelector(".bottom").style.display = "flex";

        document.querySelector(".city").innerHTML = data.name;
        document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + "°C";
        document.querySelector(".humidity").innerHTML = data.main.humidity + "%";
        document.querySelector(".wind").innerHTML = data.wind.speed + " Km/h";

        const condition = data.weather[0].main;
        setWeatherUI(condition);

    } catch (error) {
        alert("Something went wrong. Please try again!");
    }
}

function setWeatherUI(condition) {
    switch (condition) {
        case "Clear":
            weatherIcon.src = "clear.png";
            card.style.background = "linear-gradient(135deg, #fbc531, #f5a623)";
            break;

        case "Clouds":
            weatherIcon.src = "clouds.png";
            card.style.background = "linear-gradient(135deg, #7f8fa6, #353b48)";
            break;

        case "Rain":
            weatherIcon.src = "rain.png";
            card.style.background = "linear-gradient(135deg, #4b79a1, #283e51)";
            break;

        case "Drizzle":
            weatherIcon.src = "drizzle.png";
            card.style.background = "linear-gradient(135deg, #74b9ff, #0984e3)";
            break;

        case "Thunderstorm":
            weatherIcon.src = "thunder.png";
            card.style.background = "linear-gradient(135deg, #2c3e50, #000000)";
            break;

        case "Snow":
            weatherIcon.src = "snow.png";
            card.style.background = "linear-gradient(135deg, #dfe6e9, #b2bec3)";
            break;

        case "Mist":
        case "Fog":
        case "Haze":
        case "Smoke":
            weatherIcon.src = "mist.png";
            card.style.background = "linear-gradient(135deg, #636e72, #2d3436)";
            break;

        default:
            weatherIcon.src = "clear.png";
            card.style.background = "linear-gradient(135deg, #02faf6, #0054fc)";
    }
}

// Click search
searchBtn.addEventListener("click", () => {
    checkWeather(searchBox.value);
});

// Enter key search
searchBox.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        checkWeather(searchBox.value);
    }
});

