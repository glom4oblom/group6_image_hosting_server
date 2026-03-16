document.addEventListener('DOMContentLoaded', () => {
    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadTab = document.getElementById('upload-tab-btn');
    const imagesTab = document.getElementById('images-tab-btn');

    const updateTabStyles = () => {
        if (!uploadTab || !imagesTab) return;

        const isImagesPage = window.location.pathname === '/images-list';

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    const fetchImages = async () => {
        const response = await fetch('/api/images');
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to load images');
        }

        return result.images || [];
    };

    const deleteImage = async (filename) => {
        const response = await fetch('/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to delete image');
        }

        return result;
    };

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                const filename = event.currentTarget.dataset.filename;

                if (!filename) {
                    alert('Filename not found');
                    return;
                }

                try {
                    await deleteImage(filename);
                    await displayFiles();
                } catch (error) {
                    alert(error.message);
                }
            });
        });
    };

    const displayFiles = async () => {
        if (!fileListWrapper) return;

        try {
            const storedFiles = await fetchImages();
            fileListWrapper.innerHTML = '';

            if (storedFiles.length === 0) {
                fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
                updateTabStyles();
                return;
            }

            const container = document.createElement('div');
            container.className = 'file-list-container';

            const header = document.createElement('div');
            header.className = 'file-list-header';
            header.innerHTML = `
                <div class="file-col file-col-icon"></div>
                <div class="file-col file-col-preview"></div>
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-url">Url</div>
                <div class="file-col file-col-delete">Delete</div>
            `;
            container.appendChild(header);

            const list = document.createElement('div');
            list.id = 'file-list';

            storedFiles.forEach((fileData) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                    <div class="file-col file-col-icon">
                        <img src="/static/img/Group.png" alt="Icon" class="list-icon">
                    </div>
                    <div class="file-col file-col-preview">
                        <img src="${fileData.relative_url}" alt="${fileData.display_name}" class="image-preview">
                    </div>
                    <div class="file-col file-col-name">${fileData.display_name}</div>
                    <div class="file-col file-col-url">${fileData.url}</div>
                    <div class="file-col file-col-delete">
                        <button class="delete-btn" data-filename="${fileData.filename}">
                            <img src="/static/img/delete.png" alt="Delete" class="delete-icon">
                        </button>
                    </div>
                `;
                list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);

            addDeleteListeners();
            updateTabStyles();
        } catch (error) {
            fileListWrapper.innerHTML = `<p style="text-align:center; margin-top:50px; color:red;">${error.message}</p>`;
        }
    };

    if (uploadTab) {
        uploadTab.addEventListener('click', () => {
            window.location.href = '/upload';
        });
    }

    if (imagesTab) {
        imagesTab.addEventListener('click', () => {
            window.location.href = '/images-list';
        });
    }

    displayFiles();
});