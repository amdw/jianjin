var pinyin = angular.module('pinyin', []);

pinyin.constant('splitText', function(text) {
  var result = [];
  var i = 0;
  while (true) {
    if (i >= text.length) {
      break;
    }
    var part = [];
    while (i < text.length) {
      part.push(text[i]);
      if (text[i].match(/[0-9]/)) {
        result.push(part.join(""));
        part = [];
      }
      i += 1;
    }
    if (part.length > 0) {
      result.push(part.join(""));
    }
  }
  return result;
});

pinyin.constant('pickVowel', function(syllable) {
  var firstVowelIdx = -1;
  for (i = 0; i < syllable.length; i++) {
    if (syllable[i].match('[aeouvAEOUV]')) {
      return i;
    }
    if (syllable[i].match('[aeiouvAEIOUV]') && firstVowelIdx < 0) {
	firstVowelIdx = i;
    }
  }
  return firstVowelIdx;
});

pinyin.constant('vowels', {
  'a': ['ā', 'á', 'ǎ', 'à'],
  'A': ['Ā', 'Á', 'Ǎ', 'À'],
  'e': ['ē', 'é', 'ě', 'è'],
  'E': ['Ē', 'É', 'Ě', 'È'],
  'i': ['ī', 'í', 'ǐ', 'ì'],
  'I': ['Ī', 'Í', 'Ǐ', 'Ì'],
  'o': ['ō', 'ó', 'ǒ', 'ò'],
  'O': ['Ō', 'Ó', 'Ǒ', 'Ò'],
  'u': ['ū', 'ú', 'ǔ', 'ù'],
  'U': ['Ū', 'Ú', 'Ǔ', 'Ù'],
  'v': ['ǖ', 'ǘ', 'ǚ', 'ǜ'],
  'V': ['Ǖ', 'Ǘ', 'Ǚ', 'Ǜ']
});

pinyin.factory('convertPart', function(vowels, pickVowel) {
  return function(part) {
    var syllableMatch = part.match('([a-zA-Z]+)([1-4])$');
    if (!syllableMatch) {
      return part;
    }
    var syllable = syllableMatch[1];
    var tone = syllableMatch[2];
    var vowelIdx = pickVowel(syllable);
    if (vowelIdx < 0) {
      return part;
    }
    var newVowel = vowels[syllable[vowelIdx]][tone-1];
    return part.substr(0, part.length - syllable.length - 1) + 
  	   syllable.substr(0, vowelIdx) + newVowel + syllable.substr(vowelIdx + 1);
  }
});

pinyin.filter('pinyin', function(splitText, convertPart) {
  return function(text) {
    var parts = splitText(text);
    var convertedParts = parts.map(convertPart);
    return convertedParts.join("");
  };
});

