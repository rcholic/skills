---
name: snaprender
description: Give your agent eyes on the web. See any website visually, analyze layouts, compare devices, monitor pages for changes, and generate visual reports.
metadata: {"openclaw": {"requires": {"bins": ["curl"], "env": ["SNAPRENDER_API_KEY"]}}}
---

# SnapRender: Give Your Agent Eyes on the Web

You can see any website. When the user asks you to look at a page, check how something looks, compare layouts, inspect a design, monitor a page, or do any kind of visual web analysis, use SnapRender to capture what the page looks like and then analyze it with your vision capabilities.

## How to Capture

Use bash with curl:

```bash
curl -s "https://app.snap-render.com/v1/screenshot?url=URL&response_type=json&block_ads=true&block_cookie_banners=true" \
  -H "X-API-Key: $SNAPRENDER_API_KEY"
```

Replace URL with the target (must include https://).

The response is JSON with an `image` field containing a base64 data URI. Pass this image to your vision capabilities to see and analyze the page.

## Parameters

| Parameter | Values | Default | What it does |
|-----------|--------|---------|--------------|
| url | Any public URL | required | The page to look at |
| format | png, jpeg, webp, pdf | png | Output format |
| device | iphone_14, iphone_15_pro, pixel_7, ipad_pro, macbook_pro | desktop | See the page as a specific device |
| dark_mode | true, false | false | See the dark mode version |
| full_page | true, false | false | See the entire scrollable page |
| block_ads | true, false | true | Remove ads for a clean view |
| block_cookie_banners | true, false | true | Remove cookie popups |
| response_type | json | json | Always use json |
| width | 320-3840 | 1280 | Viewport width |
| height | 200-10000 | 800 | Viewport height |
| quality | 1-100 | 90 | Image quality (JPEG/WebP) |
| delay | 0-10000 | 0 | Wait after page load (ms) |

## What you can do

- **Look at any website**: "What does stripe.com look like?" "Show me the homepage of competitor.com"
- **Check mobile layouts**: Use device=iphone_15_pro or device=pixel_7 to see how a page looks on phones
- **Compare devices**: Make separate calls for desktop and mobile, then compare the layouts
- **Compare dark and light mode**: Capture with dark_mode=true and dark_mode=false
- **Inspect full pages**: Use full_page=true to see everything below the fold
- **Visual QA**: Check if a page looks broken, if elements are misaligned, if text is readable
- **Monitor changes**: Capture a page, describe what you see, compare to previous observations
- **Analyze designs**: Look at how competitors structure their pages, pricing, layouts

## Instructions

1. Always use `response_type=json` to get the image as base64 for visual analysis.
2. After receiving the screenshot, look at the image carefully and describe what you see in detail.
3. For comparisons, make separate API calls and analyze each image.
4. Ads and cookie banners are blocked by default so you see the actual content.

## Getting an API Key

Sign up free at https://app.snap-render.com/auth/signup (50 free screenshots/month, no credit card).
