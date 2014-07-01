var jianjinApp = angular.module('jianjinApp', ['ngRoute']);

jianjinApp.config(function ($routeProvider) {
  $routeProvider.
    when('/', {
      templateUrl: '/static/about.html',
    }).
    otherwise({
      redirectTo: '/'
    });
});
