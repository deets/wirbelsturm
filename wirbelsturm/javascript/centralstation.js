var CentralStation = Backbone.Model.extend(
    {
	initialize : function() {
	    _.bindAll(this, "start", "dispatch", "error", "timeout");
	    if(this.get("endpoint") == null) {
		throw new Error("Now endpoint given!");
	    }
	},

	start : function() {
	    console.log("start");
	    var d = $.getJSON(this.get("endpoint")).
		success(this.dispatch).
		error(this.error);
	    this.set({"state" : "running"});
	},

	dispatch : function(data) {
	    console.log("dispatch");
	    console.log(data);
	    this.start();
	},

	timeout : function() {
	    console.log("timeout");
	    this.start();
	},

	error : function(data) {
	    console.log("error");
	    this.set({ "state" : "error"});
	},

	defaults : {
	    state : "new",
	    endpoint : null,
	    timeout : 3000
	}
    }
);