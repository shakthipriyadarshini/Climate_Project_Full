// =====================================
// GLOBAL CHART VARIABLE
// =====================================

let climateChart = null;

// =====================================
// CREATE TREND CHART
// =====================================

function createTrendChart(forecastData) {

    const labels = forecastData.map(day =>
        day.date
    );

    const tempData = forecastData.map(day =>
        day.temperature
    );

    const humidityData = forecastData.map(day =>
        day.humidity
    );

    const windData = forecastData.map(day =>
        day.wind
    );

    const ctx = document.getElementById("myChart");

    if (!ctx) return;

    if (climateChart) {

        climateChart.destroy();
    }

    climateChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {
                    label: "Temperature °C",

                    data: tempData,

                    borderColor: "#3cc4ff",

                    tension: 0.4
                },

                {
                    label: "Humidity %",

                    data: humidityData,

                    borderColor: "#00ff99",

                    tension: 0.4
                },

                {
                    label: "Wind Speed",

                    data: windData,

                    borderColor: "#ff9900",

                    tension: 0.4
                }

            ]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    labels: {

                        color: "white"
                    }
                }
            },

            scales: {

                x: {

                    ticks: {

                        color: "white"
                    }
                },

                y: {

                    ticks: {

                        color: "white"
                    }
                }
            }
        }
    });
}

// =====================================
// GET CURRENT WEATHER
// =====================================

// =====================================
// GET CURRENT WEATHER
// =====================================

async function getWeather() {

    const city = document.getElementById("city").value;

    localStorage.setItem(
    "selectedCity",
    city
);

    if (city === "") {

        alert("Please enter city");

        return;
    }

    try {

        const response = await fetch(
            `/predict/${city}`
        );

        const data = await response.json();

        if (data.error) {

            alert(data.error);

            return;
        }

        document.getElementById("temp").innerHTML =
            data.current_temperature + " °C";

        document.getElementById("humidity").innerHTML =
            data.humidity + "%";

        document.getElementById("wind").innerHTML =
            data.wind_speed + " km/h";

        document.getElementById("pressure").innerHTML =
            data.pressure + " mb";

        document.getElementById("weather").innerHTML =
            data.weather_condition;

        document.getElementById("cityname").innerHTML =
            data.city;

        // ==============================
        // RISK ELEMENTS
        // ==============================

        const rainRisk =
            document.getElementById("rainRisk");

        const stormRisk =
            document.getElementById("stormRisk");

        const heatRisk =
            document.getElementById("heatRisk");

        const alertText =
            document.getElementById("alertText");

        if (rainRisk)
            rainRisk.innerHTML =
            data.rainfall_risk;

        if (stormRisk)
            stormRisk.innerHTML =
            data.storm_risk;

        if (heatRisk)
            heatRisk.innerHTML =
            data.heatwave_risk;

        if (alertText)
            alertText.innerHTML =
            data.alert;

        // ==============================
        // LSTM PREDICTION VALUES
        // ==============================

        const rainValue =
            document.getElementById(
                "rainValue"
            );

        const stormValue =
            document.getElementById(
                "stormValue"
            );

        const heatValue =
            document.getElementById(
                "heatValue"
            );

        if (
            rainValue &&
            data.predicted_rainfall !== undefined
        ) {

            rainValue.innerHTML =
                data.predicted_rainfall;
        }

        if (
            stormValue &&
            data.predicted_storm !== undefined
        ) {

            stormValue.innerHTML =
                data.predicted_storm;
        }

        if (
            heatValue &&
            data.predicted_heatwave !== undefined
        ) {

            heatValue.innerHTML =
                data.predicted_heatwave;
        }

        getForecast(city);

    }

    catch (error) {

        console.log(error);

        alert("Server Error");
    }
}

// =====================================
// GET FORECAST DATA
// =====================================

