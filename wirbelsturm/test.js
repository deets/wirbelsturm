$(function() {
      var container = $('#test_widget');
      var list = $("<ul/>"); 
      container.append(list);
      function schedule() {
          $.getJSON("/dispatch").success(
              function(data) {
                  var el = $("<li/>");
		  list.append(el);
                  el.text(data.test);
		  window.setTimeout(schedule, 500);
              }
          ).error(
	      function()
	      {
                  var el = $("<li/>");
                  el.text("error");
		  list.append(el);
		  window.setTimeout(schedule, 500);
	      }
	  );
      }
      schedule();
  });
