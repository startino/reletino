const clientId = "GK6LMyd6RhaqB1q8OW0-0Q"; // client ID
const clientSecret = "Sy3uTNE4nNnBKjmz4Ab2Zta9Ss7yFg"; // Client secret

export const userAgent = "biwas"; // name
export let accessToken: string | null = null;
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
