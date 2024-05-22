"""Helper extractor to search and extract organizations from Wikidata.

Wikidata Extractor require a call to wikidata to search the organization label which can
take longer than usual as wikidata needs to search through an extensive database.
That's why the default Timeout for search request is 80 seconds.

In addition to extended timeout, wikidata sometimes start to block requests if too many
requests are being sent, to avoid this there is a backoff system in place which might
make the extraction process even slower.

Common use cases
----------------

- extract info about an organization from wikidata using organization name

Configuration
-------------

For configuring wikidata extractor, wiki_api_url and wiki_query_service_url parameters
in `mex.common.settings` needs to be set to Wikidata API URL (also referred to as
MediaWiki API) https://www.wikidata.org/w/api.php and Wikidata Query Service URL
https://query.wikidata.org/ respectively.

Extracting organization
-----------------------

Use `search_organization_by_label` in `wikidata.extract` by passing in the name of one
organization. This function will first call wikidata query service to search for
organization and then call wikidata api url on each one of them to fetch all info about
the organization.

Transforming organization
-------------------------

Use the `transform_wikidata_organizations_to_extracted_organizations` in
`wikidata.transform` to get MEx `ExtractedOrganization` from wikidata results.
"""
