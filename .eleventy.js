module.exports = function (eleventyConfig) {
  eleventyConfig.addLayoutAlias('base', 'layouts/base.njk');

  eleventyConfig.addCollection("spendsOver500", (collection) => {
    const allItems = collection.getAll()[0].data.spendsOver500;

    var spendCollection = [];

    for (const [key, value] of Object.entries(allItems)) {
      var monthSpendData = {
        "title": key,
        "displayTitle": (new Date(`${key}-01`)).toLocaleString("en-GB", { month: "long", year: "numeric" }),
        "data": value
      }

      spendCollection.push(monthSpendData);
    }

    return spendCollection;
  });

  eleventyConfig.addFilter("jsonify", function (value) { return JSON.stringify(value, null, 4) });

  eleventyConfig.addFilter("fixed", function (value, length) { return value?.toFixed(length || 2) });

  eleventyConfig.addFilter("sum", function (value, propName) {
    return value.reduce((accumulator, currentValue) => {
      return accumulator + currentValue[propName]
    }, 0);
  });

  eleventyConfig.addFilter("toCurrency", function (value) {
    let GBPFormat = new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP',
    });

    return GBPFormat.format(value);
  })

  eleventyConfig.addPassthroughCopy("CNAME");

};
