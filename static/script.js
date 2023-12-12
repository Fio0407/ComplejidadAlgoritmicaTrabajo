document.addEventListener("DOMContentLoaded", function () {
    // Add an event listener to the "Buscar Dataset" button.
    const fileInput = document.getElementById("fileInput");

    // Listen for changes in the file input element
    fileInput.addEventListener("change", function () {
        const selectedFile = fileInput.files[0];
        if (selectedFile) {
            // Assuming you want to overwrite the file only if it's a text file
            if (selectedFile.type === "text/plain") {
                const formData = new FormData();
                formData.append("file", selectedFile);

                // Use fetch to send the file to the server
                fetch("/generate_graph", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("File uploaded successfully. Graph generated.");
                    } else {
                        alert("Error uploading file: " + data.message);
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                });
            } else {
                alert("Invalid file format. Please select a .txt file.");
            }
        }
    });
});
