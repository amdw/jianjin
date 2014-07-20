var jianjinApp = angular.module('jianjinApp', ['ngRoute', 'jianjinControllers']);

jianjinApp.config(function ($routeProvider) {
  $routeProvider.
    when('/', {
      redirectTo: '/browse',
    }).
    when('/browse', {
      templateUrl: '/static/browse.html',
      controller: 'BrowseListCtrl',
    }).
    when('/browse/:word_id', {
      templateUrl: '/static/word.html',
      controller: 'BrowseWordCtrl',
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
