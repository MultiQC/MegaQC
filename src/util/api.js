import JsonApiClient from "@holidayextras/jsonapi-client"

/**
 * Returns an API client with an associated API key (synchronously).
 */
export function getClient(token) {
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
    return new JsonApiClient("/rest_api/v1", options);
}

/**
 * Returns a promise of an API client with an associated API key.
 */
export function getAuthenticatedClient(token) {
    const client = getClient(token);

    // If we don't have a token, we need to obtain one
    if (!token) {
        return getToken(client).then(token => {
            client._transport._auth.header = {access_token: token};
            return client
        })
    } else
        return Promise.resolve(client);
}

/**
 * Returns a promise that resolves to an API token
 */
export function getToken(client) {
    return client.get('users', 'current').then(data => {
        return data.toJSON().api_token;
    })
}
