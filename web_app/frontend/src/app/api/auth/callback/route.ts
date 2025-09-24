import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // Get the backend API URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

    // Forward the OAuth callback to the backend with all query parameters
    const url = new URL(request.url);
    const backendCallbackUrl = `${backendUrl}/auth/callback${url.search}`;

    // Redirect to backend OAuth callback
    return NextResponse.redirect(backendCallbackUrl);
  } catch (error) {
    console.error("Auth callback error:", error);
    return NextResponse.redirect(new URL("/admin?error=server_error", request.url));
  }
}
