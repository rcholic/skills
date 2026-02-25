---
name: post-job
description: Post free job ads to 20+ job boards such as LinkedIn, Indeed, Ziprecruiter etc. to receive applicant resumes via email.
---

# JobPoster Skill

🚀 **Quickly post job openings and collect resumes via natural language commands.**

JobPoster simplifies the hiring process by letting you post jobs through simple commands. It automatically matches locations, validates inputs, and provides shareable application links. Perfect for recruiters, hiring managers, and HR teams.

## ✨ Features

- **Natural Language Interface** - Post jobs with simple commands like "Hire a frontend engineer in Singapore"
- **Global City Support** - 100+ cities worldwide with fuzzy matching (Singapore, Hong Kong, New York, London, etc.)
- **AI Job Description** - Optional AI-powered JD generation for professional, compelling postings
- **Instant Application Links** - Get shareable URLs for candidates to apply directly
- **Resume Collection** - All applications sent to your specified email
- **LinkedIn Sync** - Automatic LinkedIn job posting integration

## 🎯 When to Use

Use this skill when you need to:

- Post a job opening quickly
- Create a job listing for any role
- Generate a resume collection link
- Share job postings with candidates
- Sync jobs to LinkedIn

## 🛠️ Tools

### post_job

Main tool for posting job openings.

#### Parameters

| Parameter     | Required | Type   | Description                              | Example                          |
| ------------- | -------- | ------ | ---------------------------------------- | -------------------------------- |
| `title`       | ✅ Yes   | string | Job title (min 4 characters)             | `"Senior Frontend Engineer"`     |
| `city_query`  | ✅ Yes   | string | City/location (supports fuzzy match)     | `"Singapore"`, `"NYC"`           |
| `description` | ✅ Yes   | string | Job description (min 100 characters)     | `"5+ years React experience..."` |
| `email`       | ✅ Yes   | string | Email to receive resumes                 | `"hr@company.com"`               |
| `company`     | ❌ No    | string | Company name (default: `"Your Company"`) | `"TechCorp"`                     |
| `industry`    | ❌ No    | string | Industry/field (default: `"General"`)    | `"Technology"`, `"Finance"`      |

#### Validation Rules

- **Title**: Minimum 4 characters
- **Email**: Must be valid email format
- **Description**: Minimum 100 characters (ensure meaningful job details)
- **City**: Must match a supported location (see Assets)

#### Response Format

On success, returns:

```
 `✅ **Job Posted Successfully!**\n\n` +
      `**Position:** ${title}\n` +
      `**Location:** ${matched.label}\n` +
      `**Job ID:** \`${jobId}\`\n` +
      `**The resume will be sent to:** ${email}\n\n` +
      `--- \n` +
      `**LinkedIn Sync:** ⏳ Processing in background (10-20 min). I'll check and notify you when ready!\n\n` +
      `You can also manually check with: \`check_linkedin_status\` using Job ID \`${jobId}\``
```

### check_linkedin_status

Check the status of a job's LinkedIn synchronization. Use this tool if the LinkedIn URL was not available immediately after posting.

#### Parameters

| Parameter | Required | Type   | Description                | Example      |
| --------- | -------- | ------ | -------------------------- | ------------ |
| `jobId`   | ✅ Yes   | string | The ID of the job to check | `"abcd2345"` |

#### Response Format

Returns either the LinkedIn URL (if sync complete) or a "Pending" status message.

### check_linkedin_status_auto

Auto-check LinkedIn status with polling until URL is available. Checks every 1 minute until LinkedIn URL is returned or max attempts reached.

#### Parameters

| Parameter     | Required | Type   | Description                             | Example      |
| ------------- | -------- | ------ | --------------------------------------- | ------------ |
| `jobId`       | ✅ Yes   | string | The ID of the job to check              | `"abcd2345"` |
| `intervalMs`  | ❌ No    | number | Polling interval in ms (default: 60000) | `60000`      |
| `maxAttempts` | ❌ No    | number | Maximum attempts (default: 20)          | `20`         |

#### Response Format

Returns the LinkedIn URL when available, or a timeout message after max attempts.

## 🤖 AI Assistant Workflow

### ⭐ Recommended: Auto-Notify with Background Monitor

**After calling `post_job`, spawn a background sub-agent to monitor and notify:**

```
User: "Post a health manager job in Shanghai"

AI: [Calls post_job]
    → Returns: Job ID `abc123`

