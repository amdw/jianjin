'use strict';

describe('controllers', function() {
  beforeEach(module('jianjinControllers'));

  it('should correctly extract example sentences from words', inject(function(extract_examples) {
    expect(extract_examples({})).toEqual([]);
    var s1 = {"definition": "wibble", "sentence": "wobble"};
    var s2 = {"definition": "hubble", "sentence": "bubble"};
    var s3 = {"definition": "hocus", "sentence": "pocus"};
    var word = {"definitions": [
      {"example_sentences": [s1]},
      {"example_sentences": [s2]},
      {"example_sentences": [s1, s3]}
    ]};
    expect(extract_examples(word)).toEqual([s1, s2, s3]);
  }));
});
