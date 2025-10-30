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

                console.log("Успешно:", data);
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
function getUrl() { }
function putUrl() { }
function delUrl() { }
function getUrlStats() { }
