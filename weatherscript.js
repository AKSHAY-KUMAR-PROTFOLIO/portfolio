const apiKey = "347a48fc38b6ed9b71878f03df1cac35";
const apiUrl = "https://api.openweathermap.org/data/2.5/weather?&units=metric&q=";

const searchBox = document.querySelector(".search input");
const searchBtn = document.querySelector(".search img");
const weatherIcon = document.querySelector(".weather img");

async function checkWeather(city) {
    if(city === '') {
        alert("Please enter a city name!");
        return;
    }

    const response = await fetch(apiUrl + city + `&appid=${apiKey}`);

    if (response.status === 404) {
        document.querySelector(".card h5").style.display = "block";
        document.querySelector(".weather").style.display = "none";
        document.querySelector(".bottom").style.display = "none";
    } else {
        document.querySelector(".card h5").style.display = "none";
        document.querySelector(".weather").style.display = "block";
        document.querySelector(".bottom").style.display = "flex";
    }

    const data = await response.json();

    document.querySelector(".city").innerHTML = data.name;
    document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + "°C";
    document.querySelector(".humidity").innerHTML = data.main.humidity + " %";
    document.querySelector(".wind").innerHTML = data.wind.speed + " Km/h";

    // Weather Icon Change based on conditions
    if (data.weather[0].main === "Clouds") {
        weatherIcon.src = "images/clouds.png";
    } else if (data.weather[0].main === "Clear") {
        weatherIcon.src = "images/clear.png";
    } else if (data.weather[0].main === "Rain") {
        weatherIcon.src = "images/rain.png";
    } else if (data.weather[0].main === "Drizzle") {
        weatherIcon.src = "images/drizzle.png";
    } else if (data.weather[0].main === "Mist") {
        weatherIcon.src = "images/mist.png";
    }
}

// Event listener for search button click
searchBtn.addEventListener("click", () => {
    checkWeather(searchBox.value);
});

// Optional: Allow 'Enter' key press to trigger search
searchBox.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        checkWeather(searchBox.value);
    }
});
