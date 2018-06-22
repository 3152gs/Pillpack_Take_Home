$(window).on('load', function() {
	$(function() {        
            $('#toggle > span').click(function() {
	    		var ix = $(this).index();
	    		$('#content1').toggle( ix === 0 );
	    		$('#content2').toggle( ix === 1 );
			}); 
        });
 // code here
});