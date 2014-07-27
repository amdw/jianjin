'use strict';

describe('pinyin', function() {
  beforeEach(module('pinyin'));

  it('should correctly convert single word', inject(function(convert) {
    expect(convert("ni3hao3")).toBe("nǐhǎo");
    expect(convert("bao3bei4")).toBe("bǎobèi");
    expect(convert("Shuai4ge1")).toBe("Shùaigē");
    expect(convert("CHUI1NIU2")).toBe("CHŪINIÚ");
    expect(convert("mei3nv3")).toBe("měinǚ");
    expect(convert("MEI3NV3")).toBe("MĚINǙ");
  }));

  it('should correctly convert multiple words', inject(function(convert) {
    expect(convert("ni3hao3 bao3bei4!")).toBe("nǐhǎo bǎobèi!");
  }));

  it('should ignore irrelevant text', inject(function(convert) {
    expect(convert("nz3hao3")).toBe("nz3hǎo");
    expect(convert("ni3hao5")).toBe("nǐhao5");
  }));
});
