document.addEventListener('DOMContentLoaded', function() {
    // 獲取所有必要的元素
    const selectedCategoriesContainer = document.getElementById('selected-categories');
    const availableCategoriesContainer = document.getElementById('available-categories');
    const newCategoryInput = document.getElementById('new-category-input');
    const addCategoryBtn = document.getElementById('add-category-btn');
    const selectedCategoriesHiddenInput = document.getElementById('selected-categories-hidden');

    const selectedTagsContainer = document.getElementById('selected-tags');
    const availableTagsContainer = document.getElementById('available-tags');
    const newTagInput = document.getElementById('new-tag-input');
    const addTagBtn = document.getElementById('add-tag-btn');
    const selectedTagsHiddenInput = document.getElementById('selected-tags-hidden');

    // 初始化選擇狀態
    initializeSelections();

    // 點擊「所有題材/標籤」區域中的選項 - 切換選擇狀態
    if (availableCategoriesContainer) {
        availableCategoriesContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('category-option')) {
                toggleSelection(event.target, 'category');
            }
        });
    }

    if (availableTagsContainer) {
        availableTagsContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('tag-option')) {
                toggleSelection(event.target, 'tag');
            }
        });
    }

    // 點擊「已選擇的題材/標籤」區域中的選項 - 取消選擇
    if (selectedCategoriesContainer) {
        selectedCategoriesContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('category-option')) {
                // 找到對應的「所有題材」區域中的選項
                const availableOption = availableCategoriesContainer.querySelector(`.category-option[data-id="${event.target.dataset.id}"]`);
                if (availableOption) {
                    toggleSelection(availableOption, 'category');
                }
            }
        });
    }

    if (selectedTagsContainer) {
        selectedTagsContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('tag-option')) {
                // 找到對應的「所有標籤」區域中的選項
                const availableOption = availableTagsContainer.querySelector(`.tag-option[data-id="${event.target.dataset.id}"]`);
                if (availableOption) {
                    toggleSelection(availableOption, 'tag');
                }
            }
        });
    }

    // 新增題材
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', function() {
            addNewOption('category');
        });
    }

    // 新增標籤
    if (addTagBtn) {
        addTagBtn.addEventListener('click', function() {
            addNewOption('tag');
        });
    }

    // 初始化選擇狀態
    function initializeSelections() {
        // 根據初始選擇狀態更新「已選擇的題材/標籤」區域
        updateSelectedContainers();
        // 更新隱藏輸入欄位
        updateHiddenInputs();
    }

    // 切換選擇狀態
    function toggleSelection(optionElement, type) {
        // 切換選擇狀態
        optionElement.classList.toggle('selected');
        
        // 更新「已選擇的題材/標籤」區域
        updateSelectedContainers();
        
        // 更新隱藏輸入欄位
        updateHiddenInputs();
    }

    // 更新「已選擇的題材/標籤」區域
    function updateSelectedContainers() {
        // 清空「已選擇的題材/標籤」區域
        if (selectedCategoriesContainer) {
            selectedCategoriesContainer.innerHTML = '';
            
            // 找出所有被選擇的題材
            const selectedCategories = availableCategoriesContainer.querySelectorAll('.category-option.selected');
            
            // 複製到「已選擇的題材」區域
            selectedCategories.forEach(category => {
                const clone = category.cloneNode(true);
                selectedCategoriesContainer.appendChild(clone);
            });
        }
        
        if (selectedTagsContainer) {
            selectedTagsContainer.innerHTML = '';
            
            // 找出所有被選擇的標籤
            const selectedTags = availableTagsContainer.querySelectorAll('.tag-option.selected');
            
            // 複製到「已選擇的標籤」區域
            selectedTags.forEach(tag => {
                const clone = tag.cloneNode(true);
                selectedTagsContainer.appendChild(clone);
            });
        }
    }

    // 更新隱藏輸入欄位
    function updateHiddenInputs() {
        if (availableCategoriesContainer && selectedCategoriesHiddenInput) {
            const selectedCategories = availableCategoriesContainer.querySelectorAll('.category-option.selected');
            const selectedCategoryNames = Array.from(selectedCategories).map(category => category.dataset.name);
            selectedCategoriesHiddenInput.value = selectedCategoryNames.join(',');
        }
        
        if (availableTagsContainer && selectedTagsHiddenInput) {
            const selectedTags = availableTagsContainer.querySelectorAll('.tag-option.selected');
            const selectedTagNames = Array.from(selectedTags).map(tag => tag.dataset.name);
            selectedTagsHiddenInput.value = selectedTagNames.join(',');
        }
    }

    // 新增選項
    function addNewOption(type) {
        const inputElement = type === 'category' ? newCategoryInput : newTagInput;
        const container = type === 'category' ? availableCategoriesContainer : availableTagsContainer;
        const value = inputElement.value.trim();
        // 使用全局變數獲取 URL
        const addUrl = type === 'category' ? addCategoryUrl : addTagUrl;
        
        if (!value) return;
        
        // 檢查是否已存在
        const existingOption = container.querySelector(`[data-name="${value}"]`);
            
        if (existingOption) {
            // 如果已存在但未選擇，則選擇它
            if (!existingOption.classList.contains('selected')) {
                toggleSelection(existingOption, type);
                alert(`${type === 'category' ? '題材' : '標籤'} "${value}" 已存在，已自動為您選擇！`);
            } else {
                alert(`${type === 'category' ? '題材' : '標籤'} "${value}" 已存在且已被選擇！`);
            }
            inputElement.value = '';
            return;
        }
        
        // 如果不存在，發送 AJAX 請求到後端新增
        fetch(addUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `name=${encodeURIComponent(value)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 後端成功處理，創建新選項或選取現有選項
                const newOption = document.createElement('span');
                newOption.classList.add(type === 'category' ? 'category-option' : 'tag-option');
                newOption.classList.add('selected'); // 新增的選項預設為已選擇
                newOption.dataset.name = data.name; // 使用後端返回的名稱
                newOption.dataset.id = data.id; // 使用後端返回的 ID
                newOption.dataset.type = type;
                newOption.textContent = data.name; // 使用後端返回的名稱
                
                // 添加到「所有題材/標籤」區域
                container.appendChild(newOption);
                
                // 更新「已選擇的題材/標籤」區域
                updateSelectedContainers();
                
                // 更新隱藏輸入欄位
                updateHiddenInputs();

                // 顯示後端返回的訊息
                alert(data.message);

            } else {
                // 後端處理失敗
                alert(`新增失敗: ${data.message}`);
            }
        })
        .catch(error => {
            // 網絡或請求錯誤
            console.error('Error:', error);
            alert(`新增過程中發生錯誤: ${error}`);
        })
        .finally(() => {
            // 無論成功或失敗，清空輸入欄位
            inputElement.value = '';
        });
    }
}); 