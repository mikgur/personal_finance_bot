function request_otp() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/user/request-otp', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function () {
        if (this.responseText == "Success") {
            alert('Код отправлен!');
            return;
        }
        if (this.responseText == "Wrong_telegram_id") {
            alert('Введен неправильный telegram_id. Перед регистрацией на сайте нужно начать диалог с ботом в телеграме, написав ему команду /start');
            return;
        }
    };
    xhr.onerror = function () {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var telegram_id_value = document.forms["registration_form"]["telegram_id"].value;
    if (telegram_id_value == "") {
        alert("Введите свой telegram_id в поле формы")
        return
    }
    var telegram_id = JSON.stringify(telegram_id_value);
    xhr.send(telegram_id);
}