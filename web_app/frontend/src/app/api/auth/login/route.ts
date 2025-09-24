import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // Get the backend API URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

    // Redirect to backend OAuth login endpoint
    return NextResponse.redirect(`${backendUrl}/login`);
  } catch (error) {
    console.error("Auth login redirect error:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
