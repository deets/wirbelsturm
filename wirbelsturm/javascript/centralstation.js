var CentralStation = Backbone.Model.extend(
    {
	initialize : function() {
	    _.bindAll(this, "start", "dispatch", "error");
	    if(this.get("endpoint") == null) {
		throw new Error("Now endpoint given!");
	    }
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
			   self.trigger(message.type, message.payload);
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

	defaults : {
	    state : "new",
	    endpoint : null
	}
    }
);