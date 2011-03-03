var CentralStation = Backbone.Model.extend(
    {
	initialize : function() {
	    _.bindAll(this, "start", "dispatch", "error", "ajax_send",
		     "ajax_complete");
	    if(this.get("endpoint") == null) {
		throw new Error("Now endpoint given!");
	    }
	    // $("body").ajaxSend(this.ajax_send);
	    // $("body").ajaxComplete(this.ajax_complete);
	},

	start : function() {
	    var url = this.get("endpoint") + "/" + new Date().getTime();
	    var lmid = this.get("latest_message_id");
	    if(lmid !== null) {
		url = url + "?latest_message_id=" +lmid;
	    }
	    var d = $.getJSON(url).
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
	    var lmid = data.latest_message_id;
	    console.log("lmid from server:" + lmid);
	    if(lmid !== undefined) {
		this.set({"latest_message_id" : lmid});
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

	// ajax_send : function(event, req, options) {
	//     var ep = this.get("endpoint");
	//     if(options.url.substring(0, ep.length) !== ep) {
	// 	return;
	//     }
	//     console.log("ajax_send");
	//     var lmid = this.get("latest_message_id");
	//     console.log("ajax_send lmid:" + lmid);
	//     if(lmid != null) {
	// 	req.setRequestHeader(this.LATEST_MESSAGE_ID, this.get("latest_message_id"));
	//     }
	// },

	// ajax_complete : function(event, req, options) {
	//     var ep = this.get("endpoint");
	//     if(options.url.substring(0, ep.length) !== ep) {
	// 	return;
	//     }
	//     console.log("ajax_complete");
	//     var lmid = req.getResponseHeader(this.LATEST_MESSAGE_ID);
	//     console.log("lmid: " + lmid);
	//     if(lmid != null) {
	// 	this.set({"latest_message_id" : lmid});		
	//     }
	// },

	defaults : {
	    state : "new",
	    endpoint : null,
	    latest_message_id : null
	}
    }
);