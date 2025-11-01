const longUrlInput = document.getElementById('long_url');
const shortUrlInput = document.getElementById('short_url');
const infoBlockP = document.getElementById('info_p');

function postUrl() {
    var longUrl = longUrlInput.value;
    fetch("/shorten", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            url: longUrl,
        }),
    })
        .then(async (response) => {
            if (response.status === 201) {
                const data = await response.json();
                infoBlockP.textContent = 'Успешно создана.';
                infoBlockP.style.color = 'green';
                shortUrlInput.value = `http://127.0.0.1:8000/shorten/${data.shortCode}`;
            } else if (response.status === 400) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 400: Длинная ссылка должна иметь полный путь.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 400:", error);
            } else {
                console.error("Неожиданный ответ:", response.status);
                const data = await response.json()
                infoBlockP.textContent = "Неожиданный ответ: " + data;
                infoBlockP.style.color = 'red';
            }
        })
        .catch((error) => {
            console.error("Ошибка сети:", error);
            infoBlockP.textContent = "Ошибка сети.";
            infoBlockP.style.color = 'red';
        });

}

function getUrl() {
    var shortUrl = shortUrlInput.value;

    fetch(shortUrl).then(
        async (response) => {
            if (response.status === 200) {
                const data = await response.json();
                if (data?.url) {
                    window.location.assign(data.url);
                }
            } else if (response.status === 404) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 404: Данная короткая ссылка не найдена.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 404:", error);
            } else {
                console.error("Неожиданный ответ:", response.status);
                const data = await response.json()
                infoBlockP.textContent = "Неожиданный ответ: " + data;
                infoBlockP.style.color = 'red';
            }
        }
    ).catch((error) => {
        console.error("Ошибка сети:", error);
        infoBlockP.textContent = "Ошибка сети.";
        infoBlockP.style.color = 'red';
    });
}

function getUrlWithTimeout() {
    infoBlockP.textContent = "Please, wait a second. We will redirect you to origin link.";
    // Запускаем таймер
    setTimeout(() => {
        getUrl();
    }, 2000);
}

function putUrl() {
    var longUrl = longUrlInput.value;
    var shortUrl = shortUrlInput.value;
    fetch(shortUrl, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            url: longUrl,
        }),
    })
        .then(async (response) => {
            if (response.status === 200) {
                const data = await response.json();
                infoBlockP.textContent = 'Успешно изменено.';
                infoBlockP.style.color = 'green';
                console.log(data);
            } else if (response.status === 400) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 400: Длинная ссылка должна иметь полный путь.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 400:", error);
            } else if (response.status === 404) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 404: Данная короткая ссылка не найдена.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 404:", error);
            } else {
                console.error("Неожиданный ответ:", response.status);
                const data = await response.json()
                infoBlockP.textContent = "Неожиданный ответ: " + data;
                infoBlockP.style.color = 'red';
            }
        })
        .catch((error) => {
            console.error("Ошибка сети:", error);
            infoBlockP.textContent = "Ошибка сети.";
            infoBlockP.style.color = 'red';
        });
}

function delUrl() {
    var shortUrl = shortUrlInput.value;
    fetch(shortUrl, {
        method: "DELETE"
    })
        .then(async (response) => {
            if (response.status === 204) {
                infoBlockP.textContent = 'Успешно удалено.';
                infoBlockP.style.color = 'green';
            } else if (response.status === 404) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 404: Данная короткая ссылка не найдена.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 404:", error);
            } else {
                console.error("Неожиданный ответ:", response.status);
                const data = await response.json()
                infoBlockP.textContent = "Неожиданный ответ: " + data;
                infoBlockP.style.color = 'red';
            }
        })
        .catch((error) => {
            console.error("Ошибка сети:", error);
            infoBlockP.textContent = "Ошибка сети.";
            infoBlockP.style.color = 'red';
        });
}

function getUrlStats() {
    var shortUrl = shortUrlInput.value;

    fetch(`${shortUrl}/stats`).then(
        async (response) => {
            if (response.status === 200) {
                const data = await response.json();
                infoBlockP.textContent = `${data.accessCount}`;
                infoBlockP.style.color = 'green';
                console.log(data);
            } else if (response.status === 404) {
                const error = await response.json();
                infoBlockP.textContent = 'Ошибка 404: Данная короткая ссылка не найдена.';
                infoBlockP.style.color = 'red';
                console.error("Ошибка 404:", error);
            } else {
                console.error("Неожиданный ответ:", response.status);
                const data = await response.json()
                infoBlockP.textContent = "Неожиданный ответ: " + data;
                infoBlockP.style.color = 'red';
            }
        }
    ).catch((error) => {
        console.error("Ошибка сети:", error);
        infoBlockP.textContent = "Ошибка сети.";
        infoBlockP.style.color = 'red';
    });
}