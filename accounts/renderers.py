from rest_framework.renderers import JSONRenderer
import json

class UserRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = {}

        if isinstance(data, dict) and "ErrorDetail" in str(data):
            response = {"errors": data}
        else:
            response = data

        return json.dumps(response)
