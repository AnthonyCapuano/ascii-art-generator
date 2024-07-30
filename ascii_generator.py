<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stable ASCII Art Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        #resultContainer {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
            overflow-x: auto;
        }
        #result {
            font-family: monospace;
            white-space: pre;
            font-size: 5px;
            line-height: 5px;
            text-align: left;
        }
        button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Stable ASCII Art Generator</h1>
    <input type="file" id="imageInput" accept="image/*">
    <button id="captureButton">Take Picture</button>
    <div id="resultContainer">
        <pre id="result"></pre>
    </div>
    <div>
        <button id="copyButton">Copy to Clipboard</button>
        <button id="shareButton">Share</button>
    </div>
    <script>
        const imageInput = document.getElementById('imageInput');
        const captureButton = document.getElementById('captureButton');
        const result = document.getElementById('result');
        const copyButton = document.getElementById('copyButton');
        const shareButton = document.getElementById('shareButton');

        imageInput.addEventListener('change', handleImage);
        captureButton.addEventListener('click', capturePicture);
        copyButton.addEventListener('click', copyToClipboard);
        shareButton.addEventListener('click', shareAsciiArt);

        function handleImage(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    processImage(event.target.result);
                };
                reader.onerror = function() {
                    showError("Error reading file. Please try again.");
                };
                reader.readAsDataURL(file);
            }
        }

        function capturePicture() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                showError("Camera access is not supported in your browser. Please try uploading an image instead.");
                return;
            }

            navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
                .then(stream => {
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    video.onloadedmetadata = () => {
                        video.play();
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        canvas.getContext('2d').drawImage(video, 0, 0);
                        stream.getTracks().forEach(track => track.stop());
                        processImage(canvas.toDataURL('image/jpeg'));
                    };
                })
                .catch(error => {
                    console.error('Error accessing camera:', error);
                    showError("Error accessing camera. Please try uploading an image instead.");
                });
        }

        function processImage(dataUrl) {
            const img = new Image();
            img.onload = function() {
                try {
                    const ascii = convertToAscii(img);
                    result.textContent = ascii;
                } catch (error) {
                    showError("Error generating ASCII art. Please try again.");
                }
            };
            img.onerror = function() {
                showError("Error loading image. Please try again.");
            };
            img.src = dataUrl;
        }

        function convertToAscii(img) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const asciiChars = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.'];

            const maxWidth = 80;
            const maxHeight = 80;
            let width = img.width;
            let height = img.height;

            if (width > height) {
                if (width > maxWidth) {
                    height *= maxWidth / width;
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width *= maxHeight / height;
                    height = maxHeight;
                }
            }

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);

            const imageData = ctx.getImageData(0, 0, width, height);
            let ascii = '';

            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const offset = (y * width + x) * 4;
                    const r = imageData.data[offset];
                    const g = imageData.data[offset + 1];
                    const b = imageData.data[offset + 2];
                    const brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    const charIndex = Math.floor(brightness * (asciiChars.length - 1));
                    ascii += asciiChars[charIndex];
                }
                ascii += '\n';
            }

            return ascii;
        }

        function copyToClipboard() {
            const asciiArt = result.textContent;
            if (asciiArt && !asciiArt.startsWith('Error')) {
                navigator.clipboard.writeText(asciiArt).then(() => {
                    alert('ASCII art copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy. Please try again.');
                });
            } else {
                alert('No valid ASCII art to copy.');
            }
        }

        function shareAsciiArt() {
            const asciiArt = result.textContent;
            if (asciiArt && !asciiArt.startsWith('Error')) {
                if (navigator.share) {
                    navigator.share({
                        title: 'ASCII Art',
                        text: asciiArt,
                    }).then(() => {
                        console.log('Successfully shared');
                    }).catch((error) => {
                        console.error('Error sharing:', error);
                        fallbackShare(asciiArt);
                    });
                } else {
                    fallbackShare(asciiArt);
                }
            } else {
                alert('No valid ASCII art to share.');
            }
        }

        function fallbackShare(asciiArt) {
            const textArea = document.createElement('textarea');
            textArea.value = asciiArt;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('ASCII art copied to clipboard! You can now paste it into your message app.');
        }

        function showError(message) {
            result.textContent = message;
            console.error(message);
        }

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    </script>
</body>
</html>
