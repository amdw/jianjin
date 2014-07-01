var jianjinControllers = angular.module('jianjinControllers', []);

jianjinControllers.controller('HeaderController', function ($scope, $location) {
  $scope.isActive = function (viewLocation) {
    return viewLocation === $location.path();
  };
});
