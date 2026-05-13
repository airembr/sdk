Understood. Here's the revised version of the **ICAL Bridge Guide** in proper documentation format, without emojis or informal elements:

---

# ICAL Bridge Guide

This guide explains how to obtain a private ICAL file from Google Calendar and how to fill in the ICAL Bridge integration form.

---

## 1. Obtaining a Private ICAL URL from Google Calendar

To integrate Google Calendar with the ICAL Bridge, you need the private ICAL URL of your calendar.

### Steps:

1. **Open Google Calendar**
   Visit [https://calendar.google.com](https://calendar.google.com) and log in with your Google account.

2. **Access Calendar Settings**
   In the left-hand panel, under "My calendars", hover over the calendar you wish to export. Click the three-dot menu icon and select "Settings and sharing".

3. **Locate the Secret ICAL URL**
   Scroll down to the section titled "Integrate calendar".
   Find the entry labeled "Secret address in iCal format".

4. **Copy the URL**
   Click "Copy" next to the "Secret address in iCal format". This is the private ICAL URL that provides read-only access to the calendar.

**Note**: The secret ICAL URL grants full read access to your calendar data. Do not share it publicly.

---

## 2. Filling Out the ICAL Bridge Form

Each field in the form corresponds to metadata or configuration required to enable the ICAL integration.

### Event Source Description

* **Event source name**
  Provide a descriptive name that uniquely identifies this calendar source.
  Example: __Engineering Team Calendar__, __Maintenance Schedule__, __John Doe Personal__

* **Event source channel** (optional)
  Specify the logical channel or category for grouping this source.
  Example: __web__, __mobile__, __calendar-sync__, __machine-1__

* **Event source description** (optional)
  Add a more detailed explanation of the source's purpose or content.
  Example: __This calendar contains the on-call rotation for the backend team.__

### Event Source Access

* **Enabled checkbox**
  Check this box to enable the calendar source. If unchecked, the source will be inactive and its data will not be processed.

### ICAL Configuration

* **ICAL URL**
  Paste the private ICAL URL obtained from Google Calendar. This should be a full URL beginning with __https://__ and ending in __.ics__.

  Example:
  __https://calendar.google.com/calendar/ical/example%40gmail.com/private-123abc456/basic.ics__

---

After filling out all required fields, submit the form to activate the ICAL Bridge connection. The system will begin pulling events from the specified calendar URL.

For troubleshooting, ensure that:

* The ICAL URL is valid and accessible.
* The calendar is not restricted or deleted.
* The checkbox to enable the source is selected.
