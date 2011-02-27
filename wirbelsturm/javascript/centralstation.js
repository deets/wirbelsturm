var CentralStation = Backbone.Model.extend(
    {
	LATEST_MESSAGE_ID : "Latest-Message-ID",

	initialize : function() {
	    _.bindAll(this, "start", "dispatch", "error", "ajax_send",
		     "ajax_complete");
	    if(this.get("endpoint") == null) {
		throw new Error("Now endpoint given!");
	    }
	    $("body").ajaxSend(this.ajax_send);
	    $("body").ajaxComplete(this.ajax_complete);
	},

	start : function() {
	    console.log("start");
	    var d = $.getJSON(this.get("endpoint")).
		success(this.dispatch).
		error(this.error);
	    if(this.get("state") != "running") {
		this.set({"state" : "running"});		
	    }
	},

	dispatch : function(data) {
	    var self = this;
	    console.log("dispatch");
	    if("messages" in data) {
		$.each(data.messages, 
		       function(__, message) {
			   console.log(message);
			   self.trigger(message.scope, message.operation, message.payload);
		       }
		      );
	    }
	    self.start();
	},

	error : function(result) {
	    // timeout, just re-start
	    if("status" in result && result.status == 504) {
		this.start();		
	    } else {
                console.log("error");
                this.set({ "state" : "error"});
	    }
	},

	ajax_send : function(event, req, options) {
	    if(options.url !== this.get("dispatch")) {
		return;
	    }
	    if(this.get("latest_message_id") != null) {
		req.setRequestHeader(this.LATEST_MESSAGE_ID, this.get("latest_message_id"));
	    }
	},

	ajax_complete : function(event, req, options) {
	    if(options.url !== this.get("dispatch")) {
		return;
	    }
	    this.set({"latest_message_id"
		      : req.getResponseHeader(this.LATEST_MESSAGE_ID )});
	},

	defaults : {
	    state : "new",
	    endpoint : null,
	    latest_message_id : null
	}
    }
);