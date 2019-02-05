period = {}

function set_period() {
    period['start'] = document.getElementById('start_date').value
    period['end'] = document.getElementById('end_date').value
}


function set_period_and_update() {
    set_period()
    update_transaction_list()
}


function update_transaction_list() {
    disable_all_buttons();
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/transaction/update', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        var transactions = JSON.parse(this.responseText);
        var transaction_table = document.getElementById('transaction_table').getElementsByTagName('tbody')[0];
        var empty_table = document.createElement('tbody');
        transaction_table.parentNode.replaceChild(empty_table, transaction_table);
        for (var i in transactions) {
            add_row(transactions[i]);
        };
        enable_all_buttons();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var period_json = JSON.stringify(period)
    xhr.send(period_json);
}


function add_row(transaction) {
    var transaction_table = document.getElementById('transaction_table').getElementsByTagName('tbody')[0];
    row_num = transaction_table.rows.length;
    var new_row = transaction_table.insertRow(row_num);
    var html_row_num = row_num + 1;

    cell_num = new_row.insertCell(-1);
    cell_num.className = 'align-middle';
    span_num = document.createElement("span");
    span_num.id = "number" + html_row_num;
    span_num.innerText = html_row_num;
    cell_num.appendChild(span_num);

    // date
    cell_date = new_row.insertCell(-1);
    cell_date.className = 'align-middle';
    span_date = document.createElement("span");
    span_date.id = "date" + html_row_num;
    span_date.innerText = transaction['date'];
    cell_date.appendChild(span_date);

    //category
    cell_caption = new_row.insertCell(-1);
    cell_caption.className = 'align-middle';
    span_caption = document.createElement("span");
    span_caption.id = "category" + html_row_num;
    span_caption.innerText = transaction['category'];
    cell_caption.appendChild(span_caption);

    //account
    cell_account = new_row.insertCell(-1);
    cell_account.className = 'align-middle';
    span_account = document.createElement("span");
    span_account.id = "account" + html_row_num;
    span_account.innerText = transaction['account'];
    cell_account.appendChild(span_account);

    //amount
    cell_amount = new_row.insertCell(-1);
    cell_amount.className = 'align-middle';
    cell_amount.style = 'text-align: right';
    span_amount = document.createElement("span");
    span_amount.id = "amount" + html_row_num;
    span_amount.innerText = transaction['amount'];
    cell_amount.appendChild(span_amount);

    //currency
    cell_currency = new_row.insertCell(-1);
    cell_currency.className = 'align-middle';
    span_currency = document.createElement("span");
    span_currency.id = "currency" + html_row_num;
    span_currency.innerText = transaction['currency'];
    cell_currency.appendChild(span_currency);

    //left button
    cell_left_btn = new_row.insertCell(-1);
    cell_left_btn.className = 'align-middle text-center';
    left_btn = document.createElement('button');
    left_btn.className = 'btn btn-secondary';
    left_btn.type = 'button';
    left_btn.id = 'left_btn' + html_row_num;
    left_btn.innerText = 'Изменить';
    left_btn.onclick = '';
    cell_left_btn.appendChild(left_btn);
    left_btn.disabled = true

    //right button
    cell_right_btn = new_row.insertCell(-1);
    cell_right_btn.className = 'align-middle text-center';
    right_btn = document.createElement('button');
    right_btn.className = 'btn btn-secondary';
    right_btn.type = 'button';
    right_btn.id = 'right_btn' + html_row_num;
    right_btn.innerText = 'Удалить';
    right_btn.onclick = delete_transaction;
    cell_right_btn.appendChild(right_btn);
};


function delete_transaction() {
    var num = this.id.slice(9);
    transaction = {}
    transaction['date'] = document.getElementById('transaction_table').getElementsByTagName('tbody')[0].rows[num-1].cells[1].innerText;
    transaction['category'] = document.getElementById('transaction_table').getElementsByTagName('tbody')[0].rows[num-1].cells[2].innerText;
    transaction['account'] = document.getElementById('transaction_table').getElementsByTagName('tbody')[0].rows[num-1].cells[3].innerText;
    transaction['amount'] = document.getElementById('transaction_table').getElementsByTagName('tbody')[0].rows[num-1].cells[4].innerText;
    transaction['currency'] = document.getElementById('transaction_table').getElementsByTagName('tbody')[0].rows[num-1].cells[5].innerText;
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/transaction/delete_transaction', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        document.getElementById('transaction_table').getElementsByTagName('tbody')[0].deleteRow(num-1);
        if (this.responseText === "success") {
            alert("Запись успешно удалена")
        } else {
            alert("Не удалось удалить запись")
        }
        update_transaction_list();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var transaction_to_delete = JSON.stringify(transaction);
    xhr.send(transaction_to_delete);
};


function disable_all_buttons() {
    return 0
}


function enable_all_buttons() {
    return 0
}