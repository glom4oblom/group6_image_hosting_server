document.addEventListener('DOMContentLoaded', () => {
    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadTab = document.getElementById('upload-tab-btn');
    const imagesTab = document.getElementById('images-tab-btn');

    let currentPage = 1;

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

    const fetchImages = async (page = 1) => {
        const response = await fetch(`/api/images?page=${page}`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to load images');
        }

        return result;
    };

    const deleteImage = async (imageId) => {
    const response = await fetch(`/delete/${imageId}`, {
        method: 'DELETE'
    });

    const rawText = await response.text();
    let result = {};

    if (rawText) {
        try {
            result = JSON.parse(rawText);
        } catch (e) {
            throw new Error(`Server returned non-JSON response: ${rawText}`);
        }
    }

    if (!response.ok) {
        throw new Error(result.error || `Delete failed with status ${response.status}`);
    }

    return result;
};

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach((button) => {
    button.addEventListener('click', async (event) => {
        const imageId = event.currentTarget.dataset.id;
        await deleteImage(imageId);
        await displayFiles(currentPage);
    });
});
    };

    const renderPagination = (pagination) => {
        if (!pagination || pagination.total_pages <= 1) {
            return '';
        }

        return `
            <div class="pagination" style="display:flex; gap:12px; justify-content:center; margin-top:24px;">
                <button id="prev-page-btn" ${pagination.has_prev ? '' : 'disabled'}>
                    Previous page
                </button>
                <span>Page ${pagination.page} of ${pagination.total_pages}</span>
                <button id="next-page-btn" ${pagination.has_next ? '' : 'disabled'}>
                    Next page
                </button>
            </div>
        `;
    };

    const bindPagination = (pagination) => {
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', async () => {
                if (pagination.has_prev) {
                    currentPage -= 1;
                    await displayFiles(currentPage);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', async () => {
                if (pagination.has_next) {
                    currentPage += 1;
                    await displayFiles(currentPage);
                }
            });
        }
    };

    const displayFiles = async (page = 1) => {
        if (!fileListWrapper) return;

        try {
            const result = await fetchImages(page);
            const storedFiles = result.images || [];
            const pagination = result.pagination || null;

            currentPage = pagination?.page || page;
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
                <div class="file-col file-col-preview">Preview</div>
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-original">Original name</div>
                <div class="file-col file-col-size">Size (KB)</div>
                <div class="file-col file-col-date">Upload time</div>
                <div class="file-col file-col-type">Type</div>
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
                    <div class="file-col file-col-preview">
                        <img src="${fileData.relative_url}" alt="${fileData.display_name}" class="image-preview">
                    </div>
                    <div class="file-col file-col-name">
                        <a href="${fileData.relative_url}" target="_blank">${fileData.display_name}</a>
                    </div>
                    <div class="file-col file-col-original">${fileData.original_name}</div>
                    <div class="file-col file-col-size">${fileData.size_kb}</div>
                    <div class="file-col file-col-date">${fileData.upload_time}</div>
                    <div class="file-col file-col-type">${fileData.file_type}</div>
                    <div class="file-col file-col-url">
                        <a href="${fileData.relative_url}" target="_blank">${fileData.url}</a>
                    </div>
                    <div class="file-col file-col-delete">
                        <button class="delete-btn" data-id="${fileData.id}">
                            <img src="/static/img/delete.png" alt="Delete" class="delete-icon">
                        </button>
                    </div>
                `;
                list.appendChild(fileItem);
            });

            container.appendChild(list);

            const paginationWrapper = document.createElement('div');
            paginationWrapper.innerHTML = renderPagination(pagination);
            container.appendChild(paginationWrapper);

            fileListWrapper.appendChild(container);

            addDeleteListeners();
            bindPagination(pagination);
            updateTabStyles();
        } catch (error) {
            fileListWrapper.innerHTML = `
                <p style="text-align:center; margin-top:50px; color:red;">
                    ${error.message}
                </p>
            `;
        }
    };

    displayFiles(currentPage);
});