
MessageListView = Backbone.View.extend(
    {
	tagName : "div",
	className : "message_list",
        initialize : function() {
	    _.bindAll(this, "message_added");
	    this.list = this.$("ul");
	    central_station.bind("message_list", this.message_added);
	 },

	message_added : function(_operation, payload) {
	    var li = $("<li>");
	    li.text(payload.message);
	    this.list.append(li);
	    $(this.list).animate({ scrollTop: $(this.list).attr("scrollHeight") - $(this.list).height() }, 500);
	}
    }
);


