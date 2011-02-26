User = Backbone.Model.extend(
    {
        initialize : function() {

        },
        defaults : {
            typing : false
        }
    }

);


UserList = Backbone.Collection.extend(
    {
        model : User,
        initialize : function() {
            _.bindAll(this, "add");
            var self = this;
            central_station.bind("user_joined", 
                                 function(user_data) {
                                     var user = new User(user_data);
                                     self.add(user);
                                 });
        }
    },
    // class properties
    {
        // site-wide initialization
        setup_user_list : function(list_id, user_data) {
            var user_list =new UserList();
            var ul_view = new UserListView({
                                               el : $(list_id).get(0),
                                               model : user_list
                                           });
            window.user_view = ul_view;
            window.user_list = user_list;
	    $.each(user_data, function(_, ud)
		   {
		       user_list.add(new User(ud));
		   }
		  );
        }
    }
);



UserListView = Backbone.View.extend( 
    {

        tagName : "ul",
        className : "user_list",
        initialize : function() {
            _.bindAll(this, "render", "add_user", "toggle_typing");
            this.model.bind("add", this.add_user);
            this.user2el = {};            
        },

        add_user : function(user) {
	    if(user.id in this.user2el)
		return;
            var li = $("<li/>");
            li.text(user.get("name"));
            $(this.el).append(li);
            this.user2el[user.id] = li;
            user.bind("change:typing", this.toggle_typing);
        },

        render : function() {
            return this;
        },

        toggle_typing : function(user) {
            var li = this.user2el[user.id];
            if(user.get("typing")) {
                $(li).addClass("typing");
            } else {
                $(li).removeClass("typing");
            }
        }
    }
);


