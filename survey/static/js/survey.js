 ;

 function show_or_hide_sample_size() {
     var $sample_size = $('#id_sample_size');
     var $div_to_toggle = $sample_size.closest('div').parent('div');

     if ($('#id_has_sampling').is(':checked')) {
         $div_to_toggle.show()
     }
     else {
         $div_to_toggle.hide();
         $sample_size.val(0)
     }
 }

 jQuery(function($){
     show_or_hide_sample_size();
     $('#id_has_sampling').on('change', function(){
         show_or_hide_sample_size();
     });
 });
