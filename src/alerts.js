import React, {useEffect, useRef, useState} from 'react';

function App(){
    // Start with an unauthenticated client, then request a token ASAP
    const client = useRef(getClient());
    useEffect(() => {
        const client = getClient();
        getToken(client).then(token => {
            clientRef.current._transport._auth.header = {access_token: token};

            client.current.find('plots/trends/series', {
                fields: JSON.stringify(selectedDataTypes),
                filter: selectedFilter,
                outliers: outlier
            })
        })
    }, []);

}

ReactDOM.render(
    <App/>,
    document.getElementById('react')
);
