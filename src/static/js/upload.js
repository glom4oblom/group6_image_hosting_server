document.addEventListener('DOMContentLoaded', function () {
    const uploadTab = document.getElementById('upload-tab-btn');
    const imagesTab = document.getElementById('images-tab-btn');
    const fileInput = document.querySelector('#file-upload');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');
    const statusMessage = document.querySelector('.upload-status');

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    const maxSizeBytes = 5 * 1024 * 1024;

    const LOCAL_STORAGE_KEY = 'uploaded_images';

const getStoredImages = () => {
    try {
        return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY)) || [];
    } catch (error) {
        return [];
    }
};

const saveStoredImages = (images) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(images));
};

const addImageToLocalStorage = (imageData) => {
    const images = getStoredImages();

    const normalizedImage = {
        name: imageData.filename || imageData.name,
        relative_url: imageData.relative_url,
        url: imageData.url
    };

    const exists = images.some((img) => img.name === normalizedImage.name);

    if (!exists) {
        images.push(normalizedImage);
        saveStoredImages(images);
    }
};

    const updateTabStyles = () => {
        if (!uploadTab || !imagesTab) return;

        const isUploadPage = window.location.pathname === '/upload';
        const isImagesPage = window.location.pathname === '/images-list';

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else if (isUploadPage) {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    const showMessage = (message, isError = false) => {
        if (!statusMessage) {
            alert(message);
            return;
        }

        statusMessage.textContent = message;
        statusMessage.style.color = isError ? 'red' : 'green';
    };

    const uploadFileToServer = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Upload failed');
        }

        return result;
    };

    const handleAndStoreFiles = async (files) => {
        if (!files || files.length === 0) return;

        for (const file of files) {
            if (!allowedTypes.includes(file.type)) {
                showMessage('Unsupported file format. Only JPG, PNG and GIF are allowed.', true);
                continue;
            }

            if (file.size > maxSizeBytes) {
                showMessage('File too large. Maximum file size is 5 MB.', true);
                continue;
            }

            try {
                showMessage('Uploading...');

                const result = await uploadFileToServer(file);

                if (result.success) {
            if (currentUploadInput) {
                currentUploadInput.value = result.url;
            }

            addImageToLocalStorage(result);

            showMessage(result.message || 'File uploaded successfully');
        } else {
            showMessage(result.error || 'Upload failed', true);
        }
            } catch (error) {
                console.error('UPLOAD FRONT ERROR:', error);
                showMessage(error.message || 'Server error while uploading file.', true);
            }
        }
    };

    if (fileInput) {
        fileInput.addEventListener('change', async (event) => {
            await handleAndStoreFiles(event.target.files);
            event.target.value = '';
        });
    }

    if (dropzone) {
        dropzone.addEventListener('dragover', (event) => {
            event.preventDefault();
        });

        dropzone.addEventListener('drop', async (event) => {
            event.preventDefault();
            await handleAndStoreFiles(event.dataTransfer.files);
        });
    }

    if (copyButton && currentUploadInput) {
        copyButton.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(currentUploadInput.value);
                showMessage('Link copied successfully');
            } catch (error) {
                showMessage('Failed to copy link', true);
            }
        });
    }


    updateTabStyles();
});