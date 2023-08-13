module.exports = function (eleventyConfig) {
  eleventyConfig.addLayoutAlias('base', 'layouts/base.njk');

  eleventyConfig.addCollection("spendsOver500", (collection) => {
    const allItems = collection.getAll()[0].data.spendsOver500;

    var spendCollection = [];

    for (const [key, value] of Object.entries(allItems)) {
      var monthSpendData = {
        "title": key,
        "data": value
      }

      spendCollection.push(monthSpendData);
    }
    
    return spendCollection;
  });

  eleventyConfig.addFilter("jsonify", function (value) { return JSON.stringify(value, null, 4) });

  eleventyConfig.addFilter("fixed", function (value, length) { return value?.toFixed(length || 2) });

  eleventyConfig.addFilter("size", function (value) { return value.length });

  eleventyConfig.addPassthroughCopy("CNAME");

};
