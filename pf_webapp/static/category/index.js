var old_captions = {}

function change_category() {
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
    disable_all_buttons(num)
}

function save_category() {
    var num = this.id.slice(8)
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/category/savebtn', true);
    xhr.onload = function() {
        var text_input = document.getElementById('input' + num)
        var caption = document.createElement("span");
        caption.id = "caption" + num
        caption.innerHTML = text_input.value;
        text_input.parentNode.replaceChild(caption, text_input);
        btnLeft.onclick = change_category;
        btnLeft.innerHTML = "Изменить";
        btnRight.onclick = delete_category;
        btnRight.innerHTML = "Удалить";
    }
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    }
    xhr.send();
    enable_all_buttons()
}

function delete_category() {
    var num = this.id.slice(9)
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var xhr = new XMLHttpRequest();
    alert("Удаляем " + num);
    xhr.open('GET', '/category/deletebtn', true);
    xhr.onload = function() {
        document.getElementById('category_table').getElementsByTagName('tbody')[0].deleteRow(num-1)
        enable_all_buttons()
    }
    xhr.onerror = function() {
        alert('Ошибка ' + xhr.status + ': ' + xhr.statusText);
    }
    xhr.send();
}

function cancel_category_change() {
    var num = this.id.slice(9)
    var btnLeft = document.getElementById("left_btn" + num);
    var btnRight = document.getElementById("right_btn" + num);

    var text_input = document.getElementById('input' + num);
    var caption = document.createElement("span");
    caption.id = "caption" + num;
    caption.innerHTML = old_captions[num];
    text_input.parentNode.replaceChild(caption, text_input);
    btnLeft.onclick = change_category;
    btnLeft.innerHTML = "Изменить";
    btnRight.onclick = delete_category;
    btnRight.innerHTML = "Удалить";
    enable_all_buttons()
}

function add_row() {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    row_num = category_table.rows.length;
    var new_row   = category_table.insertRow(row_num);
    var html_ros_num = row_num + 1
    new_row.innerHTML = '<td class = "align-middle">\
                                <span id="number' + html_ros_num + '">' + html_ros_num + '</span></td>\
                         <td class = "align-middle">\
                                <input type = "text" style = "width: 100%" id = "input' + html_ros_num + '"></td>\
                         <td class = "align-middle text-center">\
                                <button type="button" class="btn btn-secondary" id="left_btn' + html_ros_num + '" onclick="save_category.call(this)">Сохранить</button>\
                         </td>\
                         <td class = "align-middle text-center">\
                                <button type="button" class="btn btn-secondary" id="right_btn' + html_ros_num + '" onclick="delete_category.call(this)">Отмена</button>\
                         </td>'
    disable_all_buttons(html_ros_num)
}

function disable_all_buttons(except_row) {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    rows = category_table.rows
    for (var i = 0; i < rows.length; i++) {
        if (i+1 != except_row) {
            cells = rows[i].cells
            cells[2].children[0].disabled = true
            cells[3].children[0].disabled = true
        }
    }
    add_btn = document.getElementById('add_btn')
    add_btn.disabled = true
}

function enable_all_buttons() {
    var category_table = document.getElementById('category_table').getElementsByTagName('tbody')[0];
    rows = category_table.rows
    for (var i = 0; i < rows.length; i++) {
            cells = rows[i].cells
            cells[2].children[0].disabled = false
            cells[3].children[0].disabled = false
    }
    add_btn = document.getElementById('add_btn')
    add_btn.disabled = false
}