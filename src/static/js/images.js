const fileListWrapper = document.getElementById('file-list-wrapper');
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

const removeImageFromLocalStorage = (filename) => {
    const images = getStoredImages().filter((img) => img.name !== filename);
    saveStoredImages(images);
};

const fetchImages = async () => {
    const localImages = getStoredImages();

    if (localImages.length > 0) {
        return localImages;
    }

    const response = await fetch('/api/images');
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || 'Failed to load images');
    }

    const images = result.images || [];
    saveStoredImages(images);

    return images;
};

const deleteImage = async (filename) => {
    const response = await fetch('/delete-image', {
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

const updateTabStyles = () => {
    const uploadLink = document.querySelector('.upload');
    const imagesLink = document.querySelector('.images');

    if (uploadLink) uploadLink.classList.remove('active');
    if (imagesLink) imagesLink.classList.add('active');
};

const addDeleteListeners = () => {
    document.querySelectorAll('.delete-btn').forEach((button) => {
        button.addEventListener('click', async (event) => {
            const filename = event.currentTarget.dataset.filename;

            try {
                await deleteImage(filename);
                removeImageFromLocalStorage(filename);
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
            fileListWrapper.innerHTML = `
                <p class="upload__promt" style="text-align: center; margin-top: 50px;">
                    No images uploaded yet.
                </p>
            `;
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
                    <img src="${fileData.relative_url}" alt="${fileData.name}" class="image-preview">
                </div>
                <div class="file-col file-col-name">${fileData.name}</div>
                <div class="file-col file-col-url">${fileData.url}</div>
                <div class="file-col file-col-delete">
                    <button class="delete-btn" data-filename="${fileData.name}">
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
        fileListWrapper.innerHTML = `
            <p style="text-align:center; margin-top:50px; color:red;">
                ${error.message}
            </p>
        `;
    }
};

document.addEventListener('DOMContentLoaded', displayFiles);