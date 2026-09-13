document.addEventListener("DOMContentLoaded", () => {
    // Mode Switching
    const btnRecordMode = document.getElementById("btn-mode-record");
    const btnUploadMode = document.getElementById("btn-mode-upload");
    const sectionRecord = document.getElementById("section-record");
    const sectionUpload = document.getElementById("section-upload");

    btnRecordMode.addEventListener("click", () => {
        btnRecordMode.classList.add("active");
        btnUploadMode.classList.remove("active");
        sectionRecord.classList.add("active");
        sectionRecord.classList.remove("hidden");
        sectionUpload.classList.add("hidden");
        sectionUpload.classList.remove("active");
    });

    btnUploadMode.addEventListener("click", () => {
        btnUploadMode.classList.add("active");
        btnRecordMode.classList.remove("active");
        sectionUpload.classList.add("active");
        sectionUpload.classList.remove("hidden");
        sectionRecord.classList.add("hidden");
        sectionRecord.classList.remove("active");
    });

    // Handle Upload Section
    const fileInput = document.getElementById("file-input");
    const btnBrowse = document.getElementById("btn-browse-files");
    const selectedFileInfo = document.getElementById("selected-file-info");
    const fileNameDisplay = document.getElementById("file-name");
    const btnSubmitUpload = document.getElementById("btn-submit-upload");

    btnBrowse.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            selectedFileInfo.classList.remove("hidden");
        }
    });

    btnSubmitUpload.addEventListener("click", async () => {
        if (fileInput.files.length === 0) return showNotification("No file selected", true);
        await uploadFile(fileInput.files[0]);
    });

    // Handle Upload Logic
    async function uploadFile(file) {
        showNotification("Uploading and summarizing... This may take a minute.");
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("/upload-audio", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "meeting_summary.pdf";
                a.click();
                showNotification("Success! Summary downloaded.");
            } else {
                showNotification("Server error during summarization.", true);
            }
        } catch (error) {
            showNotification("Network error occurred.", true);
        }
    }

    // Notifications
    function showNotification(message, isError = false) {
        const notif = document.getElementById("notification");
        notif.textContent = message;
        if (isError) notif.classList.add("error");
        else notif.classList.remove("error");
        
        notif.classList.add("show");
        setTimeout(() => notif.classList.remove("show"), 5000);
    }
});