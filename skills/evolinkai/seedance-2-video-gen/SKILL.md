---
name: seedance-2-video-gen
description: >
  Generate AI videos from text prompts or reference images.  
  Supports text-to-video, image-to-video with customizable duration,
  resolution, and aspect ratio. Use when user wants to create,
  generate, or make AI videos, mentions Seedance, or requests
  video generation from text descriptions or images.
metadata:
  openclaw:
    requires:
      env:
        - name: EVOLINK_API_KEY
          description: "EvoLink API key from https://evolink.ai/dashboard"
          required: true
      bins:
        - jq
        - curl
---

# Seedance Video Generation

An interactive AI video generation assistant powered by the Seedance model via EvoLink API.

## Core Principles

1. **Guide, don't decide** — Never make choices for the user. Your role is to present options and let the user decide.
2. **Never write prompts for the user** — Help them understand what makes a good prompt, but the creative vision is theirs.
3. **Smart context awareness** — Recognize what the user has already provided and only ask about missing pieces.
4. **Intent first** — If the user's intent is unclear, confirm what they want before proceeding.

## Flow

### Step 1: Check for API Key

If the user hasn't provided an API key or set `EVOLINK_API_KEY`:

- Tell them they need an EvoLink API Key
- Guide them to register at https://evolink.ai and get a key from the dashboard
- Once they provide a key, proceed to Step 2

If the key is already set or provided, skip directly to Step 2.

### Step 2: Understand Intent

Assess what the user wants based on their message:

- **Intent is clear** (e.g., "generate a video of a cat dancing") → Go to Step 3
- **Intent is ambiguous** (e.g., "I want to try Seedance") → Ask what they'd like to do: generate a new video, learn about model capabilities, etc.

### Step 3: Gather Missing Information

Check what the user has already provided and **only ask about what's missing**:

| Parameter | What to tell the user | Required? |
|-----------|----------------------|-----------|
| **Video content** (prompt) | Ask them to describe what they want to see. Don't write it for them. | Yes |
| **Duration** | Supported: **4–12 seconds**. Ask how long they want. | Yes |
| **Resolution** | Supported: **480p** / **720p** / **1080p**. Ask their preference. | Yes |
| **Audio** | The model can auto-generate **voice, sound effects, and background music** matching the video. Ask if they want audio enabled. | Yes |
| **Aspect ratio** | Supported: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9. Only mention if relevant or if user asks. | Optional |
| **Reference images** | Supported: up to 9 images (JPEG/PNG/WebP, ≤30MB each). Only mention if relevant. | Optional |

**Smart gathering rules:**
- User gives everything at once → Confirm and generate immediately
- User gives partial info → Only ask about the missing pieces
- User says "I want to generate a video" with no details → Guide from the beginning

### Step 4: Generate

Once all required information is confirmed:

1. Run the generation script with the user's exact specifications
2. Show progress (generation typically takes 30–120 seconds)
3. Return the video URL (valid for 24 hours)

## Script Usage

```bash
# Set API key
export EVOLINK_API_KEY=your_key_here

# Basic text-to-video
./scripts/seedance-gen.sh "user's prompt" --duration 5 --quality 720p

# With audio disabled
./scripts/seedance-gen.sh "user's prompt" --duration 8 --quality 1080p --no-audio

# With reference image
./scripts/seedance-gen.sh "user's prompt" --image "https://example.com/ref.jpg" --duration 6 --quality 720p

# Custom aspect ratio
./scripts/seedance-gen.sh "user's prompt" --aspect-ratio 9:16 --duration 4 --quality 480p
```

## Error Handling

Provide friendly, actionable messages:

| Error | What to tell the user |
|-------|----------------------|
| Invalid/missing key (401) | "Your API key doesn't seem to work. You can check it at https://evolink.ai/dashboard" |
| Insufficient balance (402) | "Your account balance is low. You can add credits at https://evolink.ai/dashboard" |
| Rate limited (429) | "Too many requests — let's wait a moment and try again" |
| Content blocked (400) | "This prompt was flagged (realistic human faces are restricted). Try adjusting the description" |
| Service unavailable (503) | "The service is temporarily busy. Let's try again in a minute" |

## Model Capabilities Summary

Use this when the user asks what the model can do:

- **Text-to-video**: Describe a scene, get a video
- **Image-to-video**: Provide reference images to guide the output
- **Audio generation**: Auto-generates synchronized voice, sound effects, and background music
- **Duration**: 4–12 seconds
- **Resolution**: 480p, 720p, 1080p
- **Aspect ratios**: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9
- **Limitation**: Realistic human faces are restricted

## References

- `references/api-params.md`: Complete API parameter reference
- `scripts/seedance-gen.sh`: Generation script with automatic polling and error handling
