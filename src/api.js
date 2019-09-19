import axios from 'axios';

export default class MegaQcApi {
    constructor() {
        this.tokenPromise = axios.get('/api/get_token',)
            .then(response => {
                this.token = response.data.token;
            });
    }

    /**
     * Returns a promise that will only resolve once we have the API token
     */
    getToken() {
        if (this.token)
            return Promise.resolve(this.token);
        else
            return this.tokenPromise;
    }

    makeRequest(config) {
        return this.getToken()
            .then(() => {
                const finalConfig = Object.assign(config, {
                    headers: {
                        access_token: this.token
                    }
                });
                return axios.request(finalConfig)
            })
            .then(response => response.data);

    }

    getDataTypes() {
        return this.makeRequest({url: '/api/get_data_types'})
    }

    getFilterData() {
        return this.makeRequest({url: '/api/get_filters'}).then(response => response.data)
    }

    getTrendData(fields, filters) {
        return this.makeRequest({
            url: '/api/get_trend_data',
            method: 'POST',
            data: {
                fields: fields,
                filters: {filters_id: filters}
            }
        }).then(response => response.data)
    }

    reportFilterFields(data) {
        return this.makeRequest({
            url: '/api/report_filter_fields',
            method: 'post',
            data: data,
            responseType: 'json',
        })
    }
}
