//
// MegaQC: filter_samples.js
// ---------------------------
// Used by pages loading the Filter Samples modal dialogue
// to create new sample filter sets.

// To be set in the page using Python vars:
//   window.token
//   window.report_fields
//   window.sample_fields
//   window.num_matching_samples

window.data_cmp = {
    "in": "Contains string",
    "not in": "Does not contain string",
    "eq": "(=) Equal to",
    "ne": "(!=) Not equal to",
    "le": "(&le;) Less than or equal to",
    "lt": "(&lt;) Less than",
    "ge": "(&ge;) Greater than or equal to",
    "gt": "(&gt;) Greater than"
};
window.active_filters = [];
window.filter_error = false;
window.ajax_update = false;
$(function(){

    // Add new filter - Type dropdown
    $('body').on('change', '.new-filter-type select', function(e){
        // Reset downstream selectors
        var button_e = $(this).closest('tr').find('.new-filter-add');
        var key_e = $(this).closest('tr').find('.new-filter-key');
        var cmp_e = $(this).closest('tr').find('.new-filter-cmp');
        var val_e = $(this).closest('tr').find('.new-filter-value');
        button_e.prop('disabled', false);
        key_e.html('<select class="form-control"></select>');
        cmp_e.html('<select class="form-control"></select>');
        val_e.html('<input class="form-control" type="text">');
        switch($(this).val()) {
            case 'timedelta':
                key_e.html('<input type="text" readonly class="form-control-plaintext" value="Dynamic dates">');
                cmp_e.find('select').html('<option value="le">Within dates</option><option value="gt">Except dates</option>');
                val_e.find('input').attr('placeholder', 'Number of days');
                break;
            case 'daterange':
                key_e.html('<input type="text" readonly class="form-control-plaintext" value="Specific dates">');
                cmp_e.find('select').html('<option value="le">Within dates</option><option value="gt">Except dates</option>');
                val_e.html('<input class="form-control" type="date"> <input class="form-control" type="date">')
                break;
            case 'reportmeta':
                $.each(window.report_fields, function(idx, field){
                    key_e.find('select').append('<option value="'+field+'">'+field+'</option>');
                });
                $.each(window.data_cmp, function(val, txt){
                    cmp_e.find('select').append('<option value="'+val+'">'+txt+'</option>');
                });
                break;
            case 'samplemeta':
                $.each(window.sample_fields, function(idx, field){
                    key_e.find('select').append('<option value="'+field['key']+'">'+field['nicename']+'</option>');
                });
                $.each(window.data_cmp, function(val, txt){
                    cmp_e.find('select').append('<option value="'+val+'">'+txt+'</option>');
                });
                break;
            default:
                button_e.prop('disabled', true);
                key_e.find('select').prop('disabled', true).html('<option value="">[ please select a filter type ]<option>');
                cmp_e.find('select').prop('disabled', true).html('<option value="">[ please select a filter type ]<option>');
                val_e.find('input').prop('disabled', true).attr('placeholder', '[ please select a filter type ]');
                break;
        }
    });

    // Add new filter ROW
    $('body').on('click', '.new-filter-add', function(e){
        add_filter_row($(this));
    });
    // Pressing enter on a value input
    $('body').on('keyup', '.new-filter-value input', function (e) {
        if (e.keyCode == 13) {
            add_filter_row($(this));
        }
    });
    function add_filter_row(el){
        var ftype_val = el.closest('tr').find('.new-filter-type select').val();
        var fkey_val = el.closest('tr').find('.new-filter-key select').val();
        var fcmp_val = el.closest('tr').find('.new-filter-cmp select').val();
        var fvalue_val = el.closest('tr').find('.new-filter-value input').val();
        var ftype_txt = el.closest('tr').find('.new-filter-type option:selected').text();
        var fkey_txt = el.closest('tr').find('.new-filter-key option:selected').text();
        var fcmp_txt = el.closest('tr').find('.new-filter-cmp option:selected').text();
        if(fkey_val == undefined){
            fkey_val = fkey_txt = el.closest('tr').find('.new-filter-key input').val();
        }
        new_filter_row = $('<tr>' +
            '<td><div class="new-filter-type" data-value="'+ftype_val+'">'+ftype_txt+'</div></td>' +
            '<td><div class="new-filter-key" data-value="'+fkey_val+'">'+fkey_txt+'</div></td>' +
            '<td><div class="new-filter-cmp" data-value="'+fcmp_val+'">'+fcmp_txt+'</div></td>' +
            '<td><div class="new-filter-value" data-value="'+fvalue_val+'"><code>'+fvalue_val+'</code></div></td>' +
            '<td><div>' +
                '<button class="new-filter-edit btn btn-sm btn-outline-info">' +
                    '<i class="fa fa-pencil" aria-hidden="true"></i>' +
                '</button> ' +
                '<button class="new-filter-delete btn btn-sm btn-outline-danger">' +
                    '<i class="fa fa-trash" aria-hidden="true"></i>' +
                '</button>' +
            '</div></td>' +
        '</tr>');
        // Animate table row slidedown - https://stackoverflow.com/a/3410943/713980
        new_filter_row.appendTo( el.closest('table').find('tbody') )
            .find('td div').hide().slideDown();
        // Reset new filter row
        el.closest('tr').find('.new-filter-type select').val('');
        el.closest('tr').find('.new-filter-key').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        el.closest('tr').find('.new-filter-cmp').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        el.closest('tr').find('.new-filter-value').html('<input disabled class="form-control" type="text" placeholder="[ please select a filter type ]">');
        el.closest('tr').find('.new-filter-add').prop('disabled', true);
        // Update matched samples count
        update_filters();
    }

    // Delete new filter ROW
    $('body').on('click', '.new-filter-delete', function(e){
        $(this).closest('tr').find('td div').slideUp(function(){
            $(this).closest('tr').remove();
        });
    });

    // Add new filter GROUP button
    $('body').on('click', '.new-filter-group-add-btn', function(e){
        new_group_card = $('.new-filter-group-card').first().clone();
        var new_idx = $('.new-filter-group-card').length + 1;
        new_group_card.find('.card-header').html(
            '<button class="new-filter-group-delete btn btn-sm btn-outline-secondary float-right">Delete</button>' +
            'Filter Group '+new_idx);
        new_group_card.find('tbody').html('');
        new_group_card.find('.new-filter-add').prop('disabled', true);
        new_group_card.find('.new-filter-key').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        new_group_card.find('.new-filter-cmp').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        new_group_card.find('.new-filter-value').html('<input disabled class="form-control" type="text" placeholder="[ please select a filter type ]">');
        new_group_card.hide().insertBefore($(this)).slideDown();
    });

    // Delete new filter GROUP
    $('body').on('click', '.new-filter-group-delete', function(e){
        $(this).closest('.new-filter-group-card').slideUp(function(){
            $(this).remove();
        });
    });

    // Update filters
    function update_filters(){
        $('.loading-spinner').show();
        // Cancel any running update_filters ajax call
        if(window.ajax_update !== false){
            window.ajax_update.abort();
        }
        // Build active_filters object from tables
        window.active_filters = [];
        $('.filter-group-table').each(function(){
            var t_filters = [];
            $(this).find('tbody tr').each(function(){
                var filter = {
                    'type': $(this).find('.new-filter-type').data('value'),
                    'key': $(this).find('.new-filter-key').data('value'),
                    'cmp': $(this).find('.new-filter-cmp').data('value'),
                    'value': $(this).find('.new-filter-value').data('value')
                };
                var fsection = $(this).find('.new-filter-key').data('section');
                if( fsection !== undefined ){
                    filter['section'] = fsection;
                }
                t_filters.push(filter);
            });
            window.active_filters.push(t_filters);
        });
        // Call the AJAX endpoint to update the page
        // Update the page when a new filter is added
        var meta={name:$('#filters_name').val(), set:$('#filters_name').val(), is_public:($('#filters_visibility').val() == 'Everyone')};
        window.ajax_update = $.ajax({
            url: '/api/report_filter_fields',
            type: 'post',
            data:JSON.stringify( {'filters': window.active_filters, meta:meta} ),
            headers : { access_token:window.token },
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function(data){
                if (data['success']){

                    // Update the Javascript variables
                    window.num_matching_samples = data['num_samples'];
                    window.filter_error = false;

                    // Update number of matching samples
                    $('.num_filtered_samples').text(data['num_samples']+' samples');
                    $('.num_filtered_samples').removeClass('badge-danger badge-success badge-warning');
                    if(parseInt(data['num_samples']) == 0){
                        $('.num_filtered_samples').addClass('badge-danger');
                    } else if(parseInt(data['num_samples']) > 100){
                        $('.num_filtered_samples').addClass('badge-warning');
                    } else {
                        $('.num_filtered_samples').addClass('badge-success');
                    }

                    // Update the report plot type dropdown
                    if(data['report_plot_types'].length > 0){
                        $('#selectPlotType').html('<option value="">[ select plot type ]</option>').attr('disabled', false);
                        $.each(data['report_plot_types'], function(idx, field){
                            $('#selectPlotType').append('<option value="'+field['name']+'">'+field['nicename']+' ('+field['type']+')</option>')
                        });
                    } else {
                        $('#selectPlotType').html('<option value="">[ no available fields ]</option>').attr('disabled', true);
                    }

                    // Hide the loading spinner
                    $('.loading-spinner').hide();

                // AJAX data['success'] was false
                } else {
                    console.log(data);
                    toastr.error('There was an error applying the sample filters.');
                    $('.num_filtered_samples').text('Error applying filters').removeClass('badge-success badge-warning').addClass('badge-danger');
                    $('.loading-spinner').hide();
                    window.num_matching_samples = 0;
                    window.filter_error = true;
                }
            },
            error: function(data){
                toastr.error('There was an error applying the sample filters.');
                $('.num_filtered_samples').text('Error applying filters').removeClass('badge-success badge-warning').addClass('badge-danger');
                $('.loading-spinner').hide();
                window.num_matching_samples = 0;
                window.filter_error = true;
            }
        });
    }

    // Submit form to make a plot
    $('#createReportPlotForm').submit(function(e){
        // Check that there wasn't an error with the filters
        if(window.filter_error){
            toastr.error('There was an error applying your filters. Cannot make a plot.');
            e.preventDefault();
            return false;
        }
        // Check that some samples match the filters
        if(window.num_matching_samples == 0){
            toastr.error('Some samples must match your filters to make a plot.');
            e.preventDefault();
            return false;
        }
        // Check that a plot type has been selected
        if($('#selectPlotType').val() == ''){
            toastr.error('Please select a plot type.');
            e.preventDefault();
        }
    });
});
