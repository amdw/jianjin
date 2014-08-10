var jianjinControllers = angular.module('jianjinControllers', []);

jianjinControllers.config(function($httpProvider) {
  // Need these settings to line up with what Django does
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

jianjinControllers.controller('HeaderCtrl', function ($scope, $location) {
  $scope.isActive = function (viewLocation) {
    return $location.path().indexOf(viewLocation) == 0;
  };
});

jianjinControllers.constant('handle_error', function($scope) {
  return function(data, status) {
    $scope.error = data;
    $scope.error_status = status;
  };
});

jianjinControllers.constant('extract_examples', function(word) {
  var result = [];
  for (i in word.definitions) {
    var def = word.definitions[i];
    for (j in def.example_sentences) {
      var s = def.example_sentences[j];
      // Quadratic, but example_sentences will usually be short
      if (result.indexOf(s) < 0) {
        result.push(s);
      }
    }
  }
  return result;
});

jianjinControllers.factory('load_tags', function(handle_error) {
  return function($scope, $http) {
    $http.get('/words/tags').success(function(data) {
      $scope.all_tags = data.map(function(t) { return t.tag });
    }).error(handle_error($scope));
  };
});

jianjinControllers.factory('change_confidence', function($http) {
  return function($scope, new_confidence) {
    // Disable buttons while this request is in progress
    $scope.enable_confidence = false;
    $http.post('/words/confidence/' + $scope.word.id, {"new": new_confidence}).success(function(data) {
      $scope.enable_confidence = true;
      $scope.word.confidence = data['new'];
    }).error(function(data, status) {
      window.alert("Failed to update confidence (" + status + "):\n" + JSON.stringify(data));
      $scope.enable_confidence = true;
    });
  };
});

jianjinControllers.factory('increase_confidence', function(change_confidence) {
  return function($scope) {
    change_confidence($scope, $scope.word.confidence + 1);
  };
});

jianjinControllers.factory('decrease_confidence', function(change_confidence) {
  return function($scope) {
    change_confidence($scope, $scope.word.confidence - 1);
  };
});

jianjinControllers.controller('BrowseListCtrl', function ($scope, $http, $routeParams, load_tags, handle_error) {
  $scope.tag = $routeParams.tag;

  $http.get($scope.tag ? '/words/wordsbytag/' + $scope.tag : '/words/words/').success(function(data) {
    $scope.words = data;
  }).error(handle_error($scope));
  load_tags($scope, $http);
});

jianjinControllers.controller('BrowseWordCtrl', function ($scope, $http, $routeParams, handle_error, increase_confidence, decrease_confidence) {
  $scope.word_id = $routeParams.word_id;
  $scope.increase_confidence = function() { increase_confidence($scope) };
  $scope.decrease_confidence = function() { decrease_confidence($scope) };
  $scope.enable_confidence = true;

  $http.get('/words/words/' + $routeParams.word_id).success(function(data) {
    $scope.word = data;
  }).error(handle_error($scope));
});

jianjinControllers.controller('FlashcardCtrl', function($scope, $http, $routeParams, load_tags, handle_error, extract_examples, increase_confidence, decrease_confidence) {
  $scope.tag = $routeParams.tag;

  $scope.reset = function() {
    $scope.show_pinyin_hint = false;
    $scope.show_examples_hint = false;
    $scope.show_answer = false;
    $scope.enable_confidence = true;
    $scope.examples = [];
  };

  $scope.load_flashcard = function() {
    $http.get('/words/flashcard' + ($scope.tag ? '/' + $scope.tag : '')).success(function(data) {
      $scope.word = data;
      $scope.examples = extract_examples(data);
    }).error(handle_error($scope));
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

  $scope.increase_confidence = function() { increase_confidence($scope) };
  $scope.decrease_confidence = function() { decrease_confidence($scope) };

  // Initialisation

  $scope.next_flashcard();
  load_tags($scope, $http);
});
