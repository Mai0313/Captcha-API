from flask import Flask, jsonify, request
from omegaconf import OmegaConf

from captcha_resolver import CaptchaResolver

whitelist = OmegaConf.load("whitelist.yaml")

app = Flask(__name__)


@app.route("/get_captcha_code", methods=["POST"])
def get_captcha_code_api():
    api_key = request.headers.get("X-API-Key")
    if api_key not in whitelist.allowed_api:
        response = jsonify(
            {
                "result": "錯誤",
                "message": f"你沒有權限使用此 API, 請與管理員聯繫並提供以下代碼: {api_key}",
            }
        )
        response.status_code = 403
        return response

    captcha_base64 = request.json.get("captcha_base64")
    resolver = CaptchaResolver()
    result = resolver.get_captcha_code(captcha_base64)
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)