AI: [Spawns sub-agent with monitor_linkedin.js]
    → "✅ Job posted! I'll notify you when LinkedIn sync is complete."

[Background monitor polls every 2 minutes]

[When LinkedIn URL is ready]
AI: "🎉 LinkedIn sync complete! Job ID: `abc123`, LinkedIn URL: https://linkedin.com/jobs/view/..."
```

**Spawn the monitor sub-agent like this:**

```javascript
// After post_job succeeds and returns jobId:
// Validate jobId format before passing to sub-agent (alphanumeric + hyphen only)
const safeJobId = jobId.match(/^[a-zA-Z0-9-]+$/) ? jobId : null;
if (!safeJobId) throw new Error("Invalid jobId format");

await sessions_spawn({
  task: `Monitor LinkedIn sync for jobId: ${safeJobId}. Run: node scripts/monitor_linkedin.js --jobId "${safeJobId}" --channel "webchat". Notify me when complete.`,
  mode: "run",
  cleanup: "delete",
});
```

This ensures **proactive notification** without blocking the main session.

---

### Alternative: Manual Polling

If you prefer not to spawn a sub-agent:

1. **Save the Job ID** from the response
2. **Wait 5-10 minutes** (LinkedIn sync takes time)
3. **Call `check_linkedin_status`** with the Job ID
4. **If still pending:** Check again every 3-5 minutes
5. **When LinkedIn URL is ready:** Proactively notify the user

### Example Flow

```
User: "Post a frontend engineer job in Singapore"

AI: [Calls post_job]
    → Returns: Job ID `abc123`, Apply URL

AI: "✅ Job posted! LinkedIn sync in progress..."

[AI waits 5 minutes, then checks]

AI: [Calls check_linkedin_status with jobId: abc123]
    → Returns: LinkedIn URL

AI: "🎉 LinkedIn sync complete! URL: https://linkedin.com/jobs/view/..."
```

### Proactive Check Script (for AI)

```javascript
// After post_job returns a Job ID:
const jobId = response.jobId;

// Wait 5 minutes
await sleep(300000);

// Check LinkedIn status
const result = await check_linkedin_status({ jobId });

// If still pending, check every 3-5 minutes
// When URL is available, notify user immediately
```

### Supported Locations

The skill includes a built-in location database (`assets/locations.json`) with 100+ cities:

**Asia Pacific:** Singapore, Hong Kong, Beijing, Shanghai, Tokyo, Sydney, Mumbai, Bangkok, Seoul, Taipei

**North America:** New York, San Francisco, Los Angeles, Seattle, Chicago, Toronto, Vancouver

**Europe:** London, Berlin, Paris, Amsterdam, Dublin, Zurich, Stockholm

**Middle East:** Dubai, Abu Dhabi, Riyadh, Tel Aviv

See `assets/locations.json` for the complete list. Fuzzy matching supports variations like "NYC" → "New York".

## 📦 Installation

### Install via ClawHub

```bash
clawhub install job-poster
```

### Manual Installation

```bash
# Clone or download the skill
cd your-openclaw-workspace/skills

# Install dependencies
cd job-poster
npm install
```

## 🔐 Security Notes

- **Email Privacy**: Resume emails are visible in job postings - use a dedicated hiring email
- **Rate Limiting**: API may have rate limits for high-volume posting

## 🐛 Troubleshooting

### Issue: Job posts but no confirmation

**Cause**: Response timeout or network issue

**Solution**: Check backend logs, verify API credentials, retry with `--force`

### Issue: City not recognized

**Cause**: City not in location database

**Solution**:

1. Check `assets/locations.json` for supported cities
2. Try alternative spelling (e.g., "New York" vs "NYC")
3. Add new city to database and republish

### Issue: Duplicate job postings

**Cause**: Multiple API calls due to retry logic

**Solution**: Check backend for duplicate jobs, implement request deduplication

## 📝 Changelog

### v1.0.0 (Initial Release)

- Core job posting functionality
- 100+ city support with fuzzy matching
- Email validation
- LinkedIn sync integration
- Error handling and validation

## 🤝 Contributing

Found a bug or want to add more cities?

1. Fork the skill
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This skill is provided as-is for use with OpenClaw.

## 🆘 Support

For issues or questions:

- Check this SKILL.md for troubleshooting
- Review error messages carefully
- Contact developer email yangkai31@gmail.com if you run into any issues

---

**Happy Hiring! 🎉**
