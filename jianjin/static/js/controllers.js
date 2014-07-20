var jianjinControllers = angular.module('jianjinControllers', []);

jianjinControllers.controller('HeaderCtrl', function ($scope, $location) {
  $scope.isActive = function (viewLocation) {
    return $location.path().indexOf(viewLocation) == 0;
  };
});

jianjinControllers.controller('BrowseListCtrl', function ($scope, $http) {
  $http.get('/words/words/').success(function(data) {
    $scope.words = data;
  }).error(function(data, status) {
    $scope.error = data;
    $scope.error_status = status;
  });
});

jianjinControllers.controller('BrowseWordCtrl', function ($scope, $http, $routeParams) {
  $scope.wordId = $routeParams.wordId;
  $http.get('/words/words/' + $routeParams.wordId).success(function(data) {
    $scope.word = data;
  }).error(function(data, status) {
    $scope.error = data;
    $scope.error_status = status;
  });
});
