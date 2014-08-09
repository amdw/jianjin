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
  $scope.word_id = $routeParams.word_id;
  $http.get('/words/words/' + $routeParams.word_id).success(function(data) {
    $scope.word = data;
  }).error(function(data, status) {
    $scope.error = data;
    $scope.error_status = status;
  });
});

jianjinControllers.controller('FlashcardCtrl', function($scope, $http, $routeParams) {
  $scope.tag = $routeParams.tag;

  $scope.reset = function() {
    $scope.show_pinyin_hint = false;
    $scope.show_examples_hint = false;
    $scope.show_answer = false;
  };

  $scope.load_flashcard = function() {
    $http.get('/words/flashcard' + ($scope.tag ? '?tag=' + $scope.tag : '')).success(function(data) {
      $scope.word = data;
    }).error(function(data, status) {
      $scope.error = data;
      $scope.error_status = status;
    });
  };

  $scope.set_show_pinyin_hint = function() {
    $scope.show_pinyin_hint = true;
  };

  $scope.set_show_examples_hint = function() {
    $scope.show_examples_hint = true;
  };

  $scope.set_show_all = function() {
    $scope.set_show_pinyin_hint();
    $scope.set_show_examples_hint();
    $scope.show_answer = true;
  };

  $scope.next_flashcard = function() {
    $scope.reset();
    $scope.load_flashcard();
  };

  // Initialisation

  $scope.next_flashcard();

  $http.get('/words/tags').success(function(data) {
    $scope.all_tags = data.map(function(t) { return t.tag });
  }).error(function(data, status) {
    $scope.error = data;
    $scope.error_status = status;
  });
});
