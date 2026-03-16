document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' || event.key === 'F5') {
            event.preventDefault();
            sessionStorage.removeItem('pageWasVisited');
            window.location.href = '/';
        }
    });

    const fileUpload = document.getElementById('file-upload');
    const imagesButton = document.getElementById('images-tab-btn');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');
        const isImagesPage = window.location.pathname.includes('/images.html');

        if (!uploadTab || !imagesTab) return;

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    const handleAndStoreFiles = (files) => {
        if (!files || files.length === 0) return;

        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxSizeBytes = 5 * 1024 * 1024;
        let lastFileName = '';

        for (const file of files) {
            if (!allowedTypes.includes(file.type) || file.size > maxSizeBytes) {
                continue;
            }

            const reader = new FileReader();
            reader.onload = (event) => {
                storedFiles.push({
                    name: file.name,
                    url: event.target.result
                });
                localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                updateTabStyles();
            };
            reader.readAsDataURL(file);

            lastFileName = file.name;
        }

        if (lastFileName && currentUploadInput) {
            currentUploadInput.value = `https://sharefile.xyz/${lastFileName}`;
        }
    };

    if (copyButton && currentUploadInput) {
        copyButton.addEventListener('click', () => {
            const textToCopy = currentUploadInput.value;

            if (textToCopy && textToCopy !== 'https://') {
                navigator.clipboard.writeText(textToCopy)
                    .then(() => {
                        copyButton.textContent = 'COPIED!';
                        setTimeout(() => {
                            copyButton.textContent = 'COPY';
                        }, 2000);
                    })
                    .catch((err) => {
                        console.error('Failed to copy text:', err);
                    });
            }
        });
    }

    if (imagesButton) {
        imagesButton.addEventListener('click', () => {
            window.location.href = '/images-list';
        });
    }

    if (fileUpload) {
        fileUpload.addEventListener('change', (event) => {
            handleAndStoreFiles(event.target.files);
            event.target.value = '';
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropzone.addEventListener('drop', (event) => {
            handleAndStoreFiles(event.dataTransfer.files);
        });
    }

    updateTabStyles();
});