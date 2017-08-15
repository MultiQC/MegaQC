
$(function(){
    init_buttons();
});


function init_buttons(){
    $(".update_btn").click(function(e){
        $("#my_alert").remove()
        var data = {'csrf_token':$("#csrf_token").val()};
        e.preventDefault();
        $(this).parentsUntil('tbody').find('input').each(function(idx, el){
            if (el.type != 'button'){
                if (el.type=="checkbox"){
                    data[el.name] = $(el).prop("checked");
                }else{
                    data[el.name] = el.value;
                }
            }
        });
        $.ajax({
            url:"/api/update_users",
            type: 'post',
            data:JSON.stringify(data),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(){
                $('<div id="my_alert" class="alert alert-success">User updated successfully</div>').appendTo('form').hide().slideDown();
            },
            error: function(ret_data){
                $('<div id="my_alert" class="alert alert-danger">Error: <code>'+ret_data.responseJSON.message+'</code></div>').appendTo('form').hide().slideDown();
            }
        });
    });
    $(".delete_btn").click(function(e){
        $("#my_alert").remove()
        var my_btn = $(this);
        var data = {};
        e.preventDefault();
        $(this).parentsUntil('tbody').find('input').each(function(idx, el){
            if (el.name == 'user_id'){
                data[el.name] = el.value;
            }
        });
        $.ajax({
            url:"/api/delete_users",
            type: 'post',
            data:JSON.stringify(data),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(){
                my_btn.parentsUntil('tbody').remove();
            }
        });
    });
    $(".reset_btn").click(function(e){
        var data = {};
        e.preventDefault();
        $(this).parentsUntil('tbody').find('input').each(function(idx, el){
            if (el.name == 'user_id'){
                data[el.name] = el.value;
            }
        });
        $.ajax({
            url:"/api/reset_password",
            type: 'post',
            data:JSON.stringify(data),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(data){
                $('<div id="my_alert" class="alert alert-success">Reset password: <code>'+data.password+'</code></div>').appendTo('form').hide().slideDown();
            }
        });
    });
    $(".add_btn").click(function(e){
        $("#my_alert").remove()
        var data = {};
        e.preventDefault();
        $(this).parentsUntil('tbody').find('input').each(function(idx, el){
            if (el.type != 'button'){
                if (el.type=="checkbox"){
                    data[el.name] = $(el).prop("checked");
                }else{
                    data[el.name] = el.value;
                }
            }
        });
        $.ajax({
            url:"/api/add_user",
            type: 'post',
            data: JSON.stringify(data),
            headers: {access_token:window.token},
            dataType: 'json',
            contentType: "application/json; charset=UTF-8",
            success: function(ret_data){
                $('#add_table').find('input').each(function (idx, el){
                    if (el.type != 'button'){
                        if (el.type == "checkbox"){
                            $(el).prop("checked", false);
                        }else{
                            el.value = '';
                        }
                    }
                });
                $('#user_table tr:last').after(
                    '<tr><td><input class="form-control" type="hidden" name="id" value="'+data.user_id+'"/><input class="form-control" type="text" value="'+data.username+'" /></td><td><input class="form-control" type="text" value="'+data.email+'" /></td><td><input class="form-control" type="text" value="'+data.first_name+'" /></td><td><input class="form-control" type="text" value="'+data.last_name+'" /></td><td><input class="form-control" type="text" value="'+ret_data.api_token+'" /></td><td><input class="form-control" type="checkbox" '+(data.active ? "checked":"")+' /></td><td><input class="form-control" type="checkbox" '+(data.active ? "checked":"")+' /></td><td><input type="button" value="Update" class="btn btn-default update_btn" /></td><td><input type="button" value="Reset" class="btn btn-default reset_btn" /></td><td><input type="button" value="Delete" class="btn btn-danger delete_btn" /></td></tr>'
                );
                $('<div id="my_alert" class="alert alert-success">New password: <code>'+ret_data.password+'</code></div>').appendTo('form').hide().slideDown();
                init_buttons();
            }
        });
    });
}
