
$("#password_submit").click(function(e){
    passwords = [];
    e.preventDefault();
    $('.pw_input').each(function(idx, el){
        passwords.push(el.value);
    });
    if (passwords[0] != passwords[1]){
        alert("Passwords do not match");
    } else {
        var data={"password":passwords[0]};
        $.ajax({
            url:"/api/set_password",
            type: 'post',
            data:JSON.stringify(data),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(data){
               $('<div class="alert alert-success">New password set</div>').appendTo('form').hide().slideDown();
            }
        });
   }
});
