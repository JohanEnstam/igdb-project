import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    console.log("Logout API route called");

    // Get the backend API URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

    // Get cookies from the request
    const cookies = request.headers.get("cookie") || "";
    console.log("Forwarding cookies:", cookies);

    // Forward the logout request to the backend
    const response = await fetch(`${backendUrl}/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Forward cookies for session-based auth
        "Cookie": cookies,
      },
      credentials: "include",
    });

    console.log("Backend logout response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error("Backend logout failed:", errorData);
      return NextResponse.json(
        { detail: errorData.detail || "Logout failed" },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log("Backend logout success:", data);

    // Create response with cleared cookies
    const nextResponse = NextResponse.json(data);

    // Clear session cookies by setting them to expire
    nextResponse.cookies.set("session", "", {
      expires: new Date(0),
      path: "/",
      httpOnly: true,
      secure: false, // Set to true in production with HTTPS
      sameSite: "lax"
    });

    return nextResponse;
  } catch (error) {
    console.error("Logout API error:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
