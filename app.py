from flask import Flask, request, Response, jsonify, stream_with_context
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store the target URL
TARGET_URL = "https://rnxqv-172-183-152-26.a.free.pinggy.link"  # Default URL

@app.route('/set_url', methods=['POST'])
def set_url():
    """Update the target URL dynamically."""
    global TARGET_URL
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    TARGET_URL = data['url']
    return jsonify({"message": f"Target URL updated to {TARGET_URL}"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    """Return the currently saved target URL."""
    return jsonify({"current_target_url": TARGET_URL}), 200

@app.route('/proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Forward requests to the target URL and support streaming."""
    if not TARGET_URL:
        return jsonify({"error": "Target URL is not set"}), 500

    try:
        # Build the full URL to forward the request
        full_url = f"{TARGET_URL}/{path}"

        # Forward the request using streaming
        upstream_response = requests.request(
            method=request.method,
            url=full_url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            stream=True  # Enable streaming mode
        )

        # Stream response from upstream to client
        def generate():
            for chunk in upstream_response.iter_content(chunk_size=8192):  # Stream data in chunks
                if chunk:
                    yield chunk

        return Response(stream_with_context(generate()), status=upstream_response.status_code, headers=dict(upstream_response.headers))

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
