

MessageEntryView = Backbone.View.extend(
    {
	tagName : "div",
	className : "message_entry",

        initialize : function() {
            _.bindAll(this, "key_down", "message", "clear");
	    this.textarea = this.$("textarea");
	    this.textarea.keydown(this.key_down);
	},
	
	key_down : function(event) {
	    console.log(event);
	    var kc = event.keyCode;
	    var message = null;
	    switch(kc) {
	    case 13:
		// return-shift is a normal return
		if(event.shiftKey) {
		    break;
		}
		message = this.message();
		this.clear();
		this.trigger("send_message", message);
		// no newline added to the area
		event.preventDefault();
		break;
	    }
	},
	
	message: function() {
	    return this.textarea.val();
	},

	clear : function() {
	    this.textarea.val("");
	}
    }
);
