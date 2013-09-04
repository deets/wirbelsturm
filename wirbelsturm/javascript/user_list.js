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
            _.bindAll(this, "add", "dispatch");
            var self = this;
            central_station.bind("user_list", this.dispatch);
        },

        dispatch : function(operation, payload) {
            switch(operation) {
            case "add":
                this.add(new this.model(payload));
                break;
            case "modify":
                var id = payload.id;
                delete payload.id;
                var m = this.get(id);
                m.set(payload);
                break;
            }
            var userlist = [];
            $.each(this.models, function(_, user)
                   {
                       userlist.push(user.attributes);
                   }
                  );
            window.users_scope.users = userlist;
            window.users_scope.$digest();
        }
    },
    // class properties
    {
        // site-wide initialization
        setup_user_list : function(list_id, user_data) {
            var user_list = new UserList();
            window.user_list = user_list;
            $.each(user_data, function(_, ud)
                   {
                       user_list.add(new User(ud));
                   }
                  );
        }
    }
);



function UserListView($scope) {
    $scope.users = [
      ];
    function typingclass(typing) {
        return typing ? "typing" : "";
    }
    $scope.typingclass = typingclass;
   window.users_scope = $scope;
}
