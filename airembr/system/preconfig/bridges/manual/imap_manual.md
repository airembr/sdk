# IMAP Server Bridge Guide

The **IMAP Server Bridge** lets the System fetch emails from a mailbox at regular intervals. 
Each email is collected as an observation and stored in the system for processing.

This is useful for:

* Monitoring support or feedback inboxes
* Triggering workflows based on incoming emails
* Collecting structured data from automated messages

---

## How It Works

1. System connects to your email inbox using IMAP.
2. It fetches new emails every X minutes.
3. Each email is saved as an observation in system database.

---

## How to Set It Up

Go to **Source → Event Redirects** and select **IMAP Server Bridge** to create a new email-based event source.

### 1. Basic Info

* **Name**: A label for this source (e.g., **Support Inbox**)
* **Channel** *(optional)*: Where the data comes from (e.g., **email**)
* **Description** *(optional)*: Notes about the source (e.g., **Collects emails from support inbox**)
* **Enabled**: Check this box to activate the source

### 2. IMAP Configuration

* **IMAP Server**: The domain of your IMAP server (e.g., **imap.gmail.com**)
* **Email Account**: The full email address (e.g., **support@yourdomain.com**)
* **Email Password**: The password for the email account
* **Fetch Interval (minutes)**: How often System checks for new emails (e.g., **5** for every 5 minutes)

> **Note**: Make sure the email account supports IMAP and that credentials are valid.
