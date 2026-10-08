function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data = JSON.parse((e.postData && e.postData.contents) || "{}");

    let fileUrl = "";
    let fileName = data.reference_file || "";

    // Save the customer's PDF/Excel/etc. into Google Drive.
    if (data.reference_file_base64 && data.reference_file) {
      const bytes = Utilities.base64Decode(data.reference_file_base64);
      const blob = Utilities.newBlob(
        bytes,
        data.reference_file_mime || "application/octet-stream",
        data.reference_file
      );

      const folder = getOrCreateFolder_("TipsR Pro Customer Files");
      const file = folder.createFile(blob);
      fileName = file.getName();

      try {
        file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      } catch (shareError) {
        // Workspace accounts may block public sharing; the file still remains in Drive.
      }

      fileUrl = file.getUrl();
    }

    // Write by HEADER NAME, not by fixed column number.
    // This prevents Budget/Details/Reference File from going into the wrong columns.
    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const row = new Array(headers.length).fill("");

    const values = {
      "date & time": new Date(),
      "timestamp": new Date(),
      "name": data.name || "",
      "mobile": data.mobile || "",
      "mobile number": data.mobile || "",
      "email": data.email || "",
      "query": data.query || "",
      "message": data.query || "",
      "tell us about your work": data.query || "",
      "work details": data.query || "",
      "type": data.type || "Inquiry",
      "what do you need?": data.type || "Inquiry",
      "service": data.type || "Inquiry",
      "budget": data.budget || "",
      "reference file": fileName,
      "reference file url": fileUrl,
      "file url": fileUrl,
      "ai summary": data.ai_summary || "",
      "status": data.status || "New"
    };

    headers.forEach(function(header, index) {
      const key = String(header).trim().toLowerCase();
      if (Object.prototype.hasOwnProperty.call(values, key)) {
        row[index] = values[key];
      }
    });

    // If the sheet is completely empty, create the standard headers.
    if (headers.length === 0 || headers.every(h => String(h).trim() === "")) {
      const standard = [
        "Date & Time", "Name", "Mobile", "Email", "What do you need?",
        "Tell us about your work", "Budget", "Reference File",
        "Reference File URL", "AI Summary", "Status"
      ];
      sheet.getRange(1, 1, 1, standard.length).setValues([standard]);

      const standardValues = [
        new Date(), data.name || "", data.mobile || "", data.email || "",
        data.type || "Inquiry", data.query || "", data.budget || "",
        fileName, fileUrl, data.ai_summary || "", data.status || "New"
      ];
      sheet.getRange(2, 1, 1, standardValues.length).setValues([standardValues]);
    } else {
      sheet.appendRow(row);
    }

    return json_({success: true, fileUrl: fileUrl});
  } catch (error) {
    return json_({success: false, error: String(error)});
  }
}

function getOrCreateFolder_(name) {
  const folders = DriveApp.getFoldersByName(name);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(name);
}

function doGet() {
  return ContentService
    .createTextOutput("TipsR Pro Google Sheet API is working.")
    .setMimeType(ContentService.MimeType.TEXT);
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
