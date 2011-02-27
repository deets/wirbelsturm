

MessageEntryView = Backbone.View.extend(
    {
	tagName : "div",
	className : "message_entry",
	typing_timeout : 1500,

        initialize : function() {
            _.bindAll(this, "key_down", "message", "clear", "typing_started", 
		     "typing_ended", "cancel_typing_timer");
	     this.textarea = this.$("textarea");
	     this.textarea.keydown(this.key_down);
	     this.typing_timer = null;
	 },

	 key_down : function(event) {
	     console.log(event);
	     var kc = event.keyCode;
	     var message = null;
	     switch(kc) {
	     case 13:
		 // return-shift is a normal return
		 if(!event.shiftKey) {
		     this.typing_ended();
		     message = this.message();
		     this.clear();
		     this.trigger("send_message", message);
		     // no newline added to the area
		     event.preventDefault();
		     break;
		 }
	     default:
		 this.typing_started();
	     }
	 },

	 message: function() {
	     return this.textarea.val();
	 },

	 clear : function() {
	     this.textarea.val("");
	 },

	 typing_started : function() {
	     this.cancel_typing_timer();
	     this.typing_timer = setTimeout(this.typing_ended, this.typing_timeout);
	     this.trigger("typing", true);
	 },

	 typing_ended : function() {
	     this.cancel_typing_timer();
	     this.trigger("typing", false);
	 },


	 cancel_typing_timer : function() {
	    if(this.typing_timer != null) {
		clearTimeout(this.typing_timer);
		this.typing_timer = null;
	    }
	}
    }
);



ChatHub = function() 
{
    this.initialize.apply(this, arguments);
}

_.extend(ChatHub.prototype,
	 {
	     initialize: function(mev, endpoint, usercookie) {
		 _.bindAll(this, "typing", "send_message", "post");
		 this.endpoint = endpoint;
		 this.usercookie = usercookie;
		 this._typing = false;
		 mev.bind("typing", this.typing);
		 mev.bind("send_message", this.send_message);
	     },
	     
	     typing : function(typing) {
		 console.log("typing:" + typing);
		 if(this._typing != typing) {
		     this.post({"typing" : typing});
		 }
		 this._typing = typing;
	     },
	     
	     send_message : function(message) {
		 console.log("send_message:" + message);
		 this.post({"message" : message});
	     },

	     post : function(message) {
		 message.usercookie = this.usercookie;
		 $.post(this.endpoint, message);
	     }
	 }
	);

