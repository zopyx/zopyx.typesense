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

var filterBy = '';
if (CURRENT_PATH.length > 1) // root = "/"
    filterBy = `all_paths:=${CURRENT_PATH}`;

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
        queryBy: ts_settings["query_by"],
        filterBy: filterBy
    },
});
const searchClient = typesenseInstantsearchAdapter.searchClient;

const search = instantsearch({
    searchClient,
    indexName: ts_settings["collection"]
});

/*
 * Example:
 * https://github.com/typesense/showcase-ecommerce-store/blob/master/src/app.js
 */

search.addWidgets([
    instantsearch.widgets.searchBox({
        container: '#searchbox',
        showSubmit: false,
        showReset: false,
        placeholder: 'Search for... ',
        autofocus: false,
        searchAsYouType: true,
        showLoadingIndicator: true,
        cssClasses: {
            input: 'form-control form-control-sm border border-light text-dark',
            loadingIcon: 'stroke-primary',
        },
    }),
    instantsearch.widgets.configure({
        hitsPerPage: 10,
    }),
    instantsearch.widgets.hits({
        container: '#hits',
        templates: {
            item: `
          <div class="hit">
            <div class="hit-title"> <a class="hit-link" href="${PORTAL_URL}/{{path}}\">{{#helpers.highlight}}{ "attribute": "title" }{{/helpers.highlight}}</a></div>
            <div class="hit-meta">
                <span class="hit-portal_type">{{#helpers.highlight}}{ "attribute": "portal_type" }{{/helpers.highlight}}</span> |
                <span class="hit-review_state">{{#helpers.highlight}}{ "attribute": "review_state" }{{/helpers.highlight}}</span> |
                <span class="hit-created">{{#helpers.highlight}}{ "attribute": "created" }{{/helpers.highlight}}</span> |
                <span class="hit-modified">{{#helpers.highlight}}{ "attribute": "modified" }{{/helpers.highlight}}</span>
            </div>
            <div class="hit-text">{{#helpers.highlight}}{ "attribute": "text" }{{/helpers.highlight}}</div>
          </div>
`,
        },
    }),
    instantsearch.widgets.pagination({
        container: '#pagination',
        scrollTo: "header",
        root: "nav",
        cssClasses: {
            root: "navigation",
            list: 'pagination ',
            item: 'page-item ',
            link: 'text-decoration-none',
            disabledItem: 'text-muted',
            selectedItem: 'fw-bold text-primary',
        },

    }),
    instantsearch.widgets.refinementList({
        container: '#review-state',
        attribute: 'review_state',
    }),
    instantsearch.widgets.refinementList({
        container: '#portal-type',
        attribute: 'portal_type',
        showMore: false
    }),
    instantsearch.widgets.refinementList({
        container: '#subject',
        attribute: 'subject',
    }),
    instantsearch.widgets.refinementList({
        container: '#language',
        attribute: 'language',
    }),

    instantsearch.widgets.stats({
        container: '#stats',
        templates: {
            text: `
      {{#hasNoResults}}No hits{{/hasNoResults}}
      {{#hasOneResult}}1 hit{{/hasOneResult}}
      {{#hasManyResults}}{{#helpers.formatNumber}}{{nbHits}}{{/helpers.formatNumber}} hits {{/hasManyResults}}
      found in {{processingTimeMS}}ms
    `,
        },
        cssClasses: {
            text: 'small',
        },
    }),

    instantsearch.widgets.hitsPerPage({
        container: '#hits-per-page',
        items: [{
            label: '10 per page',
            value: 10,
            default: true
        }, {
            label: '20 per page',
            value: 20
        }, {
            label: '50 per page',
            value: 50
        }, {
            label: '100 per page',
            value: 100
        }, ],
        cssClasses: {
            select: 'custom-select custom-select-sm',
        },
    }),
]);

search.start();
