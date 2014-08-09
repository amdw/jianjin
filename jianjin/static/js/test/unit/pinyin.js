'use strict';

describe('pinyin', function() {
  beforeEach(module('pinyin'));

  it('should correctly convert single word', inject(function(pinyinFilter) {
    expect(pinyinFilter("ni3hao3")).toBe("nǐhǎo");
    expect(pinyinFilter("bao3bei4")).toBe("bǎobèi");
    expect(pinyinFilter("Shuai4ge1")).toBe("Shùaigē");
    expect(pinyinFilter("CHUI1NIU2")).toBe("CHŪINIÚ");
    expect(pinyinFilter("mei3nv3")).toBe("měinǚ");
    expect(pinyinFilter("MEI3NV3")).toBe("MĚINǙ");
  }));

  it('should correctly convert multiple words', inject(function(pinyinFilter) {
    expect(pinyinFilter("ni3hao3 bao3bei4!")).toBe("nǐhǎo bǎobèi!");
  }));

  it('should ignore irrelevant text', inject(function(pinyinFilter) {
    expect(pinyinFilter("nz3hao3")).toBe("nz3hǎo");
    expect(pinyinFilter("ni3hao5")).toBe("nǐhao5");
  }));

  it('should correctly generate MDBG links', inject(function(mdbglinkFilter) {
    expect(mdbglinkFilter("蛋白质")).toBe("http://www.mdbg.net/chindict/chindict.php?page=worddict&wdrst=0&wdqb=蛋白质");
  }));
});
