
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
                } else {
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
                toastr.success('User updated successfully');
            },
            error: function(ret_data){
                toastr.error('Error: '+ret_data.responseJSON.message);
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
                toastr.success('User deleted');
            },
            error: function(ret_data){
                toastr.error('Error: '+ret_data.responseJSON.message);
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
                toastr.success(
                    'Password updated successfully!<br>New password: <code>'+data.password+'</code>',
                    null, {
                        "closeButton": true,
                        "timeOut": 0,
                        "extendedTimeOut": 0,
                        "tapToDismiss": false
                    }
                );
            },
            error: function(ret_data){
                toastr.error('Error: '+ret_data.responseJSON.message);
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
                    '<tr>'+
                        '<td>'+
                            '<input class="form-control" type="hidden" name="user_id" value="'+data.user_id+'"/>'+
                            '<input class="form-control" type="text" name="username" value="'+data.username+'" />'+
                        '</td>'+
                        '<td><input class="form-control" type="email" name="email" value="'+data.email+'" /></td>'+
                        '<td><input class="form-control" type="text" name="first_name" value="'+data.first_name+'" /></td>'+
                        '<td><input class="form-control" type="text" name="last_name" value="'+data.last_name+'" /></td>'+
                        '<td><input class="form-control monospace" type="text" name="api_token" value="'+ret_data.api_token+'" disabled="disabled" /></td>'+
                        '<td class="align-middle"><input class="form-control" type="checkbox" name="active" '+(data.active ? 'checked="checked"':'')+' /></td>'+
                        '<td class="align-middle"><input class="form-control" type="checkbox" name="is_admin" '+(data.is_admin ? 'checked="checked"':'')+' /></td>'+
                        '<td>'+
                            '<input type="button" class="btn btn-sm btn-outline-primary update_btn" name="update_btn" value="Update"/> '+
                            '<input type="button" class="btn btn-sm btn-outline-warning reset_btn" name="reset_btn" value="Reset PW"/> '+
                            '<input type="button" class="btn btn-sm btn-outline-danger delete_btn" name="delete_btn" value="Delete"/> '+
                        '</td>'+
                    '</tr>'
                );
                toastr.success(
                    'User Added!<br>New password: <code>'+ret_data.password+'</code>',
                    null, {
                        "closeButton": true,
                        "timeOut": 0,
                        "extendedTimeOut": 0,
                        "tapToDismiss": false
                    }
                );
                init_buttons();
            },
            error: function(){
                toastr.error('Error saving new user');
            }
        });
    });
}
