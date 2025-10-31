const infoBlockP = document.getElementById('info_p');

function getUrl() {
    var shortgUrl = document.URL;

    fetch(shortgUrl).then(
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

// Запускаем таймер
setTimeout(() => {
    getUrl();
}, 1000);