/* global instantsearch */


var remote_url = PORTAL_URL + "/@@typesense-search-settings";
var ts_settings = null;

function getSearchSettings() {
    return $.getJSON({
        type: "GET",
        url: remote_url,
        async: false
    }).responseText;
}

ts_settings = JSON.parse(getSearchSettings());

const typesenseInstantsearchAdapter = new TypesenseInstantSearchAdapter({
  server: {
    apiKey: ts_settings["api_key"],
    nodes: ts_settings["nodes"]
  },
  // The following parameters are directly passed to Typesense's search API endpoint.
  //  So you can pass any parameters supported by the search endpoint below.
  //  queryBy is required.
  //  filterBy is managed and overridden by InstantSearch.js. To set it, you want to use one of the filter widgets like refinementList or use the `configure` widget.
  additionalSearchParameters: {
    queryBy: ts_settings["query_by"]
  },
});
const searchClient = typesenseInstantsearchAdapter.searchClient;

const search = instantsearch({
  searchClient,
  indexName: ts_settings["collection"]
});

search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
  }),
  instantsearch.widgets.configure({
    hitsPerPage: 8,
  }),
  instantsearch.widgets.hits({
    container: '#hits',
    templates: {
      item(item) {
        return `
        <div>
          <div class="hit-name">
            ${item._highlightResult.title.value}
          </div>
        </div>
      `;
      },
    },
  }),
  instantsearch.widgets.pagination({
    container: '#pagination',
  }),
]);

search.start();
