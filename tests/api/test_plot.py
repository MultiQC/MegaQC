from flask import url_for
from plotly.offline import plot
import json

import megaqc.user.models as user_models
from megaqc.model import models


class TestPlotApi:
    @staticmethod
    def test_get_trend_series(mix, db, client):
        # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
        data_type = mix.blend(models.SampleDataType, data_key='test_field')
        report = mix.cycle(5).blend(
            models.Report,
            created_at=lambda: mix.faker.date_time(),
            user=mix.blend(user_models.User),
            samples=lambda: mix.blend(
                models.Sample,
                data=lambda: mix.cycle(1).blend(models.SampleData, data_type=data_type,
                                                value=mix.faker.small_positive_integer)
            )

        )
        db.session.add_all([
            data_type,
            *report
        ])

        response = client.get(url_for('rest_api.trend_data', filter=json.dumps([]), fields=json.dumps(['test_field'])))

        # Check the request was successful
        assert response.status_code == 200

        # Check that there are 3 series (mean, stdev, raw data)
        assert len(response.json) == 3

        # Test that this is valid plot data
        plot({'data': response.json}, validate=True, auto_open=False)


