$(function(){
    // Turn on the zero clipboard copy buttons
    new Clipboard('.btn-copy');

    // Turn on the bootstrap tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Focus the save-plot-modal title field when shown
    $('#save_plot_favourite_modal').on('shown.bs.modal', function (e) {
        $('#plot_favourite_title').focus();
    });
});


// Save a favourite plot - triggered when submitting
// the "Save Favourite" modal form
function save_plot_favourite(plot_type, request_data){

    // Check that we have a title
    if(!$('#plot_favourite_title').val().trim()){
        $('#plot_favourite_title_feedback').show();
        $('#plot_favourite_title').addClass('is-invalid');
        return;
    }

    // Send the plot details to save
    window.ajax_update = $.ajax({
        url: '/api/save_plot_favourite',
        type: 'post',
        data: JSON.stringify({
            'type': plot_type,
            'request_data': request_data,
            'title': $('#plot_favourite_title').val(),
            'description': $('#plot_favourite_description').val()
        }),
        headers : { access_token:window.token },
        dataType: 'json',
        contentType: 'application/json; charset=UTF-8',
        success: function(data){
            if (data['success']){
                $('#save_plot_favourite_modal').modal('hide');
                $('#plot_favourite_title').val('');
                $('#plot_favourite_description').val('');
                toastr.success(
                    'Plot favourite saved!<br>Click to view all plot favourites.',
                    null,
                    { onclick: function() { window.location.href = "/plot_favourites/"; } }
                );
            }
            // AJAX data['success'] was false
            else {
                console.log(data);
                $('#save_plot_favourite_modal').modal('hide');
                toastr.error('There was an error whilst saving this plot.');
            }
        },
        error: function(data){
            console.log(data);
            $('#save_plot_favourite_modal').modal('hide');
            toastr.error('There was an error saving this plot.');
        }
    });
}
