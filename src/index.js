export default {
	async fetch(request, env) {
		const url = new URL(request.url);
		const key = url.pathname.slice(1);

		// Retrieve the secret key from environment variables
		const privateKey = env.PRIVATE_KEY;
		const authKey = request.headers.get("Auth-Key");
		const source = request.headers.get("Source");
		const version = request.headers.get("Version");


		const userAgent = request.headers.get("User-Agent") || "";
		const isBot = /bot|crawl|spider|slurp|mediapartners/i.test(userAgent);

		if (isBot) {
			return new Response("Bot requests are not allowed", { status: 403 });
		}

		// Check if the required headers for authorized app requests are present
		const isAuthorizedRequest = authKey === privateKey && source && version;
		const isPropertlyFormattedRequest = source && version;

		// later we will add logging for version and source so we can see how many requests are coming from each version and source so we can offer better support
		// source may also be used to scale the return data based on the source, for example, if the source is a mobile app, we may return a smaller image or less data


		if (!isPropertlyFormattedRequest) {
			return new Response("This API is not meant to be accessed from a browser.", {
				status: 403,
				headers: { "Content-Type": "text/plain" },
			});
		}


		switch (request.method) {
			case "PUT":
				if (!isAuthorizedRequest) {
					return new Response("Unauthorized", { status: 401 });
				}
				await env.MY_BUCKET.put(key, request.body);
				return new Response(`Put ${key} successfully!`, {
					headers: { "X-Custom-Message": "Object stored securely" },
					// we could fit a ton more data in here, but we will keep it simple for now
				});

			case "GET":
				// GET requests are allowed for all requests, authorized or not
				const object = await env.MY_BUCKET.get(key);
				if (object === null) {
					return new Response("Object Not Found", { status: 404 });
				}

				// Add metadata headers to the response
				const headers = new Headers();
				object.writeHttpMetadata(headers);
				headers.set("etag", object.httpEtag);

				return new Response(object.body, { headers });

			case "DELETE":
				if (!isAuthorizedRequest) {
					return new Response("Unauthorized", { status: 401 });
				}
				await env.MY_BUCKET.delete(key);
				return new Response("Deleted!", {
					headers: { "X-Custom-Message": "Object deleted securely" },
					// we could fit a ton more data in here, but we will keep it simple for now
				});

			default:
				// Restrict access to methods other than GET, PUT, and DELETE
				return new Response("Method Not Allowed", {
					status: 405,
					headers: {
						Allow: "PUT, GET, DELETE",
					},
				});
		}
	},
};
