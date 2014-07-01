var jianjinApp = angular.module('jianjinApp', ['ngRoute', 'jianjinControllers']);

jianjinApp.config(function ($routeProvider) {
  $routeProvider.
    when('/', {
      redirectTo: '/browse',
    }).
    when('/browse', {
    }).
    when('/new', {
    }).
    when('/flashcard', {
    }).
    when('/about', {
      templateUrl: '/static/about.html',
    }).
    otherwise({
      redirectTo: '/'
    });
});
