import type { Metadata } from "next";

const baseUrl = "https://better-py.nesalia.com";

export function createMetadata(override: Metadata): Metadata {
  return {
    ...override,
    openGraph: {
      type: "website",
      siteName: "better-py",
      ...override.openGraph,
    },
    twitter: {
      card: "summary_large_image",
      creator: "@nesalia_inc",
      ...override.twitter,
    },
  };
}

export { baseUrl };
