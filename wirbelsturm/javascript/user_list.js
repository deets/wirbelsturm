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
        setup_user_list : function(list_id) {
            var user_list =new UserList();
            var ul_view = new UserListView({
                                               el : $(list_id).get(0),
                                               model : user_list
                                           });
            window.user_view = ul_view;
            window.user_list = user_list;
            // test setup
            user_list.add(new User({"id" : "pete", "name" : "Peter"}));
            user_list.add(new User({"id" : "heiner", "name" : "Heiner"}));
            karl = new User({"id" : "karl", "name" : "Karl"});
            user_list.add(karl);
            karl.set({"typing" : true});
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


