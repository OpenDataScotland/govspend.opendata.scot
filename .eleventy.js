module.exports = function (eleventyConfig) {
  const _ = require("lodash")

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

  eleventyConfig.addCollection("spendsOver500_monthly", (collection) => {
    return _(collection.getAll()[0].data.spendsOver500).transform(function (result, value, key) {
      result.push({
        title: key,
        displayTitle: (new Date(`${key}-01`)).toLocaleString("en-GB", { month: "long", year: "numeric" }),
        total: _(value).sumBy("Transaction Amount")
      })
    }, []);
  })

  eleventyConfig.addFilter("jsonify", function (value) { return JSON.stringify(value, null, 4) });

  eleventyConfig.addFilter("fixed", function (value, length) { return value?.toFixed(length || 2) });

  eleventyConfig.addFilter("sum", function (value, propName) {
    return _(value).sumBy(propName);
  });

  const GBPFormat = new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
  });

  function toCurrency(value) {
    return GBPFormat.format(value);
  }

  eleventyConfig.addFilter("toCurrency", function (value) {
    return toCurrency(value);
  })

  eleventyConfig.addFilter("findTopSpender", function (value) {
    var maxSpend = _(value)
      .groupBy("Directorate")
      .map((directorate, total) => ({
        directorate: total,
        total: _.sumBy(directorate, "Transaction Amount")
      }))
      .maxBy("total");

    return `${maxSpend.directorate} (${toCurrency(maxSpend.total)})`;
  })

  eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addPassthroughCopy("robots.txt");
};
