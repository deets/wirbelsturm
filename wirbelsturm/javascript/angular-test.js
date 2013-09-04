function UserListController($scope) {
    console.log("UserListController");
    $scope.users = [
       { "id" : "peter" ,
         "typing" : true
	 }
      ];
   document.users_scope = $scope;
}

