// This file will contain the JavaScript for the add book page.
// It will handle the selection of categories and tags.

document.addEventListener('DOMContentLoaded', function() {
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

    // Function to render an option (category or tag)
    function renderOption(item, container, type, isSelected = false) {
        const optionElement = document.createElement('span');
        optionElement.classList.add(`${type}-option`);
        if (isSelected) {
            optionElement.classList.add('selected');
        }
        optionElement.textContent = item.name;
        optionElement.dataset.id = item.id; // Store the ID
        optionElement.dataset.name = item.name; // Store the name
        optionElement.dataset.type = type; // 'category' or 'tag'

        container.appendChild(optionElement);
    }

    // Function to update the hidden input field with selected items
    function updateHiddenInput(type) {
        const selectedItems = [];
        const container = type === 'category' ? selectedCategoriesContainer : selectedTagsContainer;
        container.querySelectorAll(`.${type}-option`).forEach(option => {
            selectedItems.push(option.dataset.name); // Use name for submission
        });
        const hiddenInput = type === 'category' ? selectedCategoriesHiddenInput : selectedTagsHiddenInput;
        hiddenInput.value = selectedItems.join(','); // Join with comma for backend
    }

    // Event delegation for clicking on options
    document.body.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('category-option') || target.classList.contains('tag-option')) {
            const itemType = target.dataset.type;
            const itemId = target.dataset.id;
            const itemName = target.dataset.name;

            if (target.classList.contains('selected')) {
                // Deselecting an item
                target.classList.remove('selected');
                // Move to available list
                const availableContainer = itemType === 'category' ? availableCategoriesContainer : availableTagsContainer;
                renderOption({ id: itemId, name: itemName }, availableContainer, itemType, false);
                target.remove();
            } else {
                // Selecting an item
                target.classList.add('selected');
                // Move to selected list
                const selectedContainer = itemType === 'category' ? selectedCategoriesContainer : selectedTagsContainer;
                renderOption({ id: itemId, name: itemName }, selectedContainer, itemType, true);
                target.remove();
            }
            updateHiddenInput(itemType); // Update hidden input after change
        }
    });

    // Function to load initial categories and tags
    function loadInitialData(categories, tags) {
        // Render available categories
        categories.forEach(category => {
            renderOption(category, availableCategoriesContainer, 'category', false);
        });

        // Render available tags
        tags.forEach(tag => {
            renderOption(tag, availableTagsContainer, 'tag', false);
        });

        // Initially update hidden inputs (in case of editing an existing book later)
        updateHiddenInput('category');
        updateHiddenInput('tag');
    }

    // Use the data embedded from the backend
    loadInitialData(initialCategories, initialTags);

    // Handle adding new category
    addCategoryBtn.addEventListener('click', function() {
        const newItemName = newCategoryInput.value.trim();
        if (newItemName) {
            // TODO: Send request to backend to add new category
            // For now, just add to available list with a temporary ID
            renderOption({ id: Date.now(), name: newItemName }, availableCategoriesContainer, 'category', false);
            newCategoryInput.value = ''; // Clear input
        }
    });

     // Handle adding new tag
     addTagBtn.addEventListener('click', function() {
        const newItemName = newTagInput.value.trim();
        if (newItemName) {
            // TODO: Send request to backend to add new tag
            // For now, just add to available list with a temporary ID
            renderOption({ id: Date.now(), name: newItemName }, availableTagsContainer, 'tag', false);
            newTagInput.value = ''; // Clear input
        }
    });

    // TODO: Ensure form submission correctly uses the hidden inputs
}); 