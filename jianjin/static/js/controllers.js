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

jianjinControllers.constant('get_word_url', function(word_id) {
  return '/words/words/' + word_id + '/';
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
    $http.get('/words/tags/').success(function(data) {
      $scope.all_tags = data.map(function(t) { return t.tag });
    }).error(handle_error($scope));
  };
});

jianjinControllers.factory('change_confidence', function($http) {
  return function($scope, new_confidence) {
    // Disable buttons while this request is in progress
    $scope.enable_confidence = false;
    $http.post('/words/confidence/' + $scope.word.id + '/', {"new": new_confidence}).success(function(data) {
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

  $http.get($scope.tag ? '/words/wordsbytag/' + $scope.tag + '/' : '/words/words/').success(function(data) {
    $scope.words = data;
  }).error(handle_error($scope));
  load_tags($scope, $http);
});

jianjinControllers.wordControllerGenerator = function(is_new) {
  return function ($scope, $http, $routeParams, $location, handle_error, increase_confidence, decrease_confidence, get_word_url) {
    $scope.word_id = $routeParams.word_id;
    $scope.increase_confidence = function() { increase_confidence($scope) };
    $scope.decrease_confidence = function() { decrease_confidence($scope) };
    $scope.parts_of_speech = [" ", "N", "V", "ADJ", "ADV", "PREP"];

    $scope.enable_confidence = true;
    $scope.editing = is_new;
    $scope.is_new = is_new;

    $scope.edit = function() {
      $scope.editing = true;
      // Poor man's deep copy
      $scope.original_word = JSON.parse(JSON.stringify($scope.word));
    };

    $scope.save = function() {
      for (i in $scope.word.tags) {
        if ($scope.word.tags[i].new) {
          delete $scope.word.tags[i].new;
        }
      }
      for (i in $scope.word.related_words) {
        if ($scope.word.related_words[i].new) {
          delete $scope.word.related_words[i].new;
        }
      }
      var on_success = function(data) {
        $scope.word = data;
        $scope.editing = false;
        if ($scope.is_new) {
          $location.path('/browse/' + data.id);
        }
      };
      var on_error = function(data, status) {
        window.alert("Error " + status + " saving word:\n" + JSON.stringify(data));
      };
      if ($scope.is_new) {
        $http.post("/words/words/", $scope.word).success(on_success).error(on_error);
      }
      else {
        $http.put(get_word_url($scope.word_id), $scope.word).success(on_success).error(on_error);
      }
    };

    $scope.cancel_edits = function() {
      $scope.word = $scope.original_word;
      $scope.editing = false;
    };

    $scope.add_definition = function() {
      if (typeof $scope.word.definitions == 'undefined') {
        $scope.word.definitions = [];
      }
      $scope.word.definitions.push({});
    };

    $scope.delete_definition = function(def) {
      $scope.word.definitions = $scope.word.definitions.filter(function(d) { return d !== def });
    };

    $scope.add_example_sentence = function(def) {
      if (typeof def.example_sentences == 'undefined') {
        def.example_sentences = [];
      }
      def.example_sentences.push({});
    };

    $scope.delete_example_sentence = function(def, sentence) {
      def.example_sentences = def.example_sentences.filter(function(s) { return s !== sentence });
    };

    $scope.add_related_word = function() {
      if (typeof $scope.word.related_words == 'undefined') {
        $scope.word.related_words = [];
      }
      $scope.word.related_words.push({"word": "", "new": true});
    };

    $scope.remove_related_word = function(related_word) {
      $scope.word.related_words = $scope.word.related_words.filter(function(w) { return w !== related_word });
    };

    $scope.add_tag = function() {
      if (typeof $scope.word.tags == 'undefined') {
        $scope.word.tags = [];
      }
      $scope.word.tags.push({"tag": "", "new": true});
    };

    $scope.remove_tag = function(tag) {
      $scope.word.tags = $scope.word.tags.filter(function(t) { return t !== tag });
    };

    $scope.highlight = function(text) {
      return text.replace(new RegExp($scope.word.word, 'g'), '<span class="highlight">' + $scope.word.word + '</span>');
    };

    if ($scope.is_new) {
      $scope.word = {};
      $scope.add_definition();
    }
    else {
      $http.get(get_word_url($routeParams.word_id)).success(function(data) {
        $scope.word = data;
      }).error(handle_error($scope));
    }
  };
};

jianjinControllers.controller('BrowseWordCtrl', jianjinControllers.wordControllerGenerator(false));

jianjinControllers.controller('NewWordCtrl', jianjinControllers.wordControllerGenerator(true));

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
    $http.get('/words/flashcard' + ($scope.tag ? '/' + $scope.tag : '') + '/').success(function(data) {
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

