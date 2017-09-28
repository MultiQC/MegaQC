
$(function(){
    init_btns();
    init_report_checkboxes();
    init_datatable();
});
function init_datatable(){

    $('#report_table').DataTable();
    $('div.dataTables_filter input').addClass('form-control search search-query');
    $('#project_table_filter').addClass('form-inline pull-right');
    $("#project_table_filter").appendTo("h1");

}
function init_report_checkboxes(){
    $(".checkbox_report").click(function(e){
        report_id = $(this).data('id');
        if( $(this).is(':checked') ){
        $.ajax({
            url:"/api/get_samples_per_report",
            type: 'post',
            data:JSON.stringify({"report_id":report_id}),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(data){
                for (key in data){
                    $("#sample_table tbody").append("<tr class='sample_row_"+report_id+"'><td>"+key+"</td><td>"+data[key]+"</td><td><input type='checkbox' class='form-control sample_chbx' data-name='"+key+"'/></td></tr>");
                }
            }
        });
        }else{
            $(".sample_row_"+report_id).remove();

        }

    });


}
function init_btns(){
    $("#make_plot_btn").click(function(e){
        selected_samples=[];
        $(".sample_chbx:checked").each(function(idx){
            selected_samples.push($(this).data('name'));
        }
        );
        $.ajax({
            url:"/api/get_report_plot",
            type: 'post',
            data:JSON.stringify({"samples":selected_samples, "plot_type":window.graph_type}),
            headers : {access_token:window.token},
            dataType: 'json',
            contentType:"application/json; charset=UTF-8",
            success: function(json){
                console.log(json);
                html=json['plot'];
                //$("#plot_modal_body").html(html);
                //$("#result_plot").modal();
                $('#plot_location').html(html);
                }
        });

    });
    $(".plot_type_choice").each(function(idx){
        $(this).click(function(e){
            e.preventDefault();
            $("#plot_type_btn").html($(this).data('type')+"<span class='caret'></span>");
            window.graph_type=$(this).data('type');
        });
    });
}
