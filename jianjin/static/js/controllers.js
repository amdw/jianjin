var jianjinControllers = angular.module('jianjinControllers', []);

jianjinControllers.controller('HeaderCtrl', function ($scope, $location) {
  $scope.isActive = function (viewLocation) {
    return $location.path().indexOf(viewLocation) == 0;
  };
});

jianjinControllers.controller('BrowseListCtrl', function ($scope, $http) {
  $http.get('/words/words/').success(function(data) {
    $scope.words = data;
  });
});

jianjinControllers.controller('BrowseWordCtrl', function ($scope, $http, $routeParams) {
  $http.get('/words/words/' + $routeParams.wordId).success(function(data) {
    $scope.word = data;
  });
});
