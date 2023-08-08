module.exports = function(eleventyConfig) {
    eleventyConfig.addLayoutAlias('base', 'layouts/base.njk');

    eleventyConfig.addCollection("spendsOver500", (collection) => {
      const allItems = collection.getAll()[0].data.spendover500;
    
      // Filter or use another method to select the items you want
      // for the collection
      return allItems;
    });

    eleventyConfig.addFilter("jsonify", function(value) { return JSON.stringify(value, null, 4) });

  };
  