async function getForecast(city) {

    try {

        const response = await fetch(
            `/forecast/${city}`
        );

        const data = await response.json();

        if (data.error) {

            alert(data.error);

            return;
        }

        const container =
            document.getElementById(
                "forecastContainer"
            );

        if (!container) return;

        container.innerHTML = "";

        data.forecast.forEach(day => {

            let icon = "☀";

            if (day.weather.includes("Rain")) {

                icon = "🌧";
            }

            else if (
                day.weather.includes("Cloud")
            ) {

                icon = "☁";
            }

            else if (
                day.weather.includes("Storm")
            ) {

                icon = "⛈";
            }

            else if (
                day.weather.includes("Clear")
            ) {

                icon = "☀";
            }

            container.innerHTML += `

            <div class="forecast-card">

                <h3>${day.date}</h3>

                <div class="forecast-icon">

                    ${icon}

                </div>

                <h2>

                    ${day.temperature} °C

                </h2>

                <p>

                    ${day.weather}

                </p>

            </div>
            `;
        });

        // =====================================
        // UPDATE GRAPH WITH REAL DATA
        // =====================================

        createTrendChart(
            data.forecast
        );

    }

    catch (error) {

        console.log(error);
    }
}

// =====================================
// LOAD RISK PAGE AUTOMATICALLY
// =====================================

window.addEventListener(
    "DOMContentLoaded",
    async () => {

        const rainRisk =
            document.getElementById("rainRisk");

        if (!rainRisk) return;

        const city =
            localStorage.getItem(
                "selectedCity"
            );

        if (!city) {

            document.getElementById(
                "alertText"
            ).innerHTML =
                "Please analyze a city first";

            return;
        }

        try {

            const response =
                await fetch(
                    `/predict/${city}`
                );

            const data =
                await response.json();

            document.getElementById(
                "rainRisk"
            ).innerHTML =
                data.rainfall_risk;

            document.getElementById(
                "stormRisk"
            ).innerHTML =
                data.storm_risk;

            document.getElementById(
                "heatRisk"
            ).innerHTML =
                data.heatwave_risk;

            document.getElementById(
                "rainValue"
            ).innerHTML =
                data.predicted_rainfall;

            document.getElementById(
                "stormValue"
            ).innerHTML =
                data.predicted_storm;

            document.getElementById(
                "heatValue"
            ).innerHTML =
                data.predicted_heatwave;

            document.getElementById(
                "alertText"
            ).innerHTML =
                data.alert;

        }

        catch(error) {

            console.log(error);
        }

    }
);

// =====================================
// AI ASSISTANT
// =====================================

function askAssistant(){

    const question = document
        .getElementById("assistantInput")
        .value
        .toLowerCase();

    const responseBox =
        document.getElementById(
            "assistantResponse"
        );

    let answer = "";

    if(question.includes("rain")){

        answer =
        "Heavy rainfall risk depends on humidity levels and current weather patterns.";

    }

    else if(question.includes("storm")){

        answer =
        "Storm risk increases when wind speed becomes very high.";

    }

    else if(question.includes("heat")){

        answer =
        "Heatwave risk is calculated from predicted future temperature.";

    }

    else if(question.includes("climate")){

        answer =
        "Climate predictions are generated using current weather conditions and forecast trends.";

    }

    else{

        answer =
        "Please ask about rainfall, storm, heatwave, weather or climate.";
    }

    responseBox.innerHTML = answer;
}

async function getCurrentLocation() {

    if (!navigator.geolocation) {

        alert("Geolocation not supported");

        return;
    }

    navigator.geolocation.getCurrentPosition(

        async(position) => {

            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            try {

                const response = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
                );

                const data = await response.json();

                let city =

                    data.address.city ||
                    data.address.town ||
                    data.address.village;

                document.getElementById("city").value =
                city;

            }

            catch(error){

                console.log(error);
            }
        },

        () => {

            alert(
                "Unable to fetch location"
            );
        }
    );
}

function getLocation() {

    if (!navigator.geolocation) {
        alert("Geolocation not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(position) {
            console.log(position.coords.latitude);
            console.log(position.coords.longitude);
        }
    );
}