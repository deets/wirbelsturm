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
    }
);



UserListView = Backbone.View.extend( 
    {

        tagName : "ul",
        className : "user_list",
        initialize : function() {
            _.bindAll(this, "render", "add_user");
            this.model.bind("add", this.add_user);
            
        },

        add_user : function(user) {
            var li = $("<li/>");
            li.attr("id", this.el.id + "_" + user.id);
            li.text(user.get("name"));
            $(this.el).append(li);
        },

        render : function() {
            return this;
        }
    }
);