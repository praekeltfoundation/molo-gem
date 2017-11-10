(function($) {
    console.log("modeladmin/index.js");

    $(function() {
        var userCheckboxes = $('input:checkbox.user');
        userCheckboxes.each( function(i, element) {
            var $element = $(element);
            var id = $element.attr('name');
            var target = $('.field-id').filter( function () {
                return $(this).text().startsWith(id + '\n');
            });
            var cloned = $element.clone();
            target.prepend(cloned);
            cloned.change(function () {
                $element.prop('checked', cloned.is(':checked'));
            });
        });
        userCheckboxes.hide();
    });
})(jQuery);
