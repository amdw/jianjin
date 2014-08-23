var jianjinApp = angular.module('jianjinApp', ['ngRoute', 'ngSanitize', 'jianjinControllers', 'pinyin']);

jianjinApp.config(function ($routeProvider) {
  $routeProvider.
    when('/', {
      redirectTo: '/browse',
    }).
    when('/browse', {
      templateUrl: '/static/browse.html',
      controller: 'BrowseListCtrl',
    }).
    when('/browsetag/:tag', {
      templateUrl: '/static/browse.html',
      controller: 'BrowseListCtrl',
    }).
    when('/browse/:word_id', {
      templateUrl: '/static/word.html',
      controller: 'BrowseWordCtrl',
    }).
    when('/new', {
      templateUrl: '/static/word.html',
      controller: 'NewWordCtrl',
    }).
    when('/flashcard', {
      templateUrl: '/static/flashcard.html',
      controller: 'FlashcardCtrl',
    }).
    when('/flashcard/:tag', {
      templateUrl: '/static/flashcard.html',
      controller: 'FlashcardCtrl',
    }).
    when('/about', {
      templateUrl: '/static/about.html',
    }).
    otherwise({
      redirectTo: '/'
    });
});
