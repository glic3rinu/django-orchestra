(function($) {
    $(document).ready(function($) {       
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
