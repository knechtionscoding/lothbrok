from flask import Flask, request, Response
import json
import lothbrok

app = Flask(__name__)

# Ability to accept artifactory webhooks
# Example json
"""
{
   "repo_key":"docker-remote-cache",
   "path":"library/ubuntu/latest/list.manifest.json",
   "name":"list.manifest.json",
   "sha256":"35c4a2c15539c6c1e4e5fa4e554dac323ad0107d8eb5c582d6ff386b383b7dce",
   "size":1206,
   "image_name":"library/ubuntu",
   "tag":"latest",
   "platforms":[
      {
         "architecture":"amd64",
         "os":"linux"
      },
      {
         "architecture":"arm",
         "os":"linux"
      },
      {
         "architecture":"arm64",
         "os":"linux"
      },
      {
         "architecture":"ppc64le",
         "os":"linux"
      },
      {
         "architecture":"s390x",
         "os":"linux"
    }
  ]
}
"""


@app.route("/webhook/artifactory", methods=["POST"])
def respond():
    data = json.load(request.json)
    lothbrok.processor(data.image_name)
    print(request.json)
    return Response(status=200)
