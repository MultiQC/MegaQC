import JsonApiClient from "@holidayextras/jsonapi-client"

export default function getClient(token) {
    let options = {};

    // If we already have a token, attach it here
    if (token) {
        options = {
            header: {
                access_token: token
            }
        };
    }

    // Construct the client
    const client = new JsonApiClient("/rest_api/v1", options);

    // If we don't have a token, we need to obtain one
    if (!token) {
        client.get('users', 'current').then(data => {
            client._transport._auth.header.access_token = data.toJSON().api_token
        })
    }

    return client;
}

