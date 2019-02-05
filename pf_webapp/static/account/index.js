var old_captions = {}
currency_names = []
get_currency_names()


function get_currency_names() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/account/get_currencies', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        var data = JSON.parse(this.responseText);
        currency_names = data
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    xhr.send();
}


function save_new_account() {
    // Новый счет всегда самая последяя строка
    var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
    num = account_table.rows.length;
    var text_input = document.getElementById('caption_input' + num);
    caption = text_input.value;
    if (caption == '') {
        // Пустую строку нельзя сохранить
        alert("Вы пытаетесь сохранить счет без названия, так нельзя");
        return;
    };

    var text_input = document.getElementById('balance_input' + num);
    balance = text_input.value;
    if (balance == '') {
        balance = 0
    };

    var select_input = document.getElementById('currency_input' + num);
    currency = select_input.value;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/account/add_new_account', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        if (this.responseText == "already_exist") {
            alert('Счет с таким именем уже существует');
            return;
        }
        update_accounts();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var new_account = JSON.stringify({"name": caption, 
                                 "initial_balance": balance,
                                "currency":currency})
    xhr.send(new_account);
};


function add_new_row() {
    add_row("", "", "")
    edit_account(self = false, new_account=true)
};


function add_row(caption, balance, currency) {
    var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
    row_num = account_table.rows.length;
    var new_row = account_table.insertRow(row_num);
    var html_row_num = row_num + 1;

    cell_num = new_row.insertCell(-1);
    cell_num.className = 'align-middle';
    span_num = document.createElement("span");
    span_num.id = "number" + html_row_num;
    span_num.innerText = html_row_num;
    cell_num.appendChild(span_num);

    cell_caption = new_row.insertCell(-1);
    cell_caption.className = 'align-middle';
    span_caption = document.createElement("span");
    span_caption.id = "caption" + html_row_num;
    span_caption.innerText = caption;
    cell_caption.appendChild(span_caption);

    cell_caption = new_row.insertCell(-1);
    cell_caption.className = 'align-middle';
    cell_caption.style = 'text-align: right';
    span_caption = document.createElement("span");
    span_caption.id = "balance" + html_row_num;
    span_caption.innerText = balance;
    cell_caption.appendChild(span_caption);

    cell_caption = new_row.insertCell(-1);
    cell_caption.className = 'align-middle';
    span_caption = document.createElement("span");
    span_caption.id = "currency" + html_row_num;
    span_caption.innerText = currency;
    cell_caption.appendChild(span_caption);

    cell_left_btn = new_row.insertCell(-1);
    cell_left_btn.className = 'align-middle text-center';
    left_btn = document.createElement('button');
    left_btn.className = 'btn btn-secondary';
    left_btn.type = 'button';
    left_btn.id = 'left_btn' + html_row_num;
    left_btn.innerText = 'Изменить';
    left_btn.onclick = edit_account;
    cell_left_btn.appendChild(left_btn);

    cell_right_btn = new_row.insertCell(-1);
    cell_right_btn.className = 'align-middle text-center';
    right_btn = document.createElement('button');
    right_btn.className = 'btn btn-secondary';
    right_btn.type = 'button';
    right_btn.id = 'right_btn' + html_row_num;
    right_btn.innerText = 'Удалить';
    right_btn.onclick = delete_account;
    cell_right_btn.appendChild(right_btn);
};


function cancel_account_change() {
    var num = this.id.slice(9);
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var text_input = document.getElementById('caption_input' + num);
    var caption = document.createElement("span");
    caption.id = "caption" + num;
    caption.innerHTML = old_captions[num];
    text_input.parentNode.replaceChild(caption, text_input);
    btnLeft.onclick = edit_account;
    btnLeft.innerHTML = "Изменить";
    btnRight.onclick = delete_account;
    btnRight.innerHTML = "Удалить";
    enable_all_buttons();
};


