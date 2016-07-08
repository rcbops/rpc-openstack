(function() {
  var searchFilter = function(event) {
    // Get the search text value
    var searchText = $(event.target).val(),
        // Turn it into a regular expression
        searchRe = RegExp(searchText, "i"),
        // Find all of the templates/solutions on the page
        $templates = $(event.target).parent().siblings().find('.template'),
        // Find all of the titles of the solutions
        $heads = $templates.find('thead').find('th'),
        // Find all the short descriptions of the templates
        $bodies = $templates.find('tbody').find('p');

    // If the user cleared out the box, show everything again
    if (searchText.length <= 0) {
      $templates.show();
      return;
    }

    // A simple helper to tell us when we've found a match
    var filterByRegExp = function(index, elem) {
      return elem.innerHTML.search(searchRe) >= 0;
    };

    // Collect the matches in the head and body of the tables
    var $headMatches = $heads.filter(filterByRegExp),
        $bodyMatches = $bodies.filter(filterByRegExp);

    // Make an array of elements to display after we hide everything
    var toShow = $.unique(
      $.merge($headMatches, $bodyMatches).map(function(i, elem) {
        return $(elem).parentsUntil('div.template').last().parent();
      })
    );

    // Hide everything and then show only what matches
    $templates.hide();
    toShow.each(function(i, elem) {
      $(elem).show();
    });
  };

  // Register our event handler
  $('#filter-templates > input').on('keyup', searchFilter);
})();
