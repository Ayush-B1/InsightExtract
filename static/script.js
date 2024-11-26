function summarizeText() {
    const text = document.getElementById("text-input").value;

    if (text) {
        fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            if (data.summary) {
                document.getElementById("result-text").innerText = data.summary;
                document.getElementById("download-button").style.display = 'block';
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function summarizeFromURL() {
    const url = document.getElementById("url-input").value;

    if (url) {
        fetch('/summarize_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            if (data.summary) {
                document.getElementById("result-text").innerText = data.summary;
                document.getElementById("download-button").style.display = 'block';
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function uploadPDF() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (file) {
        let formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.summary) {
                document.getElementById("result-text").innerText = data.summary;
                document.getElementById("download-button").style.display = 'block';
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function downloadSummary() {
    const summary = document.getElementById("result-text").innerText;

    fetch('/download_summary', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ summary: summary })
    })
    .then(response => response.blob())
    .then(blob => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'summary.pdf';
        link.click();
    })
    .catch(error => console.error('Error:', error));
}