function edit_account(self=false, new_account = false) {
    if (new_account) {
        var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
        num = account_table.rows.length;
    } else {
        var num = this.id.slice(8)
    }
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var caption = document.getElementById("caption" + num);
    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.id = "caption_input" + num;
    text_input.style = "width: 100%";
    text_input.value = caption.innerHTML;
    old_captions[num] = caption.innerHTML;
    caption.parentNode.replaceChild(text_input, caption);

    btnLeft.onclick = save_account;
    btnLeft.innerHTML = "Сохранить";
    btnRight.onclick = cancel_account_change;
    btnRight.innerHTML = "Отмена";

    if (new_account) {
        btnLeft.onclick = save_new_account;
        btnRight.onclick = delete_account;

        var balance = document.getElementById("balance" + num);
        var text_input = document.createElement("input");
        text_input.type = "number";
        text_input.id = "balance_input" + num;
        text_input.style = "width: 100%; text-align: right";
        text_input.value = "0";
        balance.parentNode.replaceChild(text_input, balance);

        var currency = document.getElementById("currency" + num);
        var select_input = document.createElement("select")
        select_input.id = "currency_input" + num;
        select_input.style = "width: 100%";
        for (var i = 0; i < currency_names.length; i++) {
            var option = document.createElement("option");
            option.text = currency_names[i];
            select_input.add(option);
        };
        select_input.value = "руб";
        currency.parentNode.replaceChild(select_input, currency);
    }

    disable_all_buttons(num);
};


function delete_account() {
    var num = this.id.slice(9);
    caption = document.getElementById('account_table').getElementsByTagName('tbody')[0].rows[num-1].cells[1].innerText;
    if (caption == '') {
        // Пустую строку можем удалять без разрешения сервера
        document.getElementById('account_table').getElementsByTagName('tbody')[0].deleteRow(num-1);
        enable_all_buttons();
        return;
    };
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/account/delete_account', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        document.getElementById('account_table').getElementsByTagName('tbody')[0].deleteRow(num-1);
        update_accounts();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var account_to_delete = JSON.stringify(caption);
    xhr.send(account_to_delete);
};


function disable_all_buttons(except_row) {
    var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
    rows = account_table.rows;
    for (var i = 0; i < rows.length; i++) {
        if (i+1 != except_row) {
            cells = rows[i].cells;
            cells[4].children[0].disabled = true;
            cells[5].children[0].disabled = true;
        };
    };
    add_btn = document.getElementById('add_btn');
    add_btn.disabled = true;
};


function enable_all_buttons() {
    var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
    rows = account_table.rows;
    for (var i = 0; i < rows.length; i++) {
            cells = rows[i].cells;
            cells[4].children[0].disabled = false;
            cells[5].children[0].disabled = false;
    };
    add_btn = document.getElementById('add_btn');
    add_btn.disabled = false;
};


function save_account() {
    var num = this.id.slice(8);
    var text_input = document.getElementById('caption_input' + num);
    var new_account = text_input.value;
    if (new_account == old_captions[num]) {
        update_accounts();
        return;
    };

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/account/edit_account', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        if (this.responseText == "already_exist") {
            alert('Счет с таким именем уже существует');
            return;
        };
        update_accounts();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    
    var edit_account = JSON.stringify({"old": old_captions[num], 
                                 "new": new_account})
    xhr.send(edit_account);
};


function update_accounts() {
    disable_all_buttons();
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/account/update', true);
    xhr.onload = function() {
        var data = JSON.parse(this.responseText);
        var account_table = document.getElementById('account_table').getElementsByTagName('tbody')[0];
        rows_length = account_table.rows.length;
        var empty_table = document.createElement('tbody');
        account_table.parentNode.replaceChild(empty_table, account_table);
        for (var i in data) {
            add_row(data[i][0], data[i][1] ,data[i][2]);
        };
        enable_all_buttons();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    xhr.send();
}
