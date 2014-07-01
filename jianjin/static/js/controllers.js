var jianjinControllers = angular.module('jianjinControllers', []);

jianjinControllers.controller('HeaderCtrl', function ($scope, $location) {
  $scope.isActive = function (viewLocation) {
    return viewLocation === $location.path();
  };
});

jianjinControllers.controller('BrowseCtrl', function ($scope, $http) {
  $http.get('/words/words/').success(function(data) {
    $scope.words = data;
  });
});
