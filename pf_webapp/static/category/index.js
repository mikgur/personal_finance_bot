var old_captions = {}

function save_new_category() {
    var num = this.id.slice(8);
    var text_input = document.getElementById('input' + num);
    caption = text_input.value;
    if (caption == '') {
        // Пустую строку нельзя сохранить
        alert("Вы пытаетесь сохранить категорию без название, так нельзя");
        return;
    };
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/category/add_new_category', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        if (this.responseText == "already_exist") {
            alert('Категория с таким именем уже существует');
            return;
        }
        update_categories();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var new_category = JSON.stringify(caption);
    xhr.send(new_category);
};


function add_new_row() {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    row_num = category_table.rows.length;
    var new_row = category_table.insertRow(row_num);
    var html_row_num = row_num + 1;
    new_row.innerHTML = '<td class = "align-middle">\
                                <span id="number' + html_row_num + '">' + html_row_num + '</span></td>\
                         <td class = "align-middle">\
                                <input type = "text" style = "width: 100%" id = "input' + html_row_num + '"></td>\
                         <td class = "align-middle text-center">\
                                <button type="button" class="btn btn-secondary" id="left_btn' + html_row_num + '" onclick="save_new_category.call(this)">Сохранить</button>\
                         </td>\
                         <td class = "align-middle text-center">\
                                <button type="button" class="btn btn-secondary" id="right_btn' + html_row_num + '" onclick="delete_category.call(this)">Отмена</button>\
                         </td>';
    disable_all_buttons(html_row_num);
};


function add_row(caption) {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    row_num = category_table.rows.length;
    var new_row = category_table.insertRow(row_num);
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

    cell_left_btn = new_row.insertCell(-1);
    cell_left_btn.className = 'align-middle text-center';
    left_btn = document.createElement('button');
    left_btn.className = 'btn btn-secondary';
    left_btn.type = 'button';
    left_btn.id = 'left_btn' + html_row_num;
    left_btn.innerText = 'Изменить';
    left_btn.onclick = rename_category;
    cell_left_btn.appendChild(left_btn);

    cell_right_btn = new_row.insertCell(-1);
    cell_right_btn.className = 'align-middle text-center';
    right_btn = document.createElement('button');
    right_btn.className = 'btn btn-secondary';
    right_btn.type = 'button';
    right_btn.id = 'right_btn' + html_row_num;
    right_btn.innerText = 'Удалить';
    right_btn.onclick = delete_category;
    cell_right_btn.appendChild(right_btn);
};


function cancel_category_change() {
    var num = this.id.slice(9);
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var text_input = document.getElementById('input' + num);
    var caption = document.createElement("span");
    caption.id = "caption" + num;
    caption.innerHTML = old_captions[num];
    text_input.parentNode.replaceChild(caption, text_input);
    btnLeft.onclick = rename_category;
    btnLeft.innerHTML = "Изменить";
    btnRight.onclick = delete_category;
    btnRight.innerHTML = "Удалить";
    enable_all_buttons();
};


function rename_category() {
    var num = this.id.slice(8)
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var caption = document.getElementById("caption" + num);
    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.id = "input" + num;
    text_input.style = "width: 100%";
    text_input.value = caption.innerHTML;
    old_captions[num] = caption.innerHTML;
    caption.parentNode.replaceChild(text_input, caption);
    btnLeft.onclick = save_category;
    btnLeft.innerHTML = "Сохранить";
    btnRight.onclick = cancel_category_change;
    btnRight.innerHTML = "Отмена";
    disable_all_buttons(num);
};


function delete_category() {
    var num = this.id.slice(9);
    caption = document.getElementById('category_table').getElementsByTagName('tbody')[0].rows[num-1].cells[1].innerText;
    if (caption == '') {
        // Пустую строку можем удалять без разрешения сервера
        document.getElementById('category_table').getElementsByTagName('tbody')[0].deleteRow(num-1);
        enable_all_buttons();
        return;
    };
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/category/delete_category', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        document.getElementById('category_table').getElementsByTagName('tbody')[0].deleteRow(num-1);
        update_categories();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    var category_to_delete = JSON.stringify(caption);
    xhr.send(category_to_delete);
};


function disable_all_buttons(except_row) {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    rows = category_table.rows;
    for (var i = 0; i < rows.length; i++) {
        if (i+1 != except_row) {
            cells = rows[i].cells;
            cells[2].children[0].disabled = true;
            cells[3].children[0].disabled = true;
        };
    };
    add_btn = document.getElementById('add_btn');
    add_btn.disabled = true;
};


function enable_all_buttons() {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    rows = category_table.rows;
    for (var i = 0; i < rows.length; i++) {
            cells = rows[i].cells;
            cells[2].children[0].disabled = false;
            cells[3].children[0].disabled = false;
    };
    add_btn = document.getElementById('add_btn');
    add_btn.disabled = false;
};


function save_category() {
    var num = this.id.slice(8);
    var text_input = document.getElementById('input' + num);
    var new_category = text_input.value;
    if (new_category == old_captions[num]) {
        update_categories();
        return;
    };

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/category/rename_category', true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.onload = function() {
        if (this.responseText == "already_exist") {
            alert('Категория с таким именем уже существует');
            return;
        };
        update_categories();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    
    var rename_category = JSON.stringify({"old": old_captions[num], 
                                 "new": new_category})
    xhr.send(rename_category);
};


function update_categories() {
    disable_all_buttons();
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/category/update', true);
    xhr.onload = function() {
        var data = JSON.parse(this.responseText);
        var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
        rows_length = category_table.rows.length;
        var empty_table = document.createElement('tbody');
        category_table.parentNode.replaceChild(empty_table, category_table);
        for (var i in data) {
            add_row(data[i]);
        };
        enable_all_buttons();
    };
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    };
    xhr.send();
}
