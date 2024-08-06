import { PUBLIC_REDDIT_PASSWORD } from "$env/static/public";
import { PUBLIC_REDDIT_USERNAME } from "$env/static/public";
import { PUBLIC_USER_AGENT } from "$env/static/public";

const clientId = PUBLIC_REDDIT_USERNAME; // client ID
const clientSecret = PUBLIC_REDDIT_PASSWORD; // Client secret
export const userAgent = PUBLIC_USER_AGENT; // name
let accessToken: string | null = null;
let tokenExpiry: number | null = null;

// Function to authenticate and get the access token
export async function authenticate() {
  if (accessToken && tokenExpiry && Date.now() < tokenExpiry) {
    return accessToken;
  }

  try {
    console.log("Authenticating");
    const response = await fetch("https://www.reddit.com/api/v1/access_token", {
      method: "POST",
      headers: {
        Authorization: "Basic " + btoa(`${clientId}:${clientSecret}`),
        "User-Agent": userAgent,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ grant_type: "client_credentials" }),
    });

    if (!response.ok) {
      throw new Error(`Failed to authenticate: ${response.statusText}`);
    }

    const data = await response.json();
    accessToken = data.access_token;
    tokenExpiry = Date.now() + data.expires_in * 1000; // Reddit token expiry is in seconds

    console.log("Authenticated using token:", accessToken);
    return accessToken;
  } catch (error) {
    console.error("Error during authentication:", error);
    throw new Error("Failed to authenticate");
  }
}
