
(function($) {
    $(document).ready(function($) {
        // visibility helper show on hover
        $v = $('#id_visibility');
        $v_help = $('#ticket_form .field-box.field-visibility .help')
        $v.hover(
            function() { $v_help.show(); }, 
            function() { $v_help.hide(); }
        );
        
        // show subject edit field on click
        $('#subject-edit').click(function() { 
            $('.field-box.field-subject').show();
        });
        
        // load markdown preview
        $('.load-preview').on("click", function() {
            var field = '#' + $(this).attr('data-field'),
                data = { 
                    'data': $(field).val(),
                    'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]', 
                        '#ticket_form').val(),
                },
                preview = field + '-preview';
            $(preview).load("/admin/issues/ticket/preview/", data);
            return false;
        });
    });
})(django.jQuery);
