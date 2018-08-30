import json
import urllib, urllib.parse
from urllib import parse

def run_query(search_terms):
    root_url = 'https://api.cognitive.microsoft.com/bing/v7.0'
    service = 'Web'

    results_per_page = 10
    offset = 0

    query = "'{0}'".format(search_terms)
    query = parse.quote(query)

    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        service,
        results_per_page,
        offset,
        query
    )

    username = ''
    bing_api_key = 'dfbcab20e5154916b0dd45a77b9f5e28'

    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)
    # Create our results list which we'll populate.
    results = []
    try:
        # Prepare for connecting to Bing's servers.
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        # Connect to the server and read the response generated.
        response = urllib.request.urlopen(search_url).read()
        response = response.decode('utf-8')
        # Convert the string response to a Python dictionary object.
        json_response = json.loads(response)
        # Loop through each page returned, populating out results list.
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']
            })

    except urllib.error.URLError as e:
        print("Error when querying the Bing API: ", e)

    # Return the list of results to the calling function.
    return results


def main():
    # Query, get the results and create a variable to store rank.
    query = input("Please enter a query: ")
    results = run_query(query)
    rank = 1

    # Loop through our results.
    for result in results:
        # Print details.
        print("Rank {0}".format(rank))

        print(result['title'])

        print(result['link'])


        # Increment our rank counter by 1.
        rank += 1
        
if __name__ == '__main__':
    main()





