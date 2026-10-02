export default {
  async fetch(request, env) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return json({ success: false, error: "POST required" }, 405, corsHeaders);
    }

    try {
      const form = await request.formData();
      const file = form.get("file");
      const sessionId = form.get("session_id");

      if (!file || typeof file === "string") {
        return json({ success: false, error: "Image file is required" }, 400, corsHeaders);
      }

      if (!sessionId || typeof sessionId !== "string") {
        return json({ success: false, error: "session_id is required" }, 400, corsHeaders);
      }

      if (!env.CLOUDINARY_CLOUD_NAME || !env.CLOUDINARY_API_KEY || !env.CLOUDINARY_API_SECRET) {
        return json({ success: false, error: "Cloudinary Worker secrets are not configured" }, 500, corsHeaders);
      }

      if (!file.type || !file.type.startsWith("image/")) {
        return json({ success: false, error: "Only image files are accepted" }, 400, corsHeaders);
      }

      const timestamp = Math.floor(Date.now() / 1000);
      const folder = `nexora/${sessionId}`;

      // Cloudinary signed-upload signature:
      // alphabetically sorted parameters + API secret, SHA-1.
      const signatureBase = `folder=${folder}&timestamp=${timestamp}${env.CLOUDINARY_API_SECRET}`;
      const digest = await crypto.subtle.digest(
        "SHA-1",
        new TextEncoder().encode(signatureBase)
      );
      const signature = [...new Uint8Array(digest)]
        .map(byte => byte.toString(16).padStart(2, "0"))
        .join("");

      const uploadForm = new FormData();
      uploadForm.append("file", file, file.name || "image");
      uploadForm.append("api_key", env.CLOUDINARY_API_KEY);
      uploadForm.append("timestamp", String(timestamp));
      uploadForm.append("folder", folder);
      uploadForm.append("signature", signature);

      const cloudinaryResponse = await fetch(
        `https://api.cloudinary.com/v1_1/${env.CLOUDINARY_CLOUD_NAME}/image/upload`,
        {
          method: "POST",
          body: uploadForm
        }
      );

      const cloudinaryText = await cloudinaryResponse.text();
      let cloudinaryResult;

      try {
        cloudinaryResult = JSON.parse(cloudinaryText);
      } catch {
        return json({
          success: false,
          error: "Cloudinary returned a non-JSON response",
          status: cloudinaryResponse.status,
          details: cloudinaryText
        }, 502, corsHeaders);
      }

      if (!cloudinaryResponse.ok) {
        return json({
          success: false,
          error: "Cloudinary upload failed",
          status: cloudinaryResponse.status,
          details: cloudinaryResult.error?.message || cloudinaryText
        }, 502, corsHeaders);
      }

      return json({
        success: true,
        session_id: sessionId,
        secure_url: cloudinaryResult.secure_url,
        public_id: cloudinaryResult.public_id,
        folder: cloudinaryResult.asset_folder || folder
      }, 200, corsHeaders);

    } catch (error) {
      return json({
        success: false,
        error: error.message || "Unexpected Worker error"
      }, 500, corsHeaders);
    }
  }
};

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders
    }
  });
}
