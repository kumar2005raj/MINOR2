document.addEventListener('DOMContentLoaded', () => {
    const audioFileElement = document.getElementById('audioFile');
    const uploadButton = document.getElementById('uploadButton');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const summaryTextElement = document.getElementById('summaryText');
    const transcriptionTextElement = document.getElementById('transcriptionText');

    uploadButton.addEventListener('click', async () => {
        const file = audioFileElement.files[0];
        if (!file) {
            alert('Please select an audio file.');
            return;
        }

        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('audio_file', file);

        try {
            const response = await fetch('/summarize', {
                method: 'POST',
                body: formData,
            });
   if (response.ok) {
                const data = await response.json();
                summaryTextElement.textContent = data.summary || 'No summary available.';
                transcriptionTextElement.textContent = data.transcription || 'No transcription available.';
                resultDiv.style.display = 'block';
            } else {
                alert('Error processing the audio file.');
                console.error('Server error:', response.status);
            }
        } catch (error) {
            alert('Network error occurred.');
            console.error('Fetch error:', error);
        } finally {
            loadingDiv.style.display = 'none';
        }
    });
});