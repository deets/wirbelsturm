User = Backbone.Model.extend(
    {
	
    }
);


UserList = Backbone.Collection.extend(
    {
	model: User
    }
);

var userlist = new UserList();